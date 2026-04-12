"""
Nhịp 1 — funnel events, token logging hooks, return window, raw attribution.
Tách khỏi conversation_bridge.py (orchestrator hội thoại) để tránh trùng tên module.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from psycopg import errors

from app.db import get_connection

logger = logging.getLogger(__name__)

RETURN_WINDOW_DAYS_ENGINEERING_LOCKED: tuple[int, ...] = (1, 7, 30)


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def record_funnel_event(
    *,
    sender_id: str,
    event_type: str,
    request_id: str | None,
    payload: dict[str, Any] | None = None,
) -> None:
    if not sender_id:
        return
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO funnel_events
                        (sender_id, event_type, request_id, payload_json)
                    VALUES (%s, %s, %s, %s::jsonb)
                    """,
                    (
                        sender_id,
                        event_type,
                        request_id,
                        json.dumps(payload or {}),
                    ),
                )
    except errors.UndefinedTable:
        logger.warning("funnel_events_missing event=funnel_events_table_missing type=%s", event_type)
    except Exception:
        logger.exception("funnel_event_write_failed event_type=%s", event_type)


def record_openai_token_usage(
    *,
    sender_id: str | None,
    request_id: str | None,
    model: str,
    prompt_tokens: int | None,
    completion_tokens: int | None,
    total_tokens: int | None,
) -> None:
    if not sender_id:
        return
    record_funnel_event(
        sender_id=sender_id,
        event_type="openai_token_usage",
        request_id=request_id,
        payload={
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        },
    )


def on_conversation_started(*, sender_id: str, request_id: str | None) -> None:
    record_funnel_event(
        sender_id=sender_id,
        event_type="conversation_started",
        request_id=request_id,
        payload={},
    )


def on_reading_created(
    *,
    sender_id: str,
    request_id: str | None,
    reading_id: int,
) -> None:
    record_funnel_event(
        sender_id=sender_id,
        event_type="free_result_sent",
        request_id=request_id,
        payload={"reading_id": reading_id},
    )


def on_birthdata_confirmation_requested(
    *, sender_id: str, request_id: str | None
) -> None:
    record_funnel_event(
        sender_id=sender_id,
        event_type="birthdata_confirmation_requested",
        request_id=request_id,
        payload={},
    )


def on_birthdata_confirmed(*, sender_id: str, request_id: str | None) -> None:
    record_funnel_event(
        sender_id=sender_id,
        event_type="birthdata_confirmed",
        request_id=request_id,
        payload={},
    )


def touch_user_profile_activity(*, sender_id: str) -> None:
    now = _utcnow()
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO user_profiles (sender_id, last_seen_at, last_activity_at, updated_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (sender_id) DO UPDATE SET
                        last_seen_at = EXCLUDED.last_seen_at,
                        last_activity_at = EXCLUDED.last_activity_at,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (sender_id, now, now, now),
                )
    except errors.UndefinedTable:
        pass
    except Exception:
        logger.exception("user_profile_touch_failed sender_id=%s", sender_id)


def update_return_window_baseline(*, sender_id: str, request_id: str | None) -> None:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT last_activity_at, last_seen_at
                    FROM user_profiles
                    WHERE sender_id = %s
                    """,
                    (sender_id,),
                )
                row = cur.fetchone()
            if row is None:
                return
            last_act, last_seen = row[0], row[1]
            ref = last_act or last_seen
            if ref is None:
                return
            if getattr(ref, "tzinfo", None) is None:
                ref = ref.replace(tzinfo=timezone.utc)
            delta_days = (_utcnow() - ref).total_seconds() / 86400.0
            bucket: int | None = None
            for days in sorted(RETURN_WINDOW_DAYS_ENGINEERING_LOCKED, reverse=True):
                if delta_days >= float(days):
                    bucket = days
                    break
            if bucket is None:
                return
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE user_profiles
                    SET last_return_window_days = %s, updated_at = %s
                    WHERE sender_id = %s
                      AND (last_return_window_days IS DISTINCT FROM %s)
                    """,
                    (bucket, _utcnow(), sender_id, bucket),
                )
                changed = (cur.rowcount or 0) > 0
            if changed:
                record_funnel_event(
                    sender_id=sender_id,
                    event_type="return_window_detected",
                    request_id=request_id,
                    payload={
                        "bucket_days": bucket,
                        "delta_days": round(delta_days, 4),
                        "thresholds": list(RETURN_WINDOW_DAYS_ENGINEERING_LOCKED),
                    },
                )
    except errors.UndefinedTable:
        pass
    except Exception:
        logger.exception("return_window_baseline_failed sender_id=%s", sender_id)


def persist_attribution_raw(
    *,
    sender_id: str,
    referral_ref: str | None,
    referral_source: str | None,
    postback_payload_raw: str | None,
) -> None:
    if not any([referral_ref, referral_source, postback_payload_raw]):
        return
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO user_profiles (sender_id, attribution_ref, attribution_source,
                        attribution_payload_raw, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (sender_id) DO UPDATE SET
                        attribution_ref = COALESCE(EXCLUDED.attribution_ref, user_profiles.attribution_ref),
                        attribution_source = COALESCE(EXCLUDED.attribution_source, user_profiles.attribution_source),
                        attribution_payload_raw = COALESCE(
                            EXCLUDED.attribution_payload_raw,
                            user_profiles.attribution_payload_raw
                        ),
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        sender_id,
                        referral_ref,
                        referral_source,
                        postback_payload_raw,
                        _utcnow(),
                    ),
                )
    except errors.UndefinedTable:
        pass
    except Exception:
        logger.exception("attribution_persist_failed sender_id=%s", sender_id)


def extract_referral_from_event(event: dict[str, Any]) -> tuple[str | None, str | None]:
    ref_obj = event.get("referral")
    if not isinstance(ref_obj, dict):
        return None, None
    ref = ref_obj.get("ref")
    source = ref_obj.get("source")
    r = ref.strip() if isinstance(ref, str) else None
    s = source.strip() if isinstance(source, str) else None
    return r, s


def extract_postback_payload_raw(event: dict[str, Any]) -> str | None:
    pb = event.get("postback")
    if not isinstance(pb, dict):
        return None
    payload = pb.get("payload")
    if isinstance(payload, str) and payload.strip():
        return payload.strip()
    return None


def on_inbound_messaging_event(
    *,
    sender_id: str,
    request_id: str | None,
    event: dict[str, Any],
) -> None:
    update_return_window_baseline(sender_id=sender_id, request_id=request_id)
    touch_user_profile_activity(sender_id=sender_id)
    r, s = extract_referral_from_event(event)
    raw_pb = extract_postback_payload_raw(event)
    persist_attribution_raw(
        sender_id=sender_id,
        referral_ref=r,
        referral_source=s,
        postback_payload_raw=raw_pb,
    )
