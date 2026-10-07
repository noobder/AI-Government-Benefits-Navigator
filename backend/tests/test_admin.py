import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_admin.db")
os.environ.setdefault("SECRET_KEY", "test-secret")

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.account import Account
from app.services.auth_service import hash_password


def _make_admin(email: str, password: str):
    db = SessionLocal()
    try:
        db.add(Account(email=email, password_hash=hash_password(password), role="admin"))
        db.commit()
    finally:
        db.close()


def test_admin_can_create_update_delete_scheme():
    with TestClient(app) as client:
        _make_admin("admin1@example.com", "adminpassword123")
        login = client.post("/api/auth/login", json={"email": "admin1@example.com", "password": "adminpassword123"})
        assert login.status_code == 200
        assert login.json()["role"] == "admin"

        create_payload = {
            "scheme_id": "test_admin_scheme_001",
            "scheme_name": "[TEST] Admin Created Scheme",
            "description": "Created by an automated test.",
            "category": "Education",
            "level": "State",
            "applicable_states": ["Tamil Nadu"],
            "eligibility_rules": {"operator": "AND", "conditions": [{"field": "age", "operator": ">=", "value": 18}]},
            "benefits": ["Sample benefit"],
            "required_documents": ["ID proof"],
            "application_steps": ["Apply online"],
            "official_url": "https://example.gov.in",
            "source_url": "https://example.gov.in",
            "source_name": "Test source",
            "last_verified": "2026-01-01",
            "is_demo": True,
        }
        create_resp = client.post("/api/admin/schemes", json=create_payload)
        assert create_resp.status_code == 201
        assert create_resp.json()["scheme_id"] == "test_admin_scheme_001"

        # Public endpoint should now see it too
        public_resp = client.get("/api/schemes/test_admin_scheme_001")
        assert public_resp.status_code == 200

        update_resp = client.put(
            "/api/admin/schemes/test_admin_scheme_001", json={"scheme_name": "[TEST] Renamed Scheme"}
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["scheme_name"] == "[TEST] Renamed Scheme"

        audit_resp = client.get("/api/admin/audit-log")
        assert audit_resp.status_code == 200
        actions = [row["action"] for row in audit_resp.json()]
        assert "scheme.create" in actions
        assert "scheme.update" in actions

        delete_resp = client.delete("/api/admin/schemes/test_admin_scheme_001")
        assert delete_resp.status_code == 204

        gone_resp = client.get("/api/schemes/test_admin_scheme_001")
        assert gone_resp.status_code == 404


def test_creating_duplicate_scheme_id_conflicts():
    with TestClient(app) as client:
        _make_admin("admin2@example.com", "adminpassword123")
        client.post("/api/auth/login", json={"email": "admin2@example.com", "password": "adminpassword123"})

        payload = {
            "scheme_id": "demo_edu_001",  # already exists in seed data
            "scheme_name": "Duplicate",
            "category": "Education",
            "level": "State",
        }
        resp = client.post("/api/admin/schemes", json=payload)
        assert resp.status_code == 409


def teardown_module(module):
    for f in ("test_admin.db",):
        if os.path.exists(f):
            try:
                os.remove(f)
            except PermissionError:
                pass
