from app.services.eligibility_service import evaluate_eligibility

RULES_AGE_60 = {"operator": "AND", "conditions": [{"field": "age", "operator": ">=", "value": 60}]}


def test_age_above_threshold_is_eligible():
    result = evaluate_eligibility("s1", RULES_AGE_60, {"age": 65})
    assert result.status == "likely_eligible"


def test_age_below_threshold_is_not_matching():
    result = evaluate_eligibility("s1", RULES_AGE_60, {"age": 40})
    assert result.status == "not_matching"


def test_missing_age_is_missing_information_not_not_eligible():
    result = evaluate_eligibility("s1", RULES_AGE_60, {})
    assert result.status == "missing_information"
    assert result.status != "not_matching"


def test_and_logic_all_conditions_required():
    rules = {
        "operator": "AND",
        "conditions": [
            {"field": "student", "operator": "==", "value": True},
            {"field": "annual_income", "operator": "<=", "value": 200000},
        ],
    }
    eligible = evaluate_eligibility("s2", rules, {"student": True, "annual_income": 150000})
    assert eligible.status == "likely_eligible"

    not_eligible = evaluate_eligibility("s2", rules, {"student": True, "annual_income": 500000})
    assert not_eligible.status == "not_matching"

    partial = evaluate_eligibility("s2", rules, {"student": True})
    assert partial.status == "missing_information"


def test_in_operator_state_list():
    rules = {"operator": "AND", "conditions": [{"field": "state", "operator": "IN", "value": ["Tamil Nadu", "Kerala"]}]}
    assert evaluate_eligibility("s3", rules, {"state": "Tamil Nadu"}).status == "likely_eligible"
    assert evaluate_eligibility("s3", rules, {"state": "Punjab"}).status == "not_matching"


def test_no_rules_returns_unable_to_determine():
    result = evaluate_eligibility("s4", {}, {"age": 30})
    assert result.status == "unable_to_determine"


def test_nested_and_or_groups_evaluate_correctly():
    # (age >= 60) AND (state IN [Tamil Nadu, Kerala] OR disability_status == true)
    rules = {
        "operator": "AND",
        "conditions": [
            {"field": "age", "operator": ">=", "value": 60},
            {
                "operator": "OR",
                "conditions": [
                    {"field": "state", "operator": "IN", "value": ["Tamil Nadu", "Kerala"]},
                    {"field": "disability_status", "operator": "==", "value": True},
                ],
            },
        ],
    }
    # Satisfies age, and satisfies the OR via disability even though state doesn't match
    eligible = evaluate_eligibility("s5", rules, {"age": 65, "state": "Punjab", "disability_status": True})
    assert eligible.status == "likely_eligible"

    # Satisfies age, fails both OR branches
    not_eligible = evaluate_eligibility("s5", rules, {"age": 65, "state": "Punjab", "disability_status": False})
    assert not_eligible.status == "not_matching"

    # Satisfies age, OR branch state unknown and disability unknown -> missing, not a false negative
    missing = evaluate_eligibility("s5", rules, {"age": 65})
    assert missing.status == "missing_information"
