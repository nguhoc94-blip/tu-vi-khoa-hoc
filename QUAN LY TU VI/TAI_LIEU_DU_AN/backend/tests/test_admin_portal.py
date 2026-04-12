from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_admin_login_get_ok() -> None:
    client = TestClient(app)
    r = client.get("/admin/login")
    assert r.status_code == 200
    assert "Admin" in r.text


def test_admin_dashboard_redirects_without_cookie() -> None:
    client = TestClient(app)
    r = client.get("/admin/dashboard", follow_redirects=False)
    assert r.status_code == 302
    assert "/admin/login" in (r.headers.get("location") or "")
