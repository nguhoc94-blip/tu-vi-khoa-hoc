"""Flow priority + entry source → active_flow (CP1). Pure logic + config key helpers."""

from __future__ import annotations

from typing import Any

from app.services.messenger_state import MessengerSession

ENTRY_LOVE = "love"
ENTRY_CAREER = "career"
ENTRY_ORGANIC_GENERAL = "organic_general"

FLOW_INTAKE_ABANDONED = "intake_abandoned_resume"
FLOW_PAID_REPEAT = "paid_once_repeat"
FLOW_RETURNING_UNPAID = "returning_unpaid"
FLOW_NEW_LOVE = "new_user_love"
FLOW_NEW_CAREER = "new_user_career"
FLOW_NEW_GENERAL = "new_user_general"


def resolve_active_flow(
    *,
    has_partial_intake: bool,
    paid_once: bool,
    has_free_result: bool,
    entry_source: str | None,
) -> str:
    """
    Priority (Product):
      1) intake_abandoned_resume
      2) paid_once_repeat
      3) returning_unpaid
      4) route by entry source → new_user_*
    """
    if has_partial_intake:
        return FLOW_INTAKE_ABANDONED
    if paid_once:
        return FLOW_PAID_REPEAT
    if has_free_result:
        return FLOW_RETURNING_UNPAID
    src = entry_source or ENTRY_ORGANIC_GENERAL
    if src == ENTRY_LOVE:
        return FLOW_NEW_LOVE
    if src == ENTRY_CAREER:
        return FLOW_NEW_CAREER
    return FLOW_NEW_GENERAL


def opening_package_config_keys(flow: str) -> tuple[str, str | None, str]:
    """(greeting_key, trust_bridge_final_key_or_none, opening_question_key)."""
    if flow == FLOW_NEW_LOVE:
        return ("greeting_love", "trust_bridge_final_love", "opening_question_love")
    if flow == FLOW_NEW_CAREER:
        return ("greeting_career", "trust_bridge_final_career", "opening_question_career")
    if flow == FLOW_NEW_GENERAL:
        return ("greeting_general", "trust_bridge_final_general", "opening_question_general")
    if flow == FLOW_RETURNING_UNPAID:
        return (
            "reactivation_in_window_returning",
            "trust_bridge_final_returning_unpaid",
            "opening_question_returning_unpaid",
        )
    if flow == FLOW_INTAKE_ABANDONED:
        return (
            "reactivation_in_window_resume",
            "trust_bridge_final_intake_resume",
            "opening_question_intake_resume",
        )
    if flow == FLOW_PAID_REPEAT:
        return (
            "reactivation_in_window_paid_repeat",
            "trust_bridge_final_paid_repeat",
            "opening_question_paid_repeat",
        )
    return ("greeting_general", "trust_bridge_final_general", "opening_question_general")


def cta_config_keys_after_free(flow: str) -> tuple[str, str, str, str] | None:
    """(primary_final, secondary_final, primary_legacy, secondary_legacy)."""
    mapping: dict[str, tuple[str, str, str, str]] = {
        FLOW_NEW_LOVE: (
            "cta_primary_final_love",
            "cta_secondary_final_love",
            "cta_primary_after_free_love",
            "cta_secondary_after_free_love",
        ),
        FLOW_NEW_CAREER: (
            "cta_primary_final_career",
            "cta_secondary_final_career",
            "cta_primary_after_free_career",
            "cta_secondary_after_free_career",
        ),
        FLOW_NEW_GENERAL: (
            "cta_primary_final_general",
            "cta_secondary_final_general",
            "cta_primary_after_free_general",
            "cta_secondary_after_free_general",
        ),
        FLOW_RETURNING_UNPAID: (
            "cta_primary_final_returning_unpaid",
            "cta_secondary_final_returning_unpaid",
            "cta_primary_after_free_returning_unpaid",
            "cta_secondary_after_free_returning_unpaid",
        ),
        FLOW_PAID_REPEAT: (
            "cta_primary_final_paid_repeat",
            "cta_secondary_final_paid_repeat",
            "cta_primary_after_free_paid_repeat",
            "cta_secondary_after_free_paid_repeat",
        ),
        FLOW_INTAKE_ABANDONED: (
            "cta_primary_final_intake_resume",
            "cta_secondary_final_intake_resume",
            "intake_resume_qr_resume",
            "intake_resume_qr_edit",
        ),
    }
    return mapping.get(flow)


_REF_TO_ENTRY: dict[str, str] = {
    "love": ENTRY_LOVE,
    "career": ENTRY_CAREER,
    "organic_general": ENTRY_ORGANIC_GENERAL,
    "general": ENTRY_ORGANIC_GENERAL,
}


def apply_referral_ref_to_routing(session: MessengerSession, event: dict[str, Any]) -> None:
    from app.services.messenger_funnel_bridge import extract_referral_from_event

    ref, _src = extract_referral_from_event(event)
    if not ref:
        return
    key = ref.strip().lower()
    if key not in _REF_TO_ENTRY:
        return
    if not isinstance(session.routing, dict):
        session.routing = {}
    session.routing["entry_source"] = _REF_TO_ENTRY[key]
