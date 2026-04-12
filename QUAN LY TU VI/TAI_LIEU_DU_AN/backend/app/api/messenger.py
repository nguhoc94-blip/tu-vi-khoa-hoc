from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.middleware.webhook_signature import (
    WebhookSignatureError,
    verify_if_configured,
)
from app.services.event_dedupe_db import (
    build_dedupe_key_from_messaging_event,
    try_claim_webhook_delivery,
)
from app.services.messenger_handler import process_messaging_pipeline
from app.utils.log_redact import redact_log_line

logger = logging.getLogger(__name__)

_DEFAULT_MAX_WEBHOOK_BYTES = 256 * 1024


def _max_webhook_body_bytes() -> int:
    raw = (os.environ.get("MAX_WEBHOOK_BODY_BYTES") or "").strip()
    if not raw:
        return _DEFAULT_MAX_WEBHOOK_BYTES
    try:
        return max(1024, min(int(raw), 2 * 1024 * 1024))
    except ValueError:
        return _DEFAULT_MAX_WEBHOOK_BYTES

router = APIRouter(tags=["messenger"])


@router.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(default="", alias="hub.mode"),
    hub_verify_token: str = Query(default="", alias="hub.verify_token"),
    hub_challenge: str = Query(default="", alias="hub.challenge"),
) -> PlainTextResponse:
    import os

    expected_token = (os.environ.get("FB_VERIFY_TOKEN") or "").strip()
    if hub_mode == "subscribe" and expected_token and hub_verify_token == expected_token:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Webhook verification failed")


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    raw_body = await request.body()
    request_id = str(uuid.uuid4())
    max_bytes = _max_webhook_body_bytes()
    if len(raw_body) > max_bytes:
        logger.warning(
            "webhook_payload_too_large request_id=%s bytes=%s max=%s event=payload_too_large",
            request_id,
            len(raw_body),
            max_bytes,
        )
        raise HTTPException(status_code=413, detail="payload too large")
    sig = request.headers.get("x-hub-signature-256")
    try:
        verify_if_configured(raw_body=raw_body, signature_header=sig)
    except WebhookSignatureError as e:
        logger.warning(
            "webhook_signature_rejected request_id=%s event=webhook_signature_rejected detail=%s",
            request_id,
            e,
        )
        raise HTTPException(status_code=403, detail="Invalid webhook signature") from e

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail="Invalid JSON body") from e

    entries = payload.get("entry", [])
    for entry in entries:
        messaging_events = entry.get("messaging", [])
        for event in messaging_events:
            sender_id = str(event.get("sender", {}).get("id", ""))
            if not sender_id:
                logger.info(
                    "webhook_event_ignored request_id=%s sender_id=unknown event=missing_sender",
                    request_id,
                )
                continue

            dedupe_key = build_dedupe_key_from_messaging_event(event)
            excerpt_raw = json.dumps(event, ensure_ascii=False)[:500] if dedupe_key else None
            excerpt = redact_log_line(excerpt_raw) if excerpt_raw else None
            if dedupe_key and not try_claim_webhook_delivery(
                dedupe_key=dedupe_key,
                sender_id=sender_id,
                payload_excerpt=excerpt,
            ):
                logger.info(
                    "webhook_duplicate_skipped request_id=%s sender_id=%s dedupe_key=%s",
                    request_id,
                    sender_id,
                    dedupe_key,
                )
                continue

            message = event.get("message", {})
            text = message.get("text")
            text_str = text.strip() if isinstance(text, str) else None

            background_tasks.add_task(
                process_messaging_pipeline,
                sender_id,
                event,
                text_str,
                request_id,
            )
            logger.info(
                "webhook_event_scheduled request_id=%s sender_id=%s event=webhook_event_scheduled",
                request_id,
                sender_id,
            )

    return {"status": "ok"}
