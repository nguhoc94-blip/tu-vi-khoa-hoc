from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from psycopg.rows import dict_row

from app.db import DatabaseUnavailableError, get_connection
from app.services.messenger_state import (
    ConversationState,
    LEGACY_CHATTING_STATES,
    MessengerSession,
)

# Flat keys that belong to birth_data in the old wizard format.
# Used for automatic migration of sessions written before the conversational bridge.
_LEGACY_BIRTH_KEYS = {
    "full_name",
    "birth_day",
    "birth_month",
    "birth_year",
    "birth_hour",
    "birth_minute",
    "gender",
    "calendar_type",
    "is_leap_lunar_month",
}


def _migrate_legacy_data(raw: dict[str, Any]) -> dict[str, Any]:
    """Migrate flat wizard data_json to the new nested format.

    Old format: {"full_name": "...", "birth_day": 1, ...}
    New format: {"birth": {...}, "history": [...], "chart": null, "reading_id": null}

    If `raw` already has the "birth" key it is assumed to be in new format.
    """
    if "birth" in raw:
        if "routing" not in raw:
            raw = {**raw, "routing": {}}
        return raw
    birth = {k: v for k, v in raw.items() if k in _LEGACY_BIRTH_KEYS}
    return {"birth": birth, "history": [], "chart": None, "reading_id": None, "routing": {}}


def _serialize(session: MessengerSession) -> str:
    payload: dict[str, Any] = {
        "birth": session.birth_data,
        "history": session.history,
        "chart": session.chart_json,
        "reading_id": session.reading_id,
        "routing": session.routing if isinstance(session.routing, dict) else {},
    }
    return json.dumps(payload, ensure_ascii=False)


class DbMessengerStateStore:
    def get_or_create(self, sender_id: str) -> MessengerSession:
        session, _created = self.get_or_create_ex(sender_id)
        return session

    def get_or_create_ex(self, sender_id: str) -> tuple[MessengerSession, bool]:
        created = False
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT sender_id, state, data_json, updated_at
                    FROM messenger_sessions
                    WHERE sender_id = %s
                    """,
                    (sender_id,),
                )
                row = cur.fetchone()
                if row is None:
                    created = True
                    cur.execute(
                        """
                        INSERT INTO messenger_sessions (sender_id, state, data_json)
                        VALUES (%s, %s, %s::jsonb)
                        RETURNING sender_id, state, data_json, updated_at
                        """,
                        (
                            sender_id,
                            ConversationState.CHATTING.value,
                            json.dumps(
                                {
                                    "birth": {},
                                    "history": [],
                                    "chart": None,
                                    "reading_id": None,
                                    "routing": {},
                                }
                            ),
                        ),
                    )
                    row = cur.fetchone()
        if row is None:
            raise DatabaseUnavailableError("Could not create session")
        return self._row_to_session(row), created

    def reset(self, sender_id: str) -> MessengerSession:
        return self._upsert(
            sender_id=sender_id,
            state=ConversationState.CHATTING,
            birth_data={},
            history=[],
            chart_json=None,
            reading_id=None,
            routing={},
        )

    def save(self, session: MessengerSession) -> None:
        self._upsert(
            sender_id=session.sender_id,
            state=session.state,
            birth_data=session.birth_data,
            history=session.history,
            chart_json=session.chart_json,
            reading_id=session.reading_id,
            routing=session.routing if isinstance(session.routing, dict) else {},
        )

    def mark_cancelled(self, sender_id: str) -> MessengerSession:
        """Reset session to clean CHATTING state (replaces old CANCELLED behavior)."""
        return self.reset(sender_id)

    def _upsert(
        self,
        *,
        sender_id: str,
        state: ConversationState,
        birth_data: dict[str, Any],
        history: list[dict[str, str]],
        chart_json: dict[str, Any] | None,
        reading_id: int | None,
        routing: dict[str, Any] | None = None,
    ) -> MessengerSession:
        route = routing if routing is not None else {}
        payload = json.dumps(
            {
                "birth": birth_data,
                "history": history,
                "chart": chart_json,
                "reading_id": reading_id,
                "routing": route,
            },
            ensure_ascii=False,
        )
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    INSERT INTO messenger_sessions (sender_id, state, data_json, updated_at)
                    VALUES (%s, %s, %s::jsonb, NOW())
                    ON CONFLICT (sender_id)
                    DO UPDATE SET
                      state = EXCLUDED.state,
                      data_json = EXCLUDED.data_json,
                      updated_at = NOW()
                    RETURNING sender_id, state, data_json, updated_at
                    """,
                    (sender_id, state.value, payload),
                )
                row = cur.fetchone()

        if row is None:
            raise DatabaseUnavailableError("Could not save session")
        return self._row_to_session(row)

    def _row_to_session(self, row: dict[str, Any]) -> MessengerSession:
        raw_state = str(row["state"])
        try:
            state = ConversationState(raw_state)
        except ValueError:
            state = ConversationState.CHATTING

        # Normalize to CHATTING if this is a legacy wizard state
        if state in LEGACY_CHATTING_STATES:
            state = ConversationState.CHATTING

        data_json = row["data_json"]
        if isinstance(data_json, str):
            raw: dict[str, Any] = json.loads(data_json)
        else:
            raw = dict(data_json or {})

        # Migrate old flat format to new nested format
        data = _migrate_legacy_data(raw)

        birth_data: dict[str, Any] = data.get("birth") or {}
        history: list[dict[str, str]] = data.get("history") or []
        chart_json: dict[str, Any] | None = data.get("chart") or None
        reading_id_raw = data.get("reading_id")
        reading_id: int | None = int(reading_id_raw) if reading_id_raw is not None else None

        routing_raw = data.get("routing")
        routing: dict[str, Any] = dict(routing_raw) if isinstance(routing_raw, dict) else {}

        updated_at_raw = row["updated_at"]
        updated_at = updated_at_raw if isinstance(updated_at_raw, datetime) else datetime.now()

        return MessengerSession(
            sender_id=str(row["sender_id"]),
            state=state,
            birth_data=birth_data,
            history=history,
            chart_json=chart_json,
            reading_id=reading_id,
            routing=routing,
            updated_at=updated_at,
        )
