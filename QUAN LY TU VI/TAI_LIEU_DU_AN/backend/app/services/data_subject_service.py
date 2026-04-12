"""Baseline anonymization for a Messenger sender_id (Nhịp 3 — audit via admin)."""

from __future__ import annotations

import json
import logging
from typing import Any

from psycopg import errors

from app.db import get_connection

logger = logging.getLogger(__name__)

_ANON_SESSION_PAYLOAD = {
    "anonymized": True,
    "birth": {},
    "history": [],
    "routing": {},
    "chart": None,
    "reading_id": None,
}


def anonymize_sender_baseline(sender_id: str) -> dict[str, Any]:
    """
    Scrub PII-heavy fields for sender_id. Keeps row keys where required (readings id)
    but replaces text/json content with redacted placeholders.
    """
    sid = (sender_id or "").strip()
    if not sid:
        raise ValueError("sender_id is required")

    summary: dict[str, Any] = {
        "sender_id": sid,
        "messenger_sessions_updated": 0,
        "readings_updated": 0,
        "conversation_history_deleted": 0,
        "funnel_events_deleted": 0,
        "webhook_dedupe_deleted": 0,
        "orders_updated": 0,
        "user_profiles_deleted": 0,
    }

    session_json = json.dumps(_ANON_SESSION_PAYLOAD)

    with get_connection() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """
                        UPDATE messenger_sessions
                        SET state = 'CHATTING', data_json = %s::jsonb, updated_at = NOW()
                        WHERE sender_id = %s
                        """,
                        (session_json, sid),
                    )
                    summary["messenger_sessions_updated"] = cur.rowcount or 0
                except errors.UndefinedTable:
                    pass

                try:
                    cur.execute(
                        """
                        UPDATE readings
                        SET
                            normalized_input_json = '{"anonymized":true}'::jsonb,
                            chart_json = '{"anonymized":true}'::jsonb,
                            free_teaser = '[REDACTED]',
                            full_reading = '[REDACTED]',
                            updated_at = NOW()
                        WHERE sender_id = %s
                        """,
                        (sid,),
                    )
                    summary["readings_updated"] = cur.rowcount or 0
                except errors.UndefinedTable:
                    pass

                try:
                    cur.execute(
                        "DELETE FROM conversation_history WHERE sender_id = %s",
                        (sid,),
                    )
                    summary["conversation_history_deleted"] = cur.rowcount or 0
                except errors.UndefinedTable:
                    pass

                try:
                    cur.execute(
                        "DELETE FROM funnel_events WHERE sender_id = %s",
                        (sid,),
                    )
                    summary["funnel_events_deleted"] = cur.rowcount or 0
                except errors.UndefinedTable:
                    pass

                try:
                    cur.execute(
                        "DELETE FROM webhook_dedupe WHERE sender_id = %s",
                        (sid,),
                    )
                    summary["webhook_dedupe_deleted"] = cur.rowcount or 0
                except errors.UndefinedTable:
                    pass

                try:
                    cur.execute(
                        """
                        UPDATE orders
                        SET metadata_json = '{"anonymized":true}'::jsonb, updated_at = NOW()
                        WHERE sender_id = %s
                        """,
                        (sid,),
                    )
                    summary["orders_updated"] = cur.rowcount or 0
                except errors.UndefinedTable:
                    pass

                try:
                    cur.execute(
                        "DELETE FROM user_profiles WHERE sender_id = %s",
                        (sid,),
                    )
                    summary["user_profiles_deleted"] = cur.rowcount or 0
                except errors.UndefinedTable:
                    pass

    logger.info(
        "data_subject_anonymized sender_id=%s sessions=%s readings=%s",
        sid,
        summary["messenger_sessions_updated"],
        summary["readings_updated"],
    )
    return summary
