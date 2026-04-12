from __future__ import annotations

import json
import logging
import os
import threading
import time
import urllib.error
import urllib.request
import uuid
from typing import Any

from app.services.flow_routing import apply_referral_ref_to_routing
from app.services.messenger_funnel_bridge import (
    on_conversation_started,
    on_inbound_messaging_event,
)
from app.services.messenger_state import RESET_COMMANDS
from app.services.messenger_state_db import DbMessengerStateStore
from app.services import payload_specs as payload_specs_mod
from app.services.payload_handler import apply_structured_payload
from app.services.openai_paid import unlock_demo_for_sender

logger = logging.getLogger(__name__)

_store = DbMessengerStateStore()

_SEND_RETRIES = 3
_SEND_BACKOFF_SEC = 0.6
_DEFAULT_MAX_INBOUND_CHARS = 8000
_DEFAULT_DEBOUNCE_SECONDS = 1.5

# Per-sender lock + debounce state
_meta_lock = threading.Lock()
_sender_locks: dict[str, threading.Lock] = {}
_sender_pending: dict[str, str] = {}  # sender_id → latest request_id


def _get_debounce_seconds() -> float:
    raw = (os.environ.get("DEBOUNCE_SECONDS") or "").strip()
    try:
        return max(0.0, float(raw)) if raw else _DEFAULT_DEBOUNCE_SECONDS
    except ValueError:
        return _DEFAULT_DEBOUNCE_SECONDS


def _get_sender_lock(sender_id: str) -> threading.Lock:
    with _meta_lock:
        if sender_id not in _sender_locks:
            _sender_locks[sender_id] = threading.Lock()
        return _sender_locks[sender_id]


def _register_pending(sender_id: str, request_id: str) -> None:
    with _meta_lock:
        _sender_pending[sender_id] = request_id


def _is_still_latest(sender_id: str, request_id: str) -> bool:
    with _meta_lock:
        return _sender_pending.get(sender_id) == request_id


def _max_inbound_text_chars() -> int:
    raw = (os.environ.get("MAX_INBOUND_TEXT_CHARS") or "").strip()
    if not raw:
        return _DEFAULT_MAX_INBOUND_CHARS
    try:
        return max(500, min(int(raw), 32000))
    except ValueError:
        return _DEFAULT_MAX_INBOUND_CHARS


def send_sender_action(sender_id: str, action: str, *, request_id: str) -> None:
    page_access_token = (os.environ.get("FB_PAGE_ACCESS_TOKEN") or "").strip()
    if not page_access_token:
        return
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={page_access_token}"
    payload = {
        "recipient": {"id": sender_id},
        "sender_action": action,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            logger.info(
                "messenger_sender_action_ok request_id=%s sender_id=%s action=%s status=%s",
                request_id,
                sender_id,
                action,
                resp.getcode(),
            )
    except urllib.error.URLError:
        logger.warning(
            "messenger_sender_action_failed request_id=%s sender_id=%s action=%s",
            request_id,
            sender_id,
            action,
        )


def send_text_message(sender_id: str, text: str, *, request_id: str) -> None:
    page_access_token = (os.environ.get("FB_PAGE_ACCESS_TOKEN") or "").strip()
    if not page_access_token:
        logger.warning(
            "messenger_send_skipped_missing_token request_id=%s sender_id=%s event=send_skipped",
            request_id,
            sender_id,
        )
        return

    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={page_access_token}"
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": sender_id},
        "message": {"text": text},
    }
    data = json.dumps(payload).encode("utf-8")

    for attempt in range(1, _SEND_RETRIES + 1):
        req = urllib.request.Request(
            url=url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                logger.info(
                    "messenger_send_ok request_id=%s sender_id=%s event=send_text status=%s attempt=%s",
                    request_id,
                    sender_id,
                    resp.getcode(),
                    attempt,
                )
                return
        except urllib.error.HTTPError as e:
            logger.warning(
                "messenger_send_http_error request_id=%s sender_id=%s status=%s attempt=%s",
                request_id,
                sender_id,
                e.code,
                attempt,
            )
            if attempt < _SEND_RETRIES:
                time.sleep(_SEND_BACKOFF_SEC * attempt)
        except urllib.error.URLError as e:
            logger.warning(
                "messenger_send_retry request_id=%s sender_id=%s attempt=%s err=%s",
                request_id,
                sender_id,
                attempt,
                str(e.reason),
            )
            if attempt < _SEND_RETRIES:
                time.sleep(_SEND_BACKOFF_SEC * attempt)

    logger.warning(
        "messenger_send_failed request_id=%s sender_id=%s event=send_text_failed",
        request_id,
        sender_id,
    )


def _split_text(text: str, max_len: int = 1500) -> list[str]:
    if not text:
        return []
    chunks: list[str] = []
    current = ""
    for para in text.split("\n"):
        piece = para if not current else current + "\n" + para
        if len(piece) <= max_len:
            current = piece
        else:
            if current:
                chunks.append(current)
            if len(para) <= max_len:
                current = para
            else:
                for i in range(0, len(para), max_len):
                    chunks.append(para[i : i + max_len])
                current = ""
    if current:
        chunks.append(current)
    return chunks


def extract_messaging_payload(event: dict[str, Any]) -> str | None:
    postback = event.get("postback")
    if isinstance(postback, dict):
        pl = postback.get("payload")
        if isinstance(pl, str) and pl.strip():
            return pl.strip()
    msg = event.get("message")
    if isinstance(msg, dict):
        qr = msg.get("quick_reply")
        if isinstance(qr, dict):
            qpl = qr.get("payload")
            if isinstance(qpl, str) and qpl.strip():
                return qpl.strip()
    return None


def _handle_reset(sender_id: str, *, request_id: str) -> str:
    _store.reset(sender_id)
    logger.info(
        "messenger_session_reset request_id=%s sender_id=%s event=session_reset",
        request_id,
        sender_id,
    )
    return "Đã bắt đầu lại. Bạn muốn hỏi gì về tử vi, mình sẵn sàng lắng nghe!"


def handle_incoming_text(
    sender_id: str,
    text: str,
    *,
    request_id: str,
    messaging_event: dict[str, Any] | None = None,
) -> str:
    from app.services.conversation_bridge import handle_conversation

    normalized = text.strip()

    if normalized.lower() == "unlock_demo":
        return unlock_demo_for_sender(sender_id=sender_id, request_id=request_id)

    if normalized.lower() in RESET_COMMANDS:
        return _handle_reset(sender_id, request_id=request_id)

    return handle_conversation(
        sender_id,
        normalized,
        request_id=request_id,
        messaging_event=messaging_event,
    )


def process_messaging_pipeline(
    sender_id: str,
    event: dict[str, Any],
    text: str | None,
    request_id: str,
) -> None:
    """
    Background: attribution/return plumbing, optional conversation_started on new PSID row,
    then text reply path.

    Implements per-sender lock + debounce:
    - Lock ensures serial processing per sender (no race conditions on session).
    - Debounce skips older tasks when user sends multiple messages quickly;
      only the latest message is processed. Postbacks bypass debounce.
    """
    is_text = bool(text and text.strip())
    is_postback = bool(event.get("postback"))

    # Register as latest pending for this sender (text messages only)
    if is_text and not is_postback:
        _register_pending(sender_id, request_id)
        debounce = _get_debounce_seconds()
        if debounce > 0:
            time.sleep(debounce)
            if not _is_still_latest(sender_id, request_id):
                logger.info(
                    "debounce_skipped request_id=%s sender_id=%s event=debounce_skipped",
                    request_id,
                    sender_id,
                )
                return

    sender_lock = _get_sender_lock(sender_id)
    with sender_lock:
        # After acquiring lock, double-check debounce for text messages
        if is_text and not is_postback and not _is_still_latest(sender_id, request_id):
            logger.info(
                "debounce_skipped_after_lock request_id=%s sender_id=%s event=debounce_skipped_after_lock",
                request_id,
                sender_id,
            )
            return

        _do_process_messaging_pipeline(sender_id, event, text, request_id)


def _do_process_messaging_pipeline(
    sender_id: str,
    event: dict[str, Any],
    text: str | None,
    request_id: str,
) -> None:
    """Core pipeline logic — called inside per-sender lock."""
    logger.info(
        "webhook_background_started request_id=%s sender_id=%s event=background_started",
        request_id,
        sender_id,
    )
    try:
        on_inbound_messaging_event(
            sender_id=sender_id,
            request_id=request_id,
            event=event,
        )

        had_text = bool(text and text.strip())
        structured = extract_messaging_payload(event)

        try:
            session, created = _store.get_or_create_ex(sender_id)
            apply_referral_ref_to_routing(session, event)
            _store.save(session)
            if created:
                on_conversation_started(sender_id=sender_id, request_id=request_id)
        except Exception:
            logger.exception(
                "messenger_get_or_create_ex_failed request_id=%s sender_id=%s",
                request_id,
                sender_id,
            )

        if structured:
            apply_result = apply_structured_payload(
                sender_id=sender_id,
                payload=structured,
                request_id=request_id,
                had_user_text=had_text,
            )
            if apply_result.reply_immediate:
                send_sender_action(sender_id, "typing_on", request_id=request_id)
                for chunk in _split_text(apply_result.reply_immediate):
                    send_text_message(sender_id, chunk, request_id=request_id)
            if not apply_result.continue_with_text:
                logger.info(
                    "webhook_background_completed request_id=%s sender_id=%s event=background_completed",
                    request_id,
                    sender_id,
                )
                return

        if had_text:
            lim = _max_inbound_text_chars()
            if text and len(text) > lim:
                logger.warning(
                    "messenger_inbound_text_truncated request_id=%s sender_id=%s len=%s max=%s event=text_too_long",
                    request_id,
                    sender_id,
                    len(text),
                    lim,
                )
                send_text_message(
                    sender_id,
                    "Tin nhắn của bạn quá dài. Bạn gửi ngắn gọn hơn giúp mình nhé.",
                    request_id=request_id,
                )
            else:
                send_sender_action(sender_id, "typing_on", request_id=request_id)
                reply = handle_incoming_text(
                    sender_id,
                    text or "",
                    request_id=request_id,
                    messaging_event=event,
                )
                chunks = _split_text(reply)
                logger.info(
                    "send_text_prepare request_id=%s sender_id=%s chunks=%s event=send_prepare",
                    request_id,
                    sender_id,
                    len(chunks),
                )
                for chunk in chunks:
                    send_text_message(sender_id, chunk, request_id=request_id)
        elif event.get("message"):
            logger.info(
                "messenger_non_text_received request_id=%s sender_id=%s event=non_text_message",
                request_id,
                sender_id,
            )
            send_text_message(
                sender_id,
                "Hiện bot chỉ hỗ trợ tin nhắn văn bản.",
                request_id=request_id,
            )
        elif event.get("postback") and (
            not structured or structured not in payload_specs_mod.ALL_BASELINE_PAYLOADS
        ):
            logger.info(
                "messenger_postback_no_reply request_id=%s sender_id=%s event=postback_no_handler",
                request_id,
                sender_id,
            )

        logger.info(
            "webhook_background_completed request_id=%s sender_id=%s event=background_completed",
            request_id,
            sender_id,
        )
    except Exception as e:
        logger.exception(
            "webhook_background_failed request_id=%s sender_id=%s error=%s event=background_failed",
            request_id,
            sender_id,
            repr(e),
        )
