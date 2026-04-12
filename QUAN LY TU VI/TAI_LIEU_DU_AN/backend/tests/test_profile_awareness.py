"""Lát 4 — multi-profile awareness tối thiểu (returning / paid_repeat + tín hiệu)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.services.conversation_bridge import handle_conversation
from app.services.messenger_state import ConversationState, MessengerSession


def test_profile_clarification_once_for_returning_flow() -> None:
    chart = {"menh": {"menh": "Hỏa"}, "can_chi": {}, "houses": []}
    session = MessengerSession(
        sender_id="u_ret",
        state=ConversationState.HAS_CHART,
        birth_data={},
        history=[],
        chart_json=chart,
        routing={"entry_source": "love"},
    )

    with (
        patch("app.services.conversation_bridge._store") as mock_store,
        patch("app.services.conversation_bridge.extract_birth_fields", return_value={}),
        patch("app.services.conversation_bridge.get_profile_metadata", return_value={}),
        patch("app.services.conversation_bridge.record_funnel_event") as mock_funnel,
        patch("app.services.conversation_bridge._call_openai_conversation") as mock_ai,
    ):
        mock_store.get_or_create.return_value = session
        mock_store.save.return_value = None

        reply = handle_conversation("u_ret", "cho mẹ tôi hỏi thêm", request_id="r1")

    mock_ai.assert_not_called()
    assert "hồ sơ" in reply.lower() or "người khác" in reply.lower()
    assert session.routing.get("profile_clarification_shown") is True
    types = [c.kwargs.get("event_type") for c in mock_funnel.call_args_list]
    assert "profile_switch_clarification_shown" in types


def test_no_clarification_when_already_shown() -> None:
    chart = {"menh": {}, "houses": []}
    session = MessengerSession(
        sender_id="u2",
        state=ConversationState.HAS_CHART,
        chart_json=chart,
        routing={"entry_source": "love", "profile_clarification_shown": True},
    )

    with (
        patch("app.services.conversation_bridge._store") as mock_store,
        patch("app.services.conversation_bridge.extract_birth_fields", return_value={}),
        patch("app.services.conversation_bridge.get_profile_metadata", return_value={}),
        patch(
            "app.services.conversation_bridge._call_openai_conversation",
            return_value="OK followup",
        ) as mock_ai,
    ):
        mock_store.get_or_create.return_value = session
        mock_store.save.return_value = None

        reply = handle_conversation("u2", "cho mẹ tôi", request_id="r2")

    mock_ai.assert_called_once()
    assert reply == "OK followup"
