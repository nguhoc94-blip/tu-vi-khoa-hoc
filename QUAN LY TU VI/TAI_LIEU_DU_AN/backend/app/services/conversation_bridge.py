"""
Conversation bridge — main orchestrator for the conversational MVP.

Flow per incoming message:
  1. Load session (birth_data, history, chart_json)
  2. Run birth_extractor → merge any extracted fields into birth_data
  3. Mode router (hard logic, NOT prompt-based):
       HAS_CHART   → OpenAI follow-up with chart context
       GENERATE    → all required birth fields present → generate chart + reading
       INTAKE      → partial birth_data present → ask for first missing field
       CHAT        → no birth data at all → OpenAI general tử vi chat
  4. Add user/assistant turns to history; trim to MAX_HISTORY
  5. Save session; return reply string

Mode router rules (locked per plan):
  - INTAKE only activates when birth_data is non-empty OR extractor returned ≥1 field.
  - When extractor returns {} AND birth_data is empty → CHAT mode (never force intake).
  - Follow-up (HAS_CHART) takes priority over everything else once chart exists.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

import psycopg
from openai import OpenAI

from app.db import DatabaseUnavailableError
from app.schemas.reading import GenerateReadingRequest
from app.services.app_config_store import get_config_text, get_config_text_first
from app.services.birth_extractor import extract_birth_fields
from app.services.final_message_builder import build_messenger_outbound
from app.services.flow_routing import (
    FLOW_PAID_REPEAT,
    FLOW_RETURNING_UNPAID,
    apply_referral_ref_to_routing,
    resolve_active_flow,
)
from app.services.messenger_state import (
    FIELD_QUESTION,
    ConversationState,
    MessengerSession,
)
from app.services.messenger_state_db import DbMessengerStateStore
from app.services.kb2_confirmation import (
    build_confirmation_summary_message,
    is_kb2_confirm_text,
    is_kb2_edit_text,
    kb2_reminder_when_awaiting,
)
from app.services.messenger_funnel_bridge import (
    on_birthdata_confirmation_requested,
    on_birthdata_confirmed,
    on_reading_created,
    record_funnel_event,
)
from app.services.payload_handler import append_cta_after_free_hint
from app.services.openai_paid import generate_full_reading_direct
from app.services.reading_service import process_generate_reading
from app.services.reading_store_db import ReadingStoreDb
from app.services.user_profile_flags import get_profile_metadata, paid_once_from_metadata

logger = logging.getLogger(__name__)

_store = DbMessengerStateStore()
_reading_store = ReadingStoreDb()

_CONVERSATION_MODEL_DEFAULT = "gpt-4o-mini"
_CONVERSATION_TIMEOUT = 60.0
_HISTORY_CONTEXT_TURNS = 6  # how many turns to send to OpenAI (≤ MAX_HISTORY)

DEFAULT_DONATION_TEXT = "Nếu thấy hữu ích, bạn có thể ủng hộ để dự án duy trì."

_THIRD_PARTY_HINT = re.compile(
    r"(cho\s+(mẹ|me|má|ba|bố|bo|bà|ông|anh|chị|chi|em|bạn)\b|"
    r"hộ\s+|thay\s+mặt|người\s+khác|bạn\s+tôi|mẹ\s+tôi|bố\s+tôi|chồng|vợ(\s+tôi)?)",
    re.I,
)


def _third_party_hint(text: str) -> bool:
    return bool(_THIRD_PARTY_HINT.search(text or ""))


def _maybe_profile_clarification(
    session: MessengerSession,
    text: str,
    flow: str,
    *,
    sender_id: str,
    request_id: str,
) -> str | None:
    """Lát 4 — một lần clarification khi returning/paid_repeat + tín hiệu hộ người khác."""
    if flow not in (FLOW_RETURNING_UNPAID, FLOW_PAID_REPEAT):
        return None
    r = session.routing if isinstance(session.routing, dict) else {}
    if r.get("profile_clarification_shown"):
        return None
    if not _third_party_hint(text):
        return None
    r["profile_clarification_shown"] = True
    session.routing = r
    record_funnel_event(
        sender_id=sender_id,
        event_type="profile_switch_clarification_shown",
        request_id=request_id,
        payload={"flow": flow},
    )
    msg = get_config_text_first(
        "confirmation_profile_switch_check",
        default=(
            "Mình đang hiểu là bạn đang hỏi giúp người khác, không phải hồ sơ hiện tại. "
            "Nếu đúng, cho mình biết để xử lý phù hợp nhé."
        ),
    )
    return msg.strip() or None


def _handle_kb2_path(
    session: MessengerSession,
    text: str,
    *,
    sender_id: str,
    request_id: str,
) -> str:
    """Lát 3 — chốt birth trước generate; bắt buộc funnel birthdata_* ."""
    r = session.routing if isinstance(session.routing, dict) else {}
    session.routing = r

    if r.get("kb2_awaiting_confirm"):
        if r.pop("kb2_payload_confirm", None) or is_kb2_confirm_text(text):
            on_birthdata_confirmed(sender_id=sender_id, request_id=request_id)
            r["kb2_awaiting_confirm"] = False
            safe = get_config_text_first("confirmation_pre_chart_safe_close", default="")
            gen_body = _mode_generate(session, sender_id=sender_id, request_id=request_id)
            return f"{safe}\n\n{gen_body}" if safe else gen_body
        if is_kb2_edit_text(text):
            r["kb2_awaiting_confirm"] = False
            r.pop("kb2_payload_edit", None)
            session.birth_data = {}
            return get_config_text_first(
                "confirmation_missing_field_retry",
                default="Không sao, bạn nhập lại giúp mình nhé.",
            )
        return kb2_reminder_when_awaiting(session)

    r["kb2_awaiting_confirm"] = True
    on_birthdata_confirmation_requested(sender_id=sender_id, request_id=request_id)
    return build_confirmation_summary_message(session)


def _load_prompt(name: str) -> str:
    path = Path(__file__).resolve().parents[2] / "prompts" / name
    return path.read_text(encoding="utf-8")


def _build_donation_cta() -> str:
    donation_text = (os.environ.get("DONATION_TEXT") or "").strip()
    donation_url = (os.environ.get("DONATION_URL") or "").strip()
    if not donation_text and not donation_url:
        return ""
    if donation_url and not donation_text:
        donation_text = DEFAULT_DONATION_TEXT
    return f"{donation_text}\n{donation_url}" if donation_url else donation_text


def _chart_summary(chart_json: dict[str, Any]) -> str:
    """Build a concise text summary of the chart for the conversation prompt.

    We deliberately avoid sending the full chart JSON to reduce token cost.
    The summary includes menh, can_chi, and the first few houses.
    """
    lines: list[str] = []
    menh = chart_json.get("menh") or {}
    if menh:
        lines.append(f"Mệnh: {json.dumps(menh, ensure_ascii=False)}")
    can_chi = chart_json.get("can_chi") or {}
    if can_chi:
        lines.append(f"Can Chi: {json.dumps(can_chi, ensure_ascii=False)}")
    houses = chart_json.get("houses") or []
    if houses:
        lines.append(f"12 cung: {json.dumps(houses[:12], ensure_ascii=False)}")
    return "\n".join(lines) if lines else "(chart data available)"


def _call_openai_conversation(
    *,
    system_prompt: str,
    history: list[dict[str, str]],
    user_message: str,
    request_id: str,
) -> str:
    """Call OpenAI for a conversational response. Returns fallback string on any error."""
    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        logger.warning(
            "conversation_openai_skip request_id=%s event=conv_skip reason=missing_api_key",
            request_id,
        )
        return "Hiện mình chưa kết nối được với AI. Vui lòng thử lại sau."

    model = (
        (os.environ.get("OPENAI_MODEL") or "").strip() or _CONVERSATION_MODEL_DEFAULT
    )

    recent_history = history[-_HISTORY_CONTEXT_TURNS:] if history else []
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    messages.extend(recent_history)
    messages.append({"role": "user", "content": user_message})

    try:
        client = OpenAI(api_key=api_key, timeout=_CONVERSATION_TIMEOUT)
        completion = client.chat.completions.create(
            model=model,
            messages=messages,  # type: ignore[arg-type]
        )
        text = (completion.choices[0].message.content or "").strip()
        if not text:
            return "Mình chưa có câu trả lời phù hợp. Bạn thử hỏi lại nhé."
        logger.info(
            "conversation_openai_ok request_id=%s event=conv_ok model=%s",
            request_id,
            model,
        )
        return text
    except Exception as e:
        logger.warning(
            "conversation_openai_failed request_id=%s event=conv_failed reason=%s",
            request_id,
            type(e).__name__,
        )
        return "Mình đang gặp sự cố kết nối AI. Bạn thử lại sau nhé."


def _parse_targeted_fields(first_missing: str, text: str) -> dict[str, Any]:
    """Parse a short reply when the bot explicitly asked for `first_missing`.

    Avoids infinite INTAKE loops when OpenAI birth_extractor returns {} for
    messages like "16", "16h", "16h30p" — the model has no field context.

    Returns a dict of field(s) to merge into birth_data, or {} if no match.
    """
    t = text.strip()
    if not t:
        return {}
    lo = t.lower()

    if first_missing == "full_name":
        # Do not treat short digit-only input as a name (e.g. hour "16").
        if re.fullmatch(r"\d{1,4}", t):
            return {}
        return {"full_name": t}

    if first_missing == "birth_day":
        m = re.match(r"^(\d{1,2})\s*$", t)
        if m:
            v = int(m.group(1))
            if 1 <= v <= 31:
                return {"birth_day": v}
        return {}

    if first_missing == "birth_month":
        m = re.match(r"^(\d{1,2})\s*$", t)
        if m:
            v = int(m.group(1))
            if 1 <= v <= 12:
                return {"birth_month": v}
        return {}

    if first_missing == "birth_year":
        m = re.match(r"^(\d{4})\s*$", t)
        if m:
            y = int(m.group(1))
            if 1900 <= y <= 2100:
                return {"birth_year": y}
        return {}

    if first_missing == "birth_hour":
        # 16h30p, 16:30, 16h30, 16 h 30
        m = re.match(r"^(\d{1,2})\s*[hH:]\s*(\d{1,2})\s*p?\s*$", t)
        if m:
            h, mi = int(m.group(1)), int(m.group(2))
            out: dict[str, Any] = {}
            if 0 <= h <= 23:
                out["birth_hour"] = h
            if 0 <= mi <= 59:
                out["birth_minute"] = mi
            return out
        m = re.match(r"^(\d{1,2})\s*h\s*$", t, re.I)
        if m:
            h = int(m.group(1))
            if 0 <= h <= 23:
                return {"birth_hour": h}
        m = re.match(r"^(\d{1,2})\s*$", t)
        if m:
            h = int(m.group(1))
            if 0 <= h <= 23:
                return {"birth_hour": h}
        return {}

    if first_missing == "birth_minute":
        m = re.match(r"^(\d{1,2})\s*p?\s*$", t, re.I)
        if m:
            mi = int(m.group(1))
            if 0 <= mi <= 59:
                return {"birth_minute": mi}
        return {}

    if first_missing == "gender":
        mapping = {
            "nam": "male",
            "male": "male",
            "nữ": "female",
            "nu": "female",
            "female": "female",
        }
        if lo in mapping:
            return {"gender": mapping[lo]}
        return {}

    if first_missing == "calendar_type":
        mapping = {
            "solar": "solar",
            "lunar": "lunar",
            "duong": "solar",
            "dương": "solar",
            "am": "lunar",
            "âm": "lunar",
        }
        if lo in mapping:
            return {"calendar_type": mapping[lo]}
        return {}

    if first_missing == "is_leap_lunar_month":
        if lo in ("có", "co", "yes", "true", "1"):
            return {"is_leap_lunar_month": True}
        if lo in ("không", "khong", "no", "false", "0"):
            return {"is_leap_lunar_month": False}
        return {}

    return {}


def _mode_chat(
    session: MessengerSession,
    user_message: str,
    *,
    request_id: str,
) -> str:
    """CHAT mode: general tử vi conversation (no birth data, no chart)."""
    system_prompt = _load_prompt("system_conversation.txt").replace(
        "{{CHART_CONTEXT}}",
        "Người dùng chưa cung cấp thông tin ngày sinh. "
        "Hãy trả lời các câu hỏi tổng quát về tử vi một cách tự nhiên. "
        "Nếu người dùng muốn xem lá số cá nhân, hỏi nhẹ nhàng họ tên và ngày sinh.",
    )
    return _call_openai_conversation(
        system_prompt=system_prompt,
        history=session.history,
        user_message=user_message,
        request_id=request_id,
    )


def _mode_intake(session: MessengerSession) -> str:
    """INTAKE mode: ask for the first missing birth field."""
    missing = session.missing_birth_fields()
    if not missing:
        return ""
    first_missing = missing[0]
    body = FIELD_QUESTION.get(first_missing, f"Bạn cho mình biết {first_missing} nhé?")
    rq = session.routing if isinstance(session.routing, dict) else {}
    if not rq.get("disclaimer_intake_shown"):
        disc = get_config_text("disclaimer_snippet_intake", "")
        if disc:
            body = f"{disc}\n\n{body}"
        rq["disclaimer_intake_shown"] = True
        session.routing = rq
    return body


def _mode_generate(
    session: MessengerSession,
    *,
    sender_id: str,
    request_id: str,
) -> str:
    """GENERATE mode: build chart + reading, then move session to HAS_CHART."""
    try:
        payload = GenerateReadingRequest(**session.birth_data)
    except Exception as e:
        logger.warning(
            "conversation_birth_invalid request_id=%s sender_id=%s error=%s event=birth_invalid",
            request_id,
            sender_id,
            repr(e),
        )
        # Birth data failed validation — ask for first missing/invalid field
        missing = session.missing_birth_fields()
        if missing:
            return FIELD_QUESTION.get(missing[0], "Dữ liệu ngày sinh chưa hợp lệ. Bạn kiểm tra lại nhé?")
        return "Dữ liệu ngày sinh chưa hợp lệ. Bạn kiểm tra lại nhé?"

    result = process_generate_reading(
        payload,
        request_id=request_id,
        sender_id=sender_id,
    )
    full_reading, full_status = generate_full_reading_direct(
        chart_json=result.chart_json.model_dump(mode="json"),
        request_id=request_id,
        sender_id=sender_id,
    )
    reading_id = _reading_store.create_full_free_reading(
        sender_id=sender_id,
        normalized_input_json=result.normalized_input.model_dump(mode="json"),
        chart_json=result.chart_json.model_dump(mode="json"),
        free_teaser=result.teaser,
        full_reading=full_reading,
        status=full_status,
    )
    logger.info(
        "reading_created request_id=%s sender_id=%s event=reading_created reading_id=%s",
        request_id,
        sender_id,
        reading_id,
    )
    on_reading_created(
        sender_id=sender_id,
        request_id=request_id,
        reading_id=reading_id,
    )

    outbound = build_messenger_outbound(reading_body=full_reading)
    donation_cta = _build_donation_cta()
    footer = get_config_text_first("footer_final_common", "footer_baseline", default="")
    meta = get_profile_metadata(sender_id)
    es2 = session.routing.get("entry_source") if isinstance(session.routing, dict) else None
    entry_for_cta = es2 if isinstance(es2, str) else None
    flow_for_cta = resolve_active_flow(
        has_partial_intake=False,
        paid_once=paid_once_from_metadata(meta),
        has_free_result=True,
        entry_source=entry_for_cta,
    )
    cta_hint = append_cta_after_free_hint(flow_for_cta)

    # Persist chart to session and move to HAS_CHART
    session.chart_json = result.chart_json.model_dump(mode="json")
    session.reading_id = reading_id
    session.state = ConversationState.HAS_CHART
    if not isinstance(session.routing, dict):
        session.routing = {}
    session.routing["active_flow"] = flow_for_cta

    tail_parts = [p for p in (footer, cta_hint, donation_cta) if p]
    tail = "\n\n".join(tail_parts) if tail_parts else ""
    base = f"{outbound}\n\nBạn có thể hỏi thêm về lá số vừa xem nhé."
    return f"{base}\n\n{tail}" if tail else base


def _mode_followup(
    session: MessengerSession,
    user_message: str,
    *,
    request_id: str,
) -> str:
    """HAS_CHART mode: follow-up conversation using chart as context."""
    chart_summary = _chart_summary(session.chart_json or {})
    chart_context = (
        f"Người dùng đã có lá số tử vi. Dưới đây là tóm tắt lá số:\n{chart_summary}"
    )
    system_prompt = _load_prompt("system_conversation.txt").replace(
        "{{CHART_CONTEXT}}", chart_context
    )
    return _call_openai_conversation(
        system_prompt=system_prompt,
        history=session.history,
        user_message=user_message,
        request_id=request_id,
    )


def handle_conversation(
    sender_id: str,
    text: str,
    *,
    request_id: str,
    messaging_event: dict[str, Any] | None = None,
) -> str:
    """Main entry point for the conversational bridge.

    Loads session, extracts birth fields, routes to the correct mode,
    updates history, saves session, and returns a reply string.
    """
    try:
        session = _store.get_or_create(sender_id)
    except DatabaseUnavailableError:
        logger.warning(
            "conversation_db_unavailable request_id=%s sender_id=%s event=db_unavailable",
            request_id,
            sender_id,
        )
        return "Hệ thống đang bận, vui lòng thử lại sau."

    if messaging_event:
        apply_referral_ref_to_routing(session, messaging_event)

    metadata = get_profile_metadata(sender_id)
    es = session.routing.get("entry_source") if isinstance(session.routing, dict) else None
    entry_src = es if isinstance(es, str) else None
    flow = resolve_active_flow(
        has_partial_intake=session.has_partial_intake(),
        paid_once=paid_once_from_metadata(metadata),
        has_free_result=bool(session.chart_json or session.reading_id),
        entry_source=entry_src,
    )
    if not isinstance(session.routing, dict):
        session.routing = {}
    session.routing["active_flow"] = flow

    # --- Targeted intake: field the bot is asking for (short replies) ---
    if (
        session.has_any_birth_data()
        and not session.is_birth_complete()
        and not session.chart_json
    ):
        missing = session.missing_birth_fields()
        if missing:
            first_missing = missing[0]
            targeted = _parse_targeted_fields(first_missing, text)
            if targeted:
                session.birth_data.update(targeted)
                logger.info(
                    "conversation_targeted_parse request_id=%s sender_id=%s field=%s parsed=%s event=targeted_parse",
                    request_id,
                    sender_id,
                    first_missing,
                    list(targeted.keys()),
                )

    # --- OpenAI birth extract (broad NLU) ---
    extracted = extract_birth_fields(text, request_id=request_id)
    logger.info(
        "birth_extract_result request_id=%s sender_id=%s text=%r extracted=%s birth_keys=%s event=birth_extract_result",
        request_id,
        sender_id,
        text[:200],
        list(extracted.keys()) if extracted else [],
        list(session.birth_data.keys()),
    )
    if extracted:
        session.birth_data.update(extracted)
        logger.info(
            "conversation_fields_merged request_id=%s sender_id=%s merged=%s event=fields_merged",
            request_id,
            sender_id,
            list(extracted.keys()),
        )

    # --- Mode routing (hard logic) ---
    try:
        if session.chart_json:
            # HAS_CHART: follow-up; lát 4 có thể chèn clarification một lần
            clarify = _maybe_profile_clarification(
                session, text, flow, sender_id=sender_id, request_id=request_id
            )
            if clarify:
                reply = clarify
            else:
                reply = _mode_followup(session, text, request_id=request_id)
            session.state = ConversationState.HAS_CHART

        elif session.is_birth_complete():
            # Lát 3 — KB-2 confirm trước generate
            reply = _handle_kb2_path(session, text, sender_id=sender_id, request_id=request_id)
            session.state = (
                ConversationState.HAS_CHART if session.chart_json else ConversationState.CHATTING
            )

        elif session.has_any_birth_data():
            # Partial birth_data (including newly extracted) → ask for next missing field
            reply = _mode_intake(session)
            session.state = ConversationState.CHATTING

        else:
            # No birth data at all → general tử vi chat (NEVER force intake)
            reply = _mode_chat(session, text, request_id=request_id)
            session.state = ConversationState.CHATTING

    except DatabaseUnavailableError:
        logger.warning(
            "conversation_db_unavailable request_id=%s sender_id=%s event=db_unavailable",
            request_id,
            sender_id,
        )
        return "Hệ thống đang bận, vui lòng thử lại sau."

    except psycopg.Error as e:
        # Storage error (table missing, constraint fail, etc.) — system fault.
        # Birth data is preserved so user can retry without re-entering.
        logger.exception(
            "conversation_storage_error request_id=%s sender_id=%s error=%s event=storage_error",
            request_id,
            sender_id,
            repr(e),
        )
        return "Hệ thống đang gặp lỗi lưu trữ. Vui lòng thử lại sau."

    except RuntimeError as e:
        # Config/deployment error (e.g. missing env vars).
        # Birth data is preserved so user can retry without re-entering.
        logger.exception(
            "conversation_config_error request_id=%s sender_id=%s error=%s event=config_error",
            request_id,
            sender_id,
            repr(e),
        )
        return "Hệ thống đang gặp lỗi cấu hình. Vui lòng thử lại sau hoặc liên hệ quản trị viên."

    except Exception as e:
        logger.exception(
            "conversation_error request_id=%s sender_id=%s error=%s event=conversation_error",
            request_id,
            sender_id,
            repr(e),
        )
        return "Mình đang gặp sự cố. Bạn thử lại sau nhé."

    # --- Update history and save ---
    session.add_turn("user", text)
    session.add_turn("assistant", reply)

    try:
        _store.save(session)
    except Exception as e:
        logger.exception(
            "conversation_save_failed request_id=%s sender_id=%s error=%s event=save_failed",
            request_id,
            sender_id,
            repr(e),
        )
        # Return the reply anyway — the user should still get their response

    return reply
