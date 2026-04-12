from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.services import payload_specs as P
from app.services.messenger_state import MessengerSession
from app.services.payload_handler import apply_structured_payload


def test_secondary_returning_unpaid_emits_upsell_secondary() -> None:
    session = MessengerSession(sender_id="u1", routing={})
    with (
        patch("app.services.payload_handler._store.get_or_create", return_value=session),
        patch("app.services.payload_handler._store.save", MagicMock()),
        patch("app.services.payload_handler.get_profile_metadata", return_value={}),
        patch("app.services.payload_handler.record_funnel_event") as mock_funnel,
    ):
        apply_structured_payload(
            sender_id="u1",
            payload=P.TV_CTA_SECONDARY_RETURNING_UNPAID,
            request_id="r1",
            had_user_text=False,
        )
    types = [c.kwargs.get("event_type") for c in mock_funnel.call_args_list]
    assert "upsell_secondary_clicked" in types
