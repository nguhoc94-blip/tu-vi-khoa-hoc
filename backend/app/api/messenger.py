from __future__ import annotations

import logging
import os
import uuid
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import PlainTextResponse

from app.services.messenger_handler import process_incoming_text, send_text_message

logger = logging.getLogger(__name__)

router = APIRouter(tags=["messenger"])


@router.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(default="", alias="hub.mode"),
    hub_verify_token: str = Query(default="", alias="hub.verify_token"),
    hub_challenge: str = Query(default="", alias="hub.challenge"),
) -> PlainTextResponse:
    expected_token = (os.environ.get("FB_VERIFY_TOKEN") or "").strip()
    if hub_mode == "subscribe" and expected_token and hub_verify_token == expected_token:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Webhook verification failed")


@router.post("/webhook")
def receive_webhook(payload: dict[str, Any] = Body(...)) -> dict[str, str]:
    request_id = str(uuid.uuid4())
    entries = payload.get("entry", [])
    for entry in entries:
        messaging_events = entry.get("messaging", [])
        for event in messaging_events:
            sender_id = str(event.get("sender", {}).get("id", ""))
            if not sender_id:
                logger.info(
                    "messenger_event_ignored request_id=%s sender_id=unknown event=missing_sender",
                    request_id,
                )
                continue

            message = event.get("message", {})
            text = message.get("text")
            if isinstance(text, str) and text.strip():
                logger.info(
                    "messenger_text_received request_id=%s sender_id=%s event=text_message",
                    request_id,
                    sender_id,
                )
                process_incoming_text(sender_id, text)
                continue

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

    return {"status": "ok"}

