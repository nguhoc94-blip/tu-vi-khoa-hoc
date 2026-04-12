from __future__ import annotations

import json
import logging
from typing import Any

from psycopg.rows import dict_row

from app.db import get_connection

logger = logging.getLogger(__name__)


def get_config_value(config_key: str) -> dict[str, Any] | None:
    try:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT config_value
                    FROM app_config
                    WHERE config_key = %s
                    """,
                    (config_key,),
                )
                row = cur.fetchone()
        if not row:
            return None
        raw = row["config_value"]
        if isinstance(raw, dict):
            return dict(raw)
        if isinstance(raw, str):
            return json.loads(raw)
        return dict(raw or {})
    except Exception:
        logger.debug("app_config_get_failed key=%s", config_key, exc_info=True)
        return None


def get_config_text(config_key: str, default: str = "") -> str:
    val = get_config_value(config_key)
    if not val:
        return default
    t = val.get("text")
    return str(t).strip() if t is not None else default


# Runtime Messenger chỉ đọc cột published (config_value). draft_value chỉ dùng trong admin.
_TRUST_FINAL_FALLBACK: dict[str, str] = {
    "trust_bridge_final_love": "trust_bridge_new_user_love",
    "trust_bridge_final_career": "trust_bridge_new_user_career",
    "trust_bridge_final_general": "trust_bridge_new_user_general",
    "trust_bridge_final_returning_unpaid": "trust_bridge_returning_unpaid",
    "trust_bridge_final_intake_resume": "",
    "trust_bridge_final_paid_repeat": "trust_bridge_paid_repeat",
}


def get_config_text_first(*keys: str, default: str = "") -> str:
    """Thử lần lượt các key published; dùng cho CP3 final + fallback CP2."""
    for k in keys:
        if not k:
            continue
        t = get_config_text(k, "")
        if t:
            return t
    return default


def get_config_text_trust_final(trust_final_key: str) -> str:
    fb = _TRUST_FINAL_FALLBACK.get(trust_final_key, "")
    return get_config_text_first(trust_final_key, fb)


def compose_opening_text(greeting_key: str, trust_key: str | None, opening_key: str) -> str:
    parts: list[str] = []
    g = get_config_text(greeting_key)
    if g:
        parts.append(g)
    if trust_key:
        t = (
            get_config_text_trust_final(trust_key)
            if trust_key.startswith("trust_bridge_final_")
            else get_config_text(trust_key)
        )
        if t:
            parts.append(t)
    o = get_config_text(opening_key)
    if o:
        parts.append(o)
    return "\n\n".join(parts) if parts else ""
