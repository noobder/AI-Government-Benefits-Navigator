import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_auth.db")
os.environ.setdefault("SECRET_KEY", "test-secret")

from fastapi.testclient import TestClient

from app.main import app


def test_register_login_me_logout_flow():
    with TestClient(app) as client:
        resp = client.post("/api/auth/register", json={"email": "alice@example.com", "password": "correcthorse123"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == "alice@example.com"
        assert body["role"] == "user"

        # register response sets cookies; a fresh session should now see "me"
        me = client.get("/api/auth/me")
        assert me.status_code == 200
        assert me.json()["email"] == "alice@example.com"

        logout = client.post("/api/auth/logout")
        assert logout.status_code == 200

        me_after_logout = client.get("/api/auth/me")
        assert me_after_logout.json() is None


def test_duplicate_registration_is_rejected():
    with TestClient(app) as client:
        client.post("/api/auth/register", json={"email": "bob@example.com", "password": "correcthorse123"})
        resp = client.post("/api/auth/register", json={"email": "bob@example.com", "password": "anotherpassword"})
        assert resp.status_code == 409


def test_login_with_wrong_password_is_rejected():
    with TestClient(app) as client:
        client.post("/api/auth/register", json={"email": "carol@example.com", "password": "correcthorse123"})
        client.post("/api/auth/logout")
        resp = client.post("/api/auth/login", json={"email": "carol@example.com", "password": "wrong-password"})
        assert resp.status_code == 401


def test_login_locks_account_after_repeated_failures():
    with TestClient(app) as client:
        client.post("/api/auth/register", json={"email": "dave@example.com", "password": "correcthorse123"})
        client.post("/api/auth/logout")
        for _ in range(5):
            client.post("/api/auth/login", json={"email": "dave@example.com", "password": "wrong"})
        locked_resp = client.post("/api/auth/login", json={"email": "dave@example.com", "password": "wrong"})
        assert locked_resp.status_code == 423


def test_non_admin_cannot_reach_admin_routes():
    with TestClient(app) as client:
        client.post("/api/auth/register", json={"email": "eve@example.com", "password": "correcthorse123"})
        resp = client.get("/api/admin/schemes")
        assert resp.status_code == 403


def test_guest_cannot_reach_admin_routes():
    with TestClient(app) as client:
        resp = client.get("/api/admin/schemes")
        assert resp.status_code == 401


def teardown_module(module):
    for f in ("test_auth.db",):
        if os.path.exists(f):
            try:
                os.remove(f)
            except PermissionError:
                pass
