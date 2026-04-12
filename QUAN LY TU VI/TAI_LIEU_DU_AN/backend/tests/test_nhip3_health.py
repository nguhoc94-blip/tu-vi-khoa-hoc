"""Nhịp 3 — /health metadata (liveness, no DB)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_health_ok() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["service"] == "tuvi-backend"


def test_health_includes_git_metadata_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GIT_SHA", "abc123deadbeef")
    monkeypatch.setenv("BUILD_TIME", "2026-04-11T12:00:00Z")
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    j = r.json()
    assert j.get("git_sha") == "abc123deadbeef"
    assert j.get("build_time") == "2026-04-11T12:00:00Z"
