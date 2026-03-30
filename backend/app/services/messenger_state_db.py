from __future__ import annotations

import json
from datetime import datetime

from psycopg.rows import dict_row

from app.db import DatabaseUnavailableError, get_connection
from app.services.messenger_state import ConversationState, MessengerSession


class DbMessengerStateStore:
    def get_or_create(self, sender_id: str) -> MessengerSession:
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
                    cur.execute(
                        """
                        INSERT INTO messenger_sessions (sender_id, state, data_json)
                        VALUES (%s, %s, %s::jsonb)
                        RETURNING sender_id, state, data_json, updated_at
                        """,
                        (sender_id, ConversationState.NEW.value, json.dumps({})),
                    )
                    row = cur.fetchone()
        if row is None:
            raise DatabaseUnavailableError("Could not create session")
        return self._row_to_session(row)

    def reset(self, sender_id: str) -> MessengerSession:
        return self._upsert(
            sender_id=sender_id,
            state=ConversationState.WAIT_FULL_NAME,
            data={},
        )

    def save(self, session: MessengerSession) -> None:
        self._upsert(
            sender_id=session.sender_id,
            state=session.state,
            data=session.data,
        )

    def set_state(self, sender_id: str, state: ConversationState) -> MessengerSession:
        session = self.get_or_create(sender_id)
        session.state = state
        self.save(session)
        return session

    def mark_cancelled(self, sender_id: str) -> MessengerSession:
        return self._upsert(
            sender_id=sender_id,
            state=ConversationState.CANCELLED,
            data={},
        )

    def _upsert(
        self,
        *,
        sender_id: str,
        state: ConversationState,
        data: dict[str, object],
    ) -> MessengerSession:
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
                    (sender_id, state.value, json.dumps(data)),
                )
                row = cur.fetchone()

        if row is None:
            raise DatabaseUnavailableError("Could not save session")
        return self._row_to_session(row)

    def _row_to_session(self, row: dict[str, object]) -> MessengerSession:
        state_value = str(row["state"])
        data_json = row["data_json"]
        if isinstance(data_json, str):
            data = json.loads(data_json)
        else:
            data = dict(data_json or {})

        updated_at_raw = row["updated_at"]
        if isinstance(updated_at_raw, datetime):
            updated_at = updated_at_raw
        else:
            updated_at = datetime.now()

        return MessengerSession(
            sender_id=str(row["sender_id"]),
            state=ConversationState(state_value),
            data=data,
            updated_at=updated_at,
        )

