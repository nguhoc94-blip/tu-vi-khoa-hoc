from __future__ import annotations

from app.services.flow_routing import (
    ENTRY_CAREER,
    ENTRY_LOVE,
    ENTRY_ORGANIC_GENERAL,
    FLOW_INTAKE_ABANDONED,
    FLOW_NEW_CAREER,
    FLOW_NEW_LOVE,
    FLOW_NEW_GENERAL,
    FLOW_PAID_REPEAT,
    FLOW_RETURNING_UNPAID,
    resolve_active_flow,
)


def test_priority_intake_over_paid() -> None:
    assert (
        resolve_active_flow(
            has_partial_intake=True,
            paid_once=True,
            has_free_result=True,
            entry_source=ENTRY_LOVE,
        )
        == FLOW_INTAKE_ABANDONED
    )


def test_priority_paid_over_returning() -> None:
    assert (
        resolve_active_flow(
            has_partial_intake=False,
            paid_once=True,
            has_free_result=True,
            entry_source=None,
        )
        == FLOW_PAID_REPEAT
    )


def test_returning_unpaid_before_entry_source() -> None:
    assert (
        resolve_active_flow(
            has_partial_intake=False,
            paid_once=False,
            has_free_result=True,
            entry_source=ENTRY_CAREER,
        )
        == FLOW_RETURNING_UNPAID
    )


def test_entry_love_career_general() -> None:
    assert (
        resolve_active_flow(
            has_partial_intake=False,
            paid_once=False,
            has_free_result=False,
            entry_source=ENTRY_LOVE,
        )
        == FLOW_NEW_LOVE
    )
    assert (
        resolve_active_flow(
            has_partial_intake=False,
            paid_once=False,
            has_free_result=False,
            entry_source=ENTRY_CAREER,
        )
        == FLOW_NEW_CAREER
    )
    assert (
        resolve_active_flow(
            has_partial_intake=False,
            paid_once=False,
            has_free_result=False,
            entry_source=ENTRY_ORGANIC_GENERAL,
        )
        == FLOW_NEW_GENERAL
    )


def test_default_entry_organic() -> None:
    assert (
        resolve_active_flow(
            has_partial_intake=False,
            paid_once=False,
            has_free_result=False,
            entry_source=None,
        )
        == FLOW_NEW_GENERAL
    )
