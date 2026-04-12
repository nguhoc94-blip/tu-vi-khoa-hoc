"""Acceptance tests for GENERATE mode error handling in conversation_bridge.

Adapted for **KB-2** (birth summary → user confirms → generate).

  Case 1 — Happy path: after confirm → reading_created, HAS_CHART.
  Case 2 — Config path: RuntimeError → "cấu hình", birth_data intact.
  Case 3 — Storage: psycopg error on insert → "lưu trữ", birth_data intact.
  Case 4 — ValueError on insert → graceful generic error, birth_data intact.
"""

from __future__ import annotations

from contextlib import ExitStack
from unittest.mock import MagicMock, patch

import psycopg
import pytest

from app.services.conversation_bridge import handle_conversation
from app.services.messenger_state import ConversationState, MessengerSession

SENDER = "test_sender_001"

_COMPLETE_BIRTH_DATA = {
    "full_name": "Nguyễn Văn A",
    "birth_day": 15,
    "birth_month": 6,
    "birth_year": 1990,
    "birth_hour": 10,
    "birth_minute": 0,
    "gender": "male",
    "calendar_type": "solar",
}


def _make_ready_session() -> MessengerSession:
    return MessengerSession(
        sender_id=SENDER,
        state=ConversationState.CHATTING,
        birth_data=dict(_COMPLETE_BIRTH_DATA),
    )


def _mock_reading_result() -> MagicMock:
    result = MagicMock()
    result.chart_json.model_dump.return_value = {"mock": "chart", "menh": {}, "can_chi": {}, "houses": []}
    result.normalized_input.model_dump.return_value = {"mock": "input"}
    result.teaser = "teaser mock"
    return result


def _enter_generate_mocks(
    stack: ExitStack,
    mock_store: MagicMock,
    mock_reading_store: MagicMock,
) -> None:
    stack.enter_context(patch("app.services.conversation_bridge._store", mock_store))
    stack.enter_context(patch("app.services.conversation_bridge._reading_store", mock_reading_store))
    stack.enter_context(patch("app.services.conversation_bridge.extract_birth_fields", return_value={}))
    stack.enter_context(patch("app.services.conversation_bridge.get_profile_metadata", return_value={}))
    stack.enter_context(
        patch(
            "app.services.conversation_bridge.process_generate_reading",
            return_value=_mock_reading_result(),
        )
    )
    stack.enter_context(
        patch(
            "app.services.conversation_bridge.generate_full_reading_direct",
            return_value=("Full reading text", "full_generated"),
        )
    )


def test_case1_happy_path_reading_created_and_completed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DONATION_TEXT", "Thanks")
    monkeypatch.setenv("DONATION_URL", "https://example.com/donate")
    monkeypatch.setenv("MESSENGER_PART_2_BANK_BLOCK", "VPBank test")
    monkeypatch.setenv("MESSENGER_PART_3_CEO_NOTE", "CEO note test")

    session = _make_ready_session()
    mock_store = MagicMock()
    mock_store.get_or_create.return_value = session
    mock_store.save.return_value = None
    mock_reading_store = MagicMock()
    mock_reading_store.create_full_free_reading.return_value = 42

    with ExitStack() as stack:
        _enter_generate_mocks(stack, mock_store, mock_reading_store)
        handle_conversation(SENDER, "xem tử vi cho mình", request_id="r1")
        assert session.routing.get("kb2_awaiting_confirm") is True
        handle_conversation(SENDER, "đúng rồi", request_id="r2")

    assert session.state == ConversationState.HAS_CHART
    assert session.chart_json is not None
    mock_reading_store.create_full_free_reading.assert_called_once()


def test_case2_config_error_does_not_reset_session(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DONATION_TEXT", "Thanks")
    monkeypatch.setenv("DONATION_URL", "https://example.com/donate")

    session = _make_ready_session()
    original_birth = dict(session.birth_data)
    mock_store = MagicMock()
    mock_store.get_or_create.return_value = session
    mock_store.save.return_value = None
    mock_reading_store = MagicMock()
    mock_reading_store.create_full_free_reading.return_value = 99

    def _boom(*_a: object, **_k: object) -> str:
        raise RuntimeError("simulated deployment config error")

    with ExitStack() as stack:
        _enter_generate_mocks(stack, mock_store, mock_reading_store)
        stack.enter_context(patch("app.services.conversation_bridge._mode_generate", side_effect=_boom))
        handle_conversation(SENDER, "xem tử vi", request_id="r1")
        response = handle_conversation(SENDER, "đúng rồi", request_id="r2")

    assert "cấu hình" in response
    assert session.birth_data == original_birth


def test_case3_db_storage_error_does_not_reset_session(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DONATION_TEXT", "Thanks")
    monkeypatch.setenv("DONATION_URL", "https://example.com/donate")

    session = _make_ready_session()
    original_birth = dict(session.birth_data)
    mock_store = MagicMock()
    mock_store.get_or_create.return_value = session
    mock_store.save.return_value = None
    mock_reading_store = MagicMock()
    mock_reading_store.create_full_free_reading.side_effect = psycopg.OperationalError(
        'relation "readings" does not exist'
    )

    with ExitStack() as stack:
        _enter_generate_mocks(stack, mock_store, mock_reading_store)
        handle_conversation(SENDER, "xem tử vi", request_id="r1")
        response = handle_conversation(SENDER, "đúng rồi", request_id="r2")

    assert "lưu trữ" in response
    assert session.birth_data == original_birth


def test_case4_unexpected_exception_graceful_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DONATION_TEXT", "Thanks")
    monkeypatch.setenv("DONATION_URL", "https://example.com/donate")

    session = _make_ready_session()
    original_birth = dict(session.birth_data)
    mock_store = MagicMock()
    mock_store.get_or_create.return_value = session
    mock_store.save.return_value = None
    mock_reading_store = MagicMock()
    mock_reading_store.create_full_free_reading.side_effect = ValueError("unexpected internal error")

    with ExitStack() as stack:
        _enter_generate_mocks(stack, mock_store, mock_reading_store)
        handle_conversation(SENDER, "xem tử vi", request_id="r1")
        response = handle_conversation(SENDER, "đúng rồi", request_id="r2")

    assert response
    assert "sự cố" in response or "thử lại" in response
    assert session.birth_data == original_birth
