"""
10 acceptance tests for the conversational bridge MVP.

All OpenAI calls and DB interactions are mocked.
"""

from __future__ import annotations

import json
import logging
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.messenger_state import (
    ConversationState,
    MAX_HISTORY,
    MessengerSession,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_webhook_payload(text: str, sender_id: str = "user_001", mid: str = "mid_test_001") -> dict[str, Any]:
    return {
        "object": "page",
        "entry": [
            {
                "messaging": [
                    {
                        "sender": {"id": sender_id},
                        "message": {"mid": mid, "text": text},
                    }
                ]
            }
        ],
    }


def _make_session(
    *,
    birth_data: dict | None = None,
    chart_json: dict | None = None,
    history: list | None = None,
    state: ConversationState = ConversationState.CHATTING,
    routing: dict | None = None,
    reading_id: int | None = None,
) -> MessengerSession:
    return MessengerSession(
        sender_id="user_001",
        state=state,
        birth_data=birth_data or {},
        history=history or [],
        chart_json=chart_json,
        routing=dict(routing or {}),
        reading_id=reading_id,
    )


# ---------------------------------------------------------------------------
# Test 1: webhook returns 200 immediately (task scheduled, not called inline)
# ---------------------------------------------------------------------------

def test_webhook_returns_200_immediately() -> None:
    """POST /webhook must return HTTP 200 and schedule background work via add_task."""
    from fastapi import BackgroundTasks

    client = TestClient(app)
    # Patching add_task prevents actual execution while letting us assert it was scheduled.
    with patch.object(BackgroundTasks, "add_task") as mock_add_task:
        resp = client.post("/webhook", json=_make_webhook_payload("hello"))

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    # Task was scheduled (not run inline on the request thread)
    mock_add_task.assert_called()


# ---------------------------------------------------------------------------
# Test 2: webhook schedules background task with correct args
# ---------------------------------------------------------------------------

def test_webhook_schedules_background_task() -> None:
    """Background task must be scheduled with sender_id and text."""
    from fastapi import BackgroundTasks

    client = TestClient(app)
    # Use a unique mid to avoid dedup store pollution from other tests
    with patch.object(BackgroundTasks, "add_task") as mock_add_task:
        client.post("/webhook", json=_make_webhook_payload("hello", mid="mid_sched_unique_001"))

    mock_add_task.assert_called()
    call_args = mock_add_task.call_args
    func = call_args[0][0]
    sender_arg = call_args[0][1]
    event_arg = call_args[0][2]
    text_arg = call_args[0][3]
    assert func.__name__ == "process_messaging_pipeline"
    assert sender_arg == "user_001"
    assert text_arg == "hello"
    assert event_arg["message"]["text"] == "hello"


# ---------------------------------------------------------------------------
# Test 3: duplicate event is skipped
# ---------------------------------------------------------------------------

def test_duplicate_event_is_skipped(caplog: pytest.LogCaptureFixture) -> None:
    """Same message mid: second delivery logs webhook_duplicate_skipped (DB dedupe)."""
    from fastapi import BackgroundTasks

    client = TestClient(app)
    claim_calls = iter([True, False])

    def _claim(*args: object, **kwargs: object) -> bool:
        return next(claim_calls)

    with (
        patch.object(BackgroundTasks, "add_task"),
        patch("app.api.messenger.try_claim_webhook_delivery", side_effect=_claim),
        caplog.at_level(logging.INFO, logger="app.api.messenger"),
    ):
        resp1 = client.post("/webhook", json=_make_webhook_payload("hello", mid="mid_dup_002"))
        resp2 = client.post("/webhook", json=_make_webhook_payload("hello", mid="mid_dup_002"))

    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert any("webhook_duplicate_skipped" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# Test 4: natural chat gets a reply (no birth data → CHAT mode)
# ---------------------------------------------------------------------------

def test_natural_chat_gets_reply() -> None:
    """When user sends general chat with no birth data, bot replies naturally."""
    session = _make_session()

    with (
        patch("app.services.conversation_bridge._store") as mock_store,
        patch("app.services.conversation_bridge.extract_birth_fields", return_value={}),
        patch("app.services.conversation_bridge.get_profile_metadata", return_value={}),
        patch("app.services.conversation_bridge._call_openai_conversation", return_value="Tử vi là nghệ thuật đoán vận mệnh."),
    ):
        mock_store.get_or_create.return_value = session
        mock_store.save.return_value = None

        from app.services.conversation_bridge import handle_conversation
        reply = handle_conversation("user_001", "tử vi là gì?", request_id="req_test")

    assert reply
    assert len(reply) > 0
    assert "Tử vi" in reply or "tử vi" in reply.lower()


# ---------------------------------------------------------------------------
# Test 5: natural-language birth data extraction
# ---------------------------------------------------------------------------

def test_birth_data_extraction_from_natural_language(monkeypatch: pytest.MonkeyPatch) -> None:
    """Extractor must parse common Vietnamese date patterns."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake-key-for-unit-test")
    with patch("app.services.birth_extractor.OpenAI") as MockOpenAI:
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = json.dumps({
            "birth_day": 5,
            "birth_month": 6,
            "birth_year": 1990,
        })
        MockOpenAI.return_value.chat.completions.create.return_value = mock_completion

        from app.services.birth_extractor import extract_birth_fields
        result = extract_birth_fields("tôi sinh ngày 5 tháng 6 năm 1990", request_id="req_test")

    assert result.get("birth_day") == 5
    assert result.get("birth_month") == 6
    assert result.get("birth_year") == 1990


# ---------------------------------------------------------------------------
# Test 6: missing fields trigger targeted follow-up
# ---------------------------------------------------------------------------

def test_missing_fields_trigger_targeted_question() -> None:
    """When birth_data has all fields except gender, bot asks exactly for gender."""
    partial_birth = {
        "full_name": "Test User",
        "birth_day": 1,
        "birth_month": 3,
        "birth_year": 1990,
        "birth_hour": 7,
        "birth_minute": 0,
        "calendar_type": "solar",
        # gender is intentionally missing
    }
    session = _make_session(birth_data=partial_birth)

    with (
        patch("app.services.conversation_bridge._store") as mock_store,
        patch("app.services.conversation_bridge.extract_birth_fields", return_value={}),
        patch("app.services.conversation_bridge.get_profile_metadata", return_value={}),
    ):
        mock_store.get_or_create.return_value = session
        mock_store.save.return_value = None

        from app.services.conversation_bridge import handle_conversation
        reply = handle_conversation("user_001", "ok", request_id="req_test")

    # Should ask about gender specifically
    assert "giới tính" in reply.lower() or "nam" in reply.lower() or "nữ" in reply.lower()
    # Should NOT ask about fields already provided
    assert "năm sinh" not in reply.lower()
    assert "ngày sinh" not in reply.lower()


# ---------------------------------------------------------------------------
# Test 6b: targeted parse — short hour reply breaks infinite INTAKE loop
# ---------------------------------------------------------------------------

def test_targeted_parse_birth_hour_16_not_loop() -> None:
    """When first missing is birth_hour, '16' must set birth_hour without OpenAI."""
    partial_birth = {
        "full_name": "User",
        "birth_day": 16,
        "birth_month": 1,
        "birth_year": 1995,
    }
    session = _make_session(birth_data=partial_birth)

    with (
        patch("app.services.conversation_bridge._store") as mock_store,
        patch("app.services.conversation_bridge.extract_birth_fields", return_value={}),
        patch("app.services.conversation_bridge.get_profile_metadata", return_value={}),
    ):
        mock_store.get_or_create.return_value = session
        mock_store.save.return_value = None

        from app.services.conversation_bridge import handle_conversation
        reply = handle_conversation("user_001", "16", request_id="req_test")

    assert session.birth_data.get("birth_hour") == 16
    assert "phút" in reply.lower()
    assert "giờ sinh" not in reply.lower()


def test_targeted_parse_16h30p_sets_hour_and_minute() -> None:
    """Vietnamese '16h30p' must fill birth_hour and birth_minute in one shot."""
    partial_birth = {
        "full_name": "User",
        "birth_day": 16,
        "birth_month": 1,
        "birth_year": 1995,
    }
    session = _make_session(birth_data=partial_birth)

    with (
        patch("app.services.conversation_bridge._store") as mock_store,
        patch("app.services.conversation_bridge.extract_birth_fields", return_value={}),
        patch("app.services.conversation_bridge.get_profile_metadata", return_value={}),
    ):
        mock_store.get_or_create.return_value = session
        mock_store.save.return_value = None

        from app.services.conversation_bridge import handle_conversation
        reply = handle_conversation("user_001", "16h30p", request_id="req_test")

    assert session.birth_data.get("birth_hour") == 16
    assert session.birth_data.get("birth_minute") == 30
    assert "giới tính" in reply.lower()


def test_parse_targeted_fields_unit() -> None:
    from app.services.conversation_bridge import _parse_targeted_fields

    assert _parse_targeted_fields("birth_hour", "16") == {"birth_hour": 16}
    assert _parse_targeted_fields("birth_hour", "16h") == {"birth_hour": 16}
    assert _parse_targeted_fields("birth_hour", "16h30p") == {
        "birth_hour": 16,
        "birth_minute": 30,
    }
    assert _parse_targeted_fields("birth_minute", "30") == {"birth_minute": 30}
    assert _parse_targeted_fields("gender", "nam") == {"gender": "male"}


# ---------------------------------------------------------------------------
# Test 7: KB-2 — summary trước generate (lát 3)
# ---------------------------------------------------------------------------

_COMPLETE_BIRTH = {
    "full_name": "Nguyễn Văn A",
    "birth_day": 1,
    "birth_month": 3,
    "birth_year": 1990,
    "birth_hour": 7,
    "birth_minute": 0,
    "gender": "male",
    "calendar_type": "solar",
}


def test_kb2_shows_summary_before_generate() -> None:
    """Đủ birth lần đầu → confirmation summary + funnel requested; chưa generate."""
    session = _make_session(birth_data=dict(_COMPLETE_BIRTH))

    with (
        patch("app.services.conversation_bridge._store") as mock_store,
        patch("app.services.conversation_bridge._reading_store") as mock_reading_store,
        patch("app.services.conversation_bridge.extract_birth_fields", return_value={}),
        patch("app.services.conversation_bridge.get_profile_metadata", return_value={}),
        patch("app.services.conversation_bridge.process_generate_reading") as mock_gen,
        patch("app.services.conversation_bridge.on_birthdata_confirmation_requested") as mock_req,
        patch("app.services.conversation_bridge.on_birthdata_confirmed") as mock_conf,
    ):
        mock_store.get_or_create.return_value = session
        mock_store.save.return_value = None

        from app.services.conversation_bridge import handle_conversation

        reply = handle_conversation("user_001", "xem tử vi giúp mình", request_id="req_test")

    mock_gen.assert_not_called()
    mock_req.assert_called_once()
    mock_conf.assert_not_called()
    assert session.routing.get("kb2_awaiting_confirm") is True
    assert "Nguyễn Văn A" in reply or "chốt" in reply.lower()


def test_kb2_confirm_triggers_chart_generation() -> None:
    """Sau KB-2 awaiting, user xác nhận → birthdata_confirmed + generate."""
    session = _make_session(
        birth_data=dict(_COMPLETE_BIRTH),
        routing={"kb2_awaiting_confirm": True},
    )

    mock_result = MagicMock()
    mock_result.chart_json.model_dump.return_value = {"menh": {}, "houses": []}
    mock_result.normalized_input.model_dump.return_value = {}
    mock_result.teaser = "teaser"

    with (
        patch("app.services.conversation_bridge._store") as mock_store,
        patch("app.services.conversation_bridge._reading_store") as mock_reading_store,
        patch("app.services.conversation_bridge.extract_birth_fields", return_value={}),
        patch("app.services.conversation_bridge.get_profile_metadata", return_value={}),
        patch("app.services.conversation_bridge.process_generate_reading", return_value=mock_result) as mock_gen,
        patch(
            "app.services.conversation_bridge.generate_full_reading_direct",
            return_value=("Full reading text", "full_generated_free"),
        ),
        patch("app.services.conversation_bridge.build_messenger_outbound", return_value="Outbound message"),
        patch("app.services.conversation_bridge.on_birthdata_confirmation_requested") as mock_req,
        patch("app.services.conversation_bridge.on_birthdata_confirmed") as mock_conf,
    ):
        mock_store.get_or_create.return_value = session
        mock_store.save.return_value = None
        mock_reading_store.create_full_free_reading.return_value = 42

        from app.services.conversation_bridge import handle_conversation

        reply = handle_conversation("user_001", "đúng rồi", request_id="req_test")

    mock_gen.assert_called_once()
    mock_req.assert_not_called()
    mock_conf.assert_called_once()
    assert reply


# ---------------------------------------------------------------------------
# Test 8: follow-up after chart works
# ---------------------------------------------------------------------------

def test_followup_after_chart_uses_chart_context() -> None:
    """When session has chart_json, follow-up must send chart context to OpenAI."""
    chart = {"menh": {"menh": "Hỏa"}, "can_chi": {}, "houses": []}
    session = _make_session(
        chart_json=chart,
        state=ConversationState.HAS_CHART,
    )

    captured_system_prompt: list[str] = []

    def mock_openai_call(*, system_prompt: str, history: list, user_message: str, request_id: str) -> str:
        captured_system_prompt.append(system_prompt)
        return "Mệnh Hỏa thường năng động và nhiệt huyết."

    with (
        patch("app.services.conversation_bridge._store") as mock_store,
        patch("app.services.conversation_bridge.extract_birth_fields", return_value={}),
        patch("app.services.conversation_bridge.get_profile_metadata", return_value={}),
        patch("app.services.conversation_bridge._call_openai_conversation", side_effect=mock_openai_call),
    ):
        mock_store.get_or_create.return_value = session
        mock_store.save.return_value = None

        from app.services.conversation_bridge import handle_conversation
        reply = handle_conversation("user_001", "mệnh tôi là gì?", request_id="req_test")

    # Chart context must appear in the system prompt
    assert captured_system_prompt, "OpenAI was not called"
    assert "Hỏa" in captured_system_prompt[0] or "chart" in captured_system_prompt[0].lower() or "lá số" in captured_system_prompt[0]
    assert reply


# ---------------------------------------------------------------------------
# Test 9: long outbound messages are split safely
# ---------------------------------------------------------------------------

def test_long_messages_split_safely() -> None:
    """_split_text must produce chunks of at most 1500 chars."""
    from app.services.messenger_handler import _split_text

    long_text = "Đây là nội dung tử vi rất dài.\n" * 200  # ~6200 chars
    chunks = _split_text(long_text, max_len=1500)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 1500


# ---------------------------------------------------------------------------
# Test 10: background failures are logged
# ---------------------------------------------------------------------------

def test_background_failure_is_logged(caplog: pytest.LogCaptureFixture) -> None:
    """If handle_incoming_text raises, webhook_background_failed must be logged."""
    from app.services.messenger_handler import process_messaging_pipeline

    event = {
        "sender": {"id": "user_001"},
        "message": {"text": "hello", "mid": "evt_001"},
    }
    with (
        patch("app.services.messenger_handler.handle_incoming_text", side_effect=RuntimeError("boom")),
        patch("app.services.messenger_handler.send_sender_action", MagicMock()),
        patch("app.services.messenger_handler.on_inbound_messaging_event", MagicMock()),
        patch(
            "app.services.messenger_handler._store.get_or_create_ex",
            return_value=(MagicMock(), False),
        ),
        caplog.at_level(logging.ERROR, logger="app.services.messenger_handler"),
    ):
        process_messaging_pipeline("user_001", event, "hello", "req-bg-fail")

    assert any("background_failed" in r.message for r in caplog.records)
