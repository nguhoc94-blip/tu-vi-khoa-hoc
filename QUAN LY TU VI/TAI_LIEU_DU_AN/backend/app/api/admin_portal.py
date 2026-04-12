"""
Admin HTML baseline — form login + HttpOnly cookie session (Nhịp 2).
Không preview dynamic free result; chỉ config/campaign/transcript/export tĩnh.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Cookie, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from psycopg.rows import dict_row

from app.db import get_connection
from app.services.admin_audit_service import write_audit_log
from app.services.admin_password import verify_password
from app.services.data_subject_service import anonymize_sender_baseline
from app.services.admin_session_service import (
    create_session,
    delete_session,
    get_session_user,
    purge_expired_sessions,
    sessions_summary_json,
)
from app.services.webhook_dedupe_cleanup import run_webhook_dedupe_retention_cleanup

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin"])
_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

ADMIN_COOKIE = "admin_sid"


def _cookie_secure() -> bool:
    return (os.environ.get("ADMIN_COOKIE_SECURE") or "").strip().lower() in ("1", "true", "yes")


def _writer_ok(user: dict[str, Any]) -> bool:
    r = (user.get("role") or "").lower()
    return r in ("admin", "operator")


@router.get("/admin/login", response_class=HTMLResponse)
def admin_login_form(request: Request) -> Any:
    return templates.TemplateResponse(request, "admin/login.html", {"error": None})


@router.post("/admin/login")
def admin_login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
) -> Response:
    purge_expired_sessions()
    try:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT id, email, password_hash, role, is_active
                    FROM admin_users WHERE LOWER(email) = LOWER(%s)
                    """,
                    (email.strip(),),
                )
                row = cur.fetchone()
    except Exception:
        logger.exception("admin_login_db_error")
        return templates.TemplateResponse(
            request,
            "admin/login.html",
            {"error": "Hệ thống đang bận."},
            status_code=503,
        )

    if not row or not row.get("is_active"):
        write_audit_log(
            admin_user_id=None,
            action="admin_login_failed",
            resource_type="admin_user",
            detail={"email": email.strip()},
        )
        return templates.TemplateResponse(
            request,
            "admin/login.html",
            {"error": "Sai email hoặc mật khẩu."},
            status_code=401,
        )

    if not verify_password(password, str(row["password_hash"])):
        write_audit_log(
            admin_user_id=int(row["id"]),
            action="admin_login_failed",
            resource_type="admin_user",
            resource_id=str(row["id"]),
            detail={"reason": "bad_password"},
        )
        return templates.TemplateResponse(
            request,
            "admin/login.html",
            {"error": "Sai email hoặc mật khẩu."},
            status_code=401,
        )

    sid = create_session(admin_user_id=int(row["id"]))
    write_audit_log(
        admin_user_id=int(row["id"]),
        action="admin_login_ok",
        resource_type="admin_user",
        resource_id=str(row["id"]),
        detail={},
    )
    resp = RedirectResponse(url="/admin/dashboard", status_code=302)
    resp.set_cookie(
        ADMIN_COOKIE,
        sid,
        httponly=True,
        secure=_cookie_secure(),
        samesite="lax",
        max_age=86400 * 7,
        path="/",
    )
    return resp


@router.post("/admin/logout")
def admin_logout(
    request: Request,
    admin_sid: str | None = Cookie(None, alias=ADMIN_COOKIE),
) -> Response:
    if admin_sid:
        delete_session(admin_sid)
    resp = RedirectResponse(url="/admin/login", status_code=302)
    resp.delete_cookie(ADMIN_COOKIE, path="/")
    return resp


def _require_user(admin_sid: str | None) -> dict[str, Any] | RedirectResponse:
    u = get_session_user(admin_sid)
    if not u:
        return RedirectResponse(url="/admin/login", status_code=302)
    return u


@router.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, admin_sid: str | None = Cookie(None, alias=ADMIN_COOKIE)) -> Any:
    u = _require_user(admin_sid)
    if isinstance(u, RedirectResponse):
        return u
    counts: dict[str, Any] = {}
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM messenger_sessions")
                counts["sessions"] = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM readings")
                counts["readings"] = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM app_config")
                counts["config_keys"] = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM campaigns")
                counts["campaigns"] = cur.fetchone()[0]
    except Exception:
        logger.exception("admin_dashboard_counts")
        counts = {"sessions": "?", "readings": "?", "config_keys": "?", "campaigns": "?"}
    return templates.TemplateResponse(request, "admin/dashboard.html", {"user": u, "counts": counts})


@router.get("/admin/config", response_class=HTMLResponse)
def admin_config_list(request: Request, admin_sid: str | None = Cookie(None, alias=ADMIN_COOKIE)) -> Any:
    u = _require_user(admin_sid)
    if isinstance(u, RedirectResponse):
        return u
    rows: list[dict[str, Any]] = []
    try:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT config_key, updated_at,
                           (draft_value IS NOT NULL) AS has_draft
                    FROM app_config ORDER BY config_key
                    """
                )
                rows = [dict(x) for x in cur.fetchall()]
    except Exception:
        logger.exception("admin_config_list")
    return templates.TemplateResponse(request, "admin/config_list.html", {"user": u, "rows": rows})


@router.get("/admin/config/{key}/edit", response_class=HTMLResponse)
def admin_config_edit(
    request: Request,
    key: str,
    admin_sid: str | None = Cookie(None, alias=ADMIN_COOKIE),
) -> Any:
    u = _require_user(admin_sid)
    if isinstance(u, RedirectResponse):
        return u
    row: dict[str, Any] | None = None
    try:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT config_key, config_value, draft_value, updated_at
                    FROM app_config WHERE config_key = %s
                    """,
                    (key,),
                )
                row = cur.fetchone()
    except Exception:
        logger.exception("admin_config_edit")
    if not row:
        return HTMLResponse("Không tìm thấy key", status_code=404)
    draft_raw = row.get("draft_value") or row.get("config_value")
    draft_txt = json.dumps(draft_raw, ensure_ascii=False, indent=2) if draft_raw else "{}"
    pub_txt = json.dumps(row.get("config_value") or {}, ensure_ascii=False, indent=2)
    return templates.TemplateResponse(
        request,
        "admin/config_edit.html",
        {
            "user": u,
            "key": key,
            "published_json": pub_txt,
            "draft_json": draft_txt,
            "can_write": _writer_ok(u),
        },
    )


@router.post("/admin/config/{key}/draft")
def admin_config_save_draft(
    request: Request,
    key: str,
    admin_sid: str | None = Cookie(None, alias=ADMIN_COOKIE),
    body: str = Form(..., alias="draft_json"),
) -> Response:
    u = _require_user(admin_sid)
    if isinstance(u, RedirectResponse):
        return u
    if not _writer_ok(u):
        return HTMLResponse("Forbidden (viewer)", status_code=403)
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return RedirectResponse(url=f"/admin/config/{key}/edit?err=json", status_code=302)
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE app_config SET draft_value = %s::jsonb, updated_at = NOW()
                    WHERE config_key = %s
                    """,
                    (json.dumps(parsed), key),
                )
        write_audit_log(
            admin_user_id=int(u["user_id"]),
            action="app_config_draft_saved",
            resource_type="app_config",
            resource_id=key,
            detail={},
        )
    except Exception:
        logger.exception("admin_config_draft_save")
        return HTMLResponse("Lỗi lưu", status_code=500)
    return RedirectResponse(url="/admin/config", status_code=302)


@router.post("/admin/config/{key}/publish")
def admin_config_publish(
    key: str,
    admin_sid: str | None = Cookie(None, alias=ADMIN_COOKIE),
) -> Response:
    u = _require_user(admin_sid)
    if isinstance(u, RedirectResponse):
        return u
    if not _writer_ok(u):
        return HTMLResponse("Forbidden (viewer)", status_code=403)
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE app_config
                    SET config_value = COALESCE(draft_value, config_value),
                        draft_value = NULL,
                        updated_at = NOW()
                    WHERE config_key = %s
                    """,
                    (key,),
                )
        write_audit_log(
            admin_user_id=int(u["user_id"]),
            action="app_config_published",
            resource_type="app_config",
            resource_id=key,
            detail={},
        )
    except Exception:
        logger.exception("admin_config_publish")
        return HTMLResponse("Lỗi publish", status_code=500)
    return RedirectResponse(url="/admin/config", status_code=302)


@router.get("/admin/campaigns", response_class=HTMLResponse)
def admin_campaigns(request: Request, admin_sid: str | None = Cookie(None, alias=ADMIN_COOKIE)) -> Any:
    u = _require_user(admin_sid)
    if isinstance(u, RedirectResponse):
        return u
    rows: list[dict[str, Any]] = []
    try:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT id, name, external_ref, updated_at,
                           (draft_config_json IS NOT NULL) AS has_draft
                    FROM campaigns ORDER BY id DESC
                    """
                )
                rows = [dict(x) for x in cur.fetchall()]
    except Exception:
        logger.exception("admin_campaigns")
    return templates.TemplateResponse(request, "admin/campaigns.html", {"user": u, "rows": rows})


@router.get("/admin/transcript", response_class=HTMLResponse)
def admin_transcript(
    request: Request,
    admin_sid: str | None = Cookie(None, alias=ADMIN_COOKIE),
    sender_id: str = "",
) -> Any:
    u = _require_user(admin_sid)
    if isinstance(u, RedirectResponse):
        return u
    history: list[dict[str, Any]] = []
    if sender_id.strip():
        try:
            with get_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(
                        """
                        SELECT data_json, updated_at, state
                        FROM messenger_sessions WHERE sender_id = %s
                        """,
                        (sender_id.strip(),),
                    )
                    row = cur.fetchone()
            if row and row.get("data_json"):
                dj = row["data_json"]
                if isinstance(dj, str):
                    dj = json.loads(dj)
                hist = (dj or {}).get("history") or []
                history = hist if isinstance(hist, list) else []
        except Exception:
            logger.exception("admin_transcript")
    return templates.TemplateResponse(
        request,
        "admin/transcript.html",
        {"user": u, "sender_id": sender_id, "history": history},
    )


@router.get("/admin/privacy", response_class=HTMLResponse)
def admin_privacy_form(
    request: Request, admin_sid: str | None = Cookie(None, alias=ADMIN_COOKIE)
) -> Any:
    u = _require_user(admin_sid)
    if isinstance(u, RedirectResponse):
        return u
    return templates.TemplateResponse(
        request,
        "admin/privacy.html",
        {"user": u, "message": None, "error": None},
    )


@router.post("/admin/privacy/anonymize")
def admin_privacy_anonymize(
    request: Request,
    admin_sid: str | None = Cookie(None, alias=ADMIN_COOKIE),
    sender_id: str = Form(...),
) -> Any:
    u = _require_user(admin_sid)
    if isinstance(u, RedirectResponse):
        return u
    if not _writer_ok(u):
        return HTMLResponse("Forbidden (viewer)", status_code=403)
    sid = (sender_id or "").strip()
    if not sid:
        return templates.TemplateResponse(
            request,
            "admin/privacy.html",
            {"user": u, "message": None, "error": "sender_id trống."},
            status_code=400,
        )
    try:
        summary = anonymize_sender_baseline(sid)
    except ValueError as e:
        return templates.TemplateResponse(
            request,
            "admin/privacy.html",
            {"user": u, "message": None, "error": str(e)},
            status_code=400,
        )
    except Exception:
        logger.exception("admin_anonymize_failed sender_id=%s", sid)
        return templates.TemplateResponse(
            request,
            "admin/privacy.html",
            {"user": u, "message": None, "error": "Lỗi hệ thống khi ẩn danh."},
            status_code=500,
        )
    write_audit_log(
        admin_user_id=int(u["user_id"]),
        action="data_subject_anonymized",
        resource_type="sender",
        resource_id=sid,
        detail=summary,
    )
    return templates.TemplateResponse(
        request,
        "admin/privacy.html",
        {"user": u, "message": f"Đã ẩn danh baseline cho sender_id={sid}.", "error": None},
    )


@router.post("/admin/maintenance/webhook-dedupe-cleanup")
def admin_webhook_dedupe_cleanup(
    request: Request,
    admin_sid: str | None = Cookie(None, alias=ADMIN_COOKIE),
) -> Any:
    u = _require_user(admin_sid)
    if isinstance(u, RedirectResponse):
        return u
    if not _writer_ok(u):
        return HTMLResponse("Forbidden (viewer)", status_code=403)
    try:
        deleted = run_webhook_dedupe_retention_cleanup()
    except Exception:
        logger.exception("admin_dedupe_cleanup_failed")
        return templates.TemplateResponse(
            request,
            "admin/privacy.html",
            {"user": u, "message": None, "error": "Cleanup dedupe thất bại."},
            status_code=500,
        )
    write_audit_log(
        admin_user_id=int(u["user_id"]),
        action="webhook_dedupe_cleanup",
        resource_type="maintenance",
        detail={"rows_deleted": deleted, "retention_hours": 24},
    )
    return templates.TemplateResponse(
        request,
        "admin/privacy.html",
        {
            "user": u,
            "message": f"Đã chạy cleanup webhook_dedupe (24h): xóa {deleted} dòng.",
            "error": None,
        },
    )


@router.get("/admin/export/sessions.json")
def admin_export_sessions(
    admin_sid: str | None = Cookie(None, alias=ADMIN_COOKIE),
) -> PlainTextResponse:
    u = _require_user(admin_sid)
    if isinstance(u, RedirectResponse):
        return PlainTextResponse("Unauthorized", status_code=401)
    if not _writer_ok(u):
        return PlainTextResponse("Forbidden", status_code=403)
    body = sessions_summary_json()
    write_audit_log(
        admin_user_id=int(u["user_id"]),
        action="admin_export_sessions",
        resource_type="export",
        detail={},
    )
    return PlainTextResponse(
        content=body,
        media_type="application/json; charset=utf-8",
    )
