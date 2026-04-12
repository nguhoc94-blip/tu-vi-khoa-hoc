from __future__ import annotations

from app.services.event_dedupe_db import build_dedupe_key_from_messaging_event


def test_dedupe_key_uses_message_mid() -> None:
    event = {"sender": {"id": "123"}, "message": {"mid": "m.abc", "text": "hi"}}
    assert build_dedupe_key_from_messaging_event(event) == "m.abc"


def test_dedupe_key_postback_fallback() -> None:
    event = {
        "sender": {"id": "u1"},
        "timestamp": 999,
        "postback": {"payload": "GET_STARTED"},
    }
    k = build_dedupe_key_from_messaging_event(event)
    assert k is not None
    assert k.startswith("pb:u1:999:")
