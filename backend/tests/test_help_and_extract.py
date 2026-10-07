import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_help.db")
os.environ.setdefault("SECRET_KEY", "test-secret")

from fastapi.testclient import TestClient

from app.main import app


def test_help_ask_matches_known_topic():
    with TestClient(app) as client:
        resp = client.post("/api/help/ask", json={"question": "What documents do I need?", "language": "en"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["matched"] is True
        assert body["topic"] == "documents"


def test_help_ask_falls_back_for_unscoped_questions():
    with TestClient(app) as client:
        resp = client.post(
            "/api/help/ask", json={"question": "What is the capital of France?", "language": "en"}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["matched"] is False


def test_help_ask_respects_language():
    with TestClient(app) as client:
        resp = client.post("/api/help/ask", json={"question": "aadhaar password safe", "language": "hi"})
        assert resp.status_code == 200
        assert "आधार" in resp.json()["answer"]


def test_tutorial_returns_ordered_steps():
    with TestClient(app) as client:
        resp = client.get("/api/help/tutorial?language=en")
        assert resp.status_code == 200
        steps = resp.json()
        assert len(steps) >= 5
        assert steps[0]["step_id"] == "welcome"


def test_profile_extract_endpoint():
    with TestClient(app) as client:
        resp = client.post(
            "/api/profile/extract",
            json={"text": "I am a 20 year old engineering student from Tamil Nadu earning 1.5 lakh."},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["age"] == 20
        assert body["state"] == "Tamil Nadu"


def teardown_module(module):
    for f in ("test_help.db",):
        if os.path.exists(f):
            try:
                os.remove(f)
            except PermissionError:
                pass
