import os
import sys

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_benefits_navigator.db")

from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        resp = client.get("/api/health")
        assert resp.status_code == 200


def test_list_schemes_returns_seeded_demo_data():
    with TestClient(app) as client:
        resp = client.get("/api/schemes")
        assert resp.status_code == 200
        schemes = resp.json()
        assert len(schemes) >= 10
        assert all(s["is_demo"] for s in schemes)


def test_match_student_scenario_returns_relevant_scholarship():
    with TestClient(app) as client:
        payload = {
            "profile": {
                "age": 20,
                "state": "Tamil Nadu",
                "student": True,
                "course": "engineering",
                "annual_income": 150000,
            },
            "query_text": "engineering student scholarship",
        }
        resp = client.post("/api/schemes/match", json=payload)
        assert resp.status_code == 200
        results = resp.json()
        scheme_ids = [r["scheme"]["scheme_id"] for r in results]
        assert "demo_edu_001" in scheme_ids


def test_match_farmer_scenario_excludes_unrelated_categories():
    with TestClient(app) as client:
        payload = {
            "profile": {
                "age": 45,
                "state": "Tamil Nadu",
                "occupation": "farmer",
                "land_ownership": "owned",
                "land_area_acres": 2,
                "annual_income": 200000,
            },
            "query_text": "farmer land government schemes",
        }
        resp = client.post("/api/schemes/match", json=payload)
        assert resp.status_code == 200
        results = resp.json()
        statuses = {r["eligibility"]["status"] for r in results}
        assert "not_matching" not in statuses


def teardown_module(module):
    for f in ("test_benefits_navigator.db",):
        if os.path.exists(f):
            try:
                os.remove(f)
            except PermissionError:
                pass
