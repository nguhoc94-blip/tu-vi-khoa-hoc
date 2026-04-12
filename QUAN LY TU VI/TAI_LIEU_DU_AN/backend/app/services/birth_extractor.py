"""
Birth data extractor — NLU layer for the conversational bridge.

CONTRACT:
- ONLY extracts birth fields from natural language. Does not answer tử vi questions.
- Returns a partial dict with only the fields it is CONFIDENT about.
- If uncertain about a field → omits it (no guessing).
- If OpenAI is unavailable or returns invalid JSON → returns {} (safe fallback).
- Never raises; callers can always proceed with an empty extraction.

The extraction is a cheap, small call (max_tokens=300). It runs on every
incoming message, but does not replace the conversational response — it feeds
birth_data accumulation only.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from openai import OpenAI

logger = logging.getLogger(__name__)

_EXTRACTION_MODEL = "gpt-4o-mini"  # always use fast/cheap model for extraction
_EXTRACTION_TIMEOUT = 10.0
_EXTRACTION_MAX_TOKENS = 300

# Allowed output keys — anything outside this set is stripped (safety guard)
_ALLOWED_KEYS: frozenset[str] = frozenset(
    {
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
)


def _load_system_prompt() -> str:
    path = Path(__file__).resolve().parents[2] / "prompts" / "system_extraction.txt"
    return path.read_text(encoding="utf-8")


def _validate_field(key: str, value: Any) -> Any | None:
    """Return the validated value, or None to discard it."""
    if key == "full_name":
        return str(value).strip() if isinstance(value, str) and value.strip() else None
    if key in ("birth_day", "birth_month", "birth_year", "birth_hour", "birth_minute"):
        try:
            v = int(value)
        except (TypeError, ValueError):
            return None
        limits = {
            "birth_day": (1, 31),
            "birth_month": (1, 12),
            "birth_year": (1900, 2100),
            "birth_hour": (0, 23),
            "birth_minute": (0, 59),
        }
        lo, hi = limits[key]
        return v if lo <= v <= hi else None
    if key == "gender":
        v = str(value).lower().strip()
        return v if v in ("male", "female") else None
    if key == "calendar_type":
        v = str(value).lower().strip()
        return v if v in ("solar", "lunar") else None
    if key == "is_leap_lunar_month":
        if isinstance(value, bool):
            return value
        v = str(value).lower().strip()
        if v in ("true", "1", "yes", "co", "có"):
            return True
        if v in ("false", "0", "no", "khong", "không"):
            return False
        return None
    return None


def extract_birth_fields(text: str, *, request_id: str) -> dict[str, Any]:
    """Extract birth fields from free text using OpenAI.

    Returns a partial dict with validated fields only.
    Returns {} on any error (OpenAI unavailable, invalid JSON, etc.).
    """
    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        logger.warning(
            "birth_extractor_skip request_id=%s event=extractor_skip reason=missing_api_key",
            request_id,
        )
        return {}

    try:
        system_prompt = _load_system_prompt()
        client = OpenAI(api_key=api_key, timeout=_EXTRACTION_TIMEOUT)
        completion = client.chat.completions.create(
            model=_EXTRACTION_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0,
        )
        raw_content = (completion.choices[0].message.content or "").strip()

        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError:
            logger.warning(
                "birth_extractor_invalid_json request_id=%s event=extractor_invalid_json raw=%s",
                request_id,
                raw_content[:200],
            )
            return {}

        if not isinstance(parsed, dict):
            return {}

        # Validate and filter to allowed keys only
        result: dict[str, Any] = {}
        for key, value in parsed.items():
            if key not in _ALLOWED_KEYS:
                continue
            validated = _validate_field(key, value)
            if validated is not None:
                result[key] = validated

        logger.info(
            "birth_extractor_ok request_id=%s event=extractor_ok fields=%s",
            request_id,
            list(result.keys()),
        )
        return result

    except Exception as e:
        logger.warning(
            "birth_extractor_failed request_id=%s event=extractor_failed reason=%s",
            request_id,
            type(e).__name__,
        )
        return {}
