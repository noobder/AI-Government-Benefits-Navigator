import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_localization.db")
os.environ.setdefault("SECRET_KEY", "test-secret")

from fastapi.testclient import TestClient

from app.main import app
from app.services.eligibility_service import evaluate_eligibility

RULES_AGE_60 = {"operator": "AND", "conditions": [{"field": "age", "operator": ">=", "value": 60}]}


def test_eligibility_explanation_is_localized_to_hindi():
    result = evaluate_eligibility("s1", RULES_AGE_60, {"age": 65}, language="hi")
    assert result.status == "likely_eligible"
    assert "पात्र" not in result.explanation or "पूरा" in result.explanation  # sanity: Devanagari text present
    assert any("ऀ" <= ch <= "ॿ" for ch in result.explanation)


def test_eligibility_explanation_is_localized_to_tamil():
    result = evaluate_eligibility("s1", RULES_AGE_60, {"age": 40}, language="ta")
    assert result.status == "not_matching"
    assert any("஀" <= ch <= "௿" for ch in result.explanation)


def test_eligibility_condition_reason_uses_translated_field_label():
    result = evaluate_eligibility("s1", RULES_AGE_60, {"age": 65}, language="en")
    assert "age" in result.matched_conditions[0].reason
    result_hi = evaluate_eligibility("s1", RULES_AGE_60, {"age": 65}, language="hi")
    assert "उम्र" in result_hi.matched_conditions[0].reason


def test_missing_condition_reason_localized():
    result = evaluate_eligibility("s1", RULES_AGE_60, {}, language="ta")
    assert result.status == "missing_information"
    assert "வழங்கப்படவில்லை" in result.missing_conditions[0].reason


def test_scheme_list_returns_hindi_translation():
    with TestClient(app) as client:
        resp = client.get("/api/schemes?language=hi")
        assert resp.status_code == 200
        schemes = {s["scheme_id"]: s for s in resp.json()}
        assert "[डेमो]" in schemes["demo_edu_001"]["scheme_name"]


def test_scheme_list_returns_tamil_translation():
    with TestClient(app) as client:
        resp = client.get("/api/schemes?language=ta")
        assert resp.status_code == 200
        schemes = {s["scheme_id"]: s for s in resp.json()}
        assert "[டெமோ]" in schemes["demo_agri_001"]["scheme_name"]


def test_scheme_falls_back_to_english_when_no_translation_field():
    with TestClient(app) as client:
        # English is always returned untouched regardless of translations present
        resp = client.get("/api/schemes?language=en")
        assert resp.status_code == 200
        schemes = {s["scheme_id"]: s for s in resp.json()}
        assert schemes["demo_edu_001"]["scheme_name"].startswith("[DEMO]")


def test_match_endpoint_localizes_recommendation():
    with TestClient(app) as client:
        payload = {
            "profile": {"age": 65, "annual_income": 90000},
            "query_text": "senior pension",
            "language": "hi",
        }
        resp = client.post("/api/schemes/match", json=payload)
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) > 0
        pension = next(r for r in results if r["scheme"]["scheme_id"] == "demo_senior_001")
        assert "पेंशन" in pension["scheme"]["scheme_name"] or "डेमो" in pension["scheme"]["scheme_name"]
        assert any("ऀ" <= ch <= "ॿ" for ch in pension["eligibility"]["explanation"])


def teardown_module(module):
    for f in ("test_localization.db",):
        if os.path.exists(f):
            try:
                os.remove(f)
            except PermissionError:
                pass
