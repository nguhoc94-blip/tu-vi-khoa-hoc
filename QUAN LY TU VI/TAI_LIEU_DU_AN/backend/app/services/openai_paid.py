from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from openai import OpenAI

from app.services.messenger_funnel_bridge import record_openai_token_usage
from app.services.prompt_adapter import to_prompt_input_json
from app.services.reading_postcheck import postcheck_full_text
from app.services.reading_store_db import ReadingStoreDb

logger = logging.getLogger(__name__)

DEFAULT_PAID_MODEL = "gpt-5.4"
PAID_TIMEOUT_SECONDS = 60.0
PAID_FALLBACK_MESSAGE = "Ban doc day du tam thoi chua san sang. Vui long thu lai sau."
ALREADY_AVAILABLE_MESSAGE = "Ban doc day du da co san. Neu can, vui long xem lai ket qua moi nhat."


def _backend_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_prompt(name: str) -> str:
    return (_backend_dir() / "prompts" / name).read_text(encoding="utf-8")


def _inject_json_hoso(template: str, chart_json: dict[str, Any]) -> str:
    prompt_input_json = to_prompt_input_json(chart_json)
    return template.replace("{{JSON_HOSO}}", json.dumps(prompt_input_json, ensure_ascii=False))


def _generate_paid_with_openai(
    *,
    chart_json: dict[str, Any],
    request_id: str,
    sender_id: str | None = None,
) -> tuple[bool, str]:
    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        logger.warning(
            "openai_paid_fallback request_id=%s event=openai_paid_fallback reason=missing_api_key",
            request_id,
        )
        return False, PAID_FALLBACK_MESSAGE

    model = (
        (os.environ.get("PAID_OPENAI_MODEL") or "").strip()
        or (os.environ.get("OPENAI_MODEL") or "").strip()
        or DEFAULT_PAID_MODEL
    )

    try:
        system_content = _inject_json_hoso(_load_prompt("system_full_production.txt"), chart_json)
        user_content = _inject_json_hoso(_load_prompt("user_full_production.txt"), chart_json)
        client = OpenAI(api_key=api_key, timeout=PAID_TIMEOUT_SECONDS)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content},
            ],
        )
        usage = getattr(completion, "usage", None)
        if sender_id and usage is not None:
            record_openai_token_usage(
                sender_id=sender_id,
                request_id=request_id,
                model=model,
                prompt_tokens=getattr(usage, "prompt_tokens", None),
                completion_tokens=getattr(usage, "completion_tokens", None),
                total_tokens=getattr(usage, "total_tokens", None),
            )
        text = (completion.choices[0].message.content or "").strip()
        if not text:
            logger.warning(
                "openai_paid_fallback request_id=%s event=openai_paid_fallback reason=empty_response",
                request_id,
            )
            return False, PAID_FALLBACK_MESSAGE

        ok, checked_text = postcheck_full_text(text)
        if not ok:
            logger.warning(
                "openai_paid_fallback request_id=%s event=openai_paid_fallback reason=postcheck_blocked",
                request_id,
            )
            return False, checked_text

        logger.info(
            "openai_paid_success request_id=%s event=openai_paid_success model=%s",
            request_id,
            model,
        )
        return True, checked_text
    except Exception as e:
        logger.warning(
            "openai_paid_fallback request_id=%s event=openai_paid_fallback reason=%s detail=%s",
            request_id,
            type(e).__name__,
            str(e)[:400],
        )
        return False, PAID_FALLBACK_MESSAGE


def unlock_demo_for_sender(*, sender_id: str, request_id: str) -> str:
    store = ReadingStoreDb()
    locked = store.get_latest_locked_by_sender(sender_id)
    if locked is None:
        latest = store.get_latest_by_sender(sender_id)
        if latest and bool(latest.get("is_unlocked")) and latest.get("full_reading"):
            return ALREADY_AVAILABLE_MESSAGE
        return "Chua co ban doc nao de mo khoa demo. Vui long tao teaser truoc."

    reading_id = int(locked["id"])
    store.set_status(reading_id=reading_id, status="unlock_requested", is_unlocked=True)
    logger.info(
        "reading_unlocked request_id=%s sender_id=%s event=reading_unlocked reading_id=%s",
        request_id,
        sender_id,
        reading_id,
    )

    chart_json = locked.get("chart_json") or {}
    if not isinstance(chart_json, dict):
        chart_json = dict(chart_json)

    success, full_text = _generate_paid_with_openai(
        chart_json=chart_json,
        request_id=request_id,
        sender_id=sender_id,
    )
    if success:
        store.set_status(
            reading_id=reading_id,
            status="full_generated",
            is_unlocked=True,
            full_reading=full_text,
        )
        return full_text

    store.set_status(
        reading_id=reading_id,
        status="full_fallback",
        is_unlocked=True,
        full_reading=full_text,
    )
    return full_text


def generate_full_reading_direct(
    *,
    chart_json: dict[str, Any],
    request_id: str,
    sender_id: str | None = None,
) -> tuple[str, str]:
    success, text = _generate_paid_with_openai(
        chart_json=chart_json,
        request_id=request_id,
        sender_id=sender_id,
    )
    if success:
        return text, "full_generated_free"
    return text, "full_fallback_free"

