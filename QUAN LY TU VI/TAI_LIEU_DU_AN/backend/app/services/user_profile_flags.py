from __future__ import annotations

import json
import logging
from typing import Any

from psycopg import errors
from psycopg.rows import dict_row

from app.db import get_connection

logger = logging.getLogger(__name__)


def get_profile_metadata(sender_id: str) -> dict[str, Any]:
    try:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT metadata_json FROM user_profiles WHERE sender_id = %s
                    """,
                    (sender_id,),
                )
                row = cur.fetchone()
        if not row:
            return {}
        raw = row["metadata_json"]
        if isinstance(raw, dict):
            return dict(raw)
        if isinstance(raw, str):
            return json.loads(raw)
        return {}
    except errors.UndefinedTable:
        return {}
    except Exception:
        logger.debug("profile_metadata_read_failed sender_id=%s", sender_id, exc_info=True)
        return {}


def paid_once_from_metadata(metadata: dict[str, Any]) -> bool:
    flags = metadata.get("flags")
    if not isinstance(flags, dict):
        return False
    return bool(flags.get("paid_once"))


def patch_profile_metadata(sender_id: str, patch: dict[str, Any]) -> None:
    if not patch:
        return
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO user_profiles (sender_id, metadata_json, updated_at)
                    VALUES (%s, %s::jsonb, NOW())
                    ON CONFLICT (sender_id) DO UPDATE SET
                        metadata_json = COALESCE(user_profiles.metadata_json, '{}'::jsonb) || EXCLUDED.metadata_json,
                        updated_at = NOW()
                    """,
                    (sender_id, json.dumps(patch)),
                )
    except errors.UndefinedTable:
        pass
    except Exception:
        logger.warning("profile_metadata_patch_failed sender_id=%s", sender_id, exc_info=True)
