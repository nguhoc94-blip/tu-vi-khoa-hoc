from __future__ import annotations

import logging
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

_env = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env)

from app.api.admin_portal import router as admin_portal_router
from app.api.messenger import router as messenger_router
from app.api.reading import router as reading_router
from app.api.unlock_demo import router as unlock_demo_router
from app.db import DatabaseUnavailableError, check_connection_ok, close_pool, init_pool
from app.db_init import run_schema_bootstrap
from app.services.admin_bootstrap import ensure_bootstrap_admin
from app.utils.log_redact import attach_redacting_formatter_to_root

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    level_name = (os.environ.get("LOG_LEVEL") or "INFO").strip().upper()
    level = getattr(logging, level_name, logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)
    if not root.handlers:
        logging.basicConfig(level=level, format=LOG_FORMAT)
    attach_redacting_formatter_to_root(fmt=LOG_FORMAT)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _configure_logging()
    log = logging.getLogger(__name__)
    skip_bootstrap = (os.environ.get("SKIP_DB_BOOTSTRAP") or "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    try:
        init_pool()
        if not skip_bootstrap:
            run_schema_bootstrap()
            ensure_bootstrap_admin()
        else:
            log.warning("skip_db_bootstrap_enabled event=skip_db_bootstrap_enabled")
    except DatabaseUnavailableError as e:
        log.warning("db_unavailable_at_startup event=db_unavailable_at_startup detail=%s", e)
    yield
    close_pool()


_configure_logging()

app = FastAPI(
    title="TuVi Messenger Bot Backend MVP",
    version="0.3.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def request_context_and_unhandled_errors(request: Request, call_next):
    rid = (request.headers.get("x-request-id") or "").strip() or str(uuid.uuid4())
    request.state.request_id = rid
    try:
        response = await call_next(request)
        response.headers.setdefault("X-Request-ID", rid)
        return response
    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "unhandled_http_error path=%s request_id=%s event=internal_error",
            request.url.path,
            rid,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "internal_error", "request_id": rid},
            headers={"X-Request-ID": rid},
        )


app.include_router(reading_router)
app.include_router(messenger_router)
app.include_router(unlock_demo_router)
app.include_router(admin_portal_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness for Render platform — no DB check (Engineering lock Nhịp 3)."""
    out: dict[str, str] = {"status": "ok", "service": "tuvi-backend"}
    sha = (os.environ.get("GIT_SHA") or "").strip()
    if sha:
        out["git_sha"] = sha[:40]
    bt = (os.environ.get("BUILD_TIME") or "").strip()
    if bt:
        out["build_time"] = bt[:64]
    return out


@app.get("/readiness")
def readiness() -> JSONResponse:
    if check_connection_ok():
        return JSONResponse(content={"status": "ready"}, status_code=200)
    return JSONResponse(content={"status": "not_ready"}, status_code=503)
