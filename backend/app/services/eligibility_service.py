"""Deterministic eligibility engine.

This is intentionally NOT LLM-based. Eligibility is decided by evaluating
structured rules (see data/seed_schemes.json `eligibility_rules`) against
the user's profile. The LLM is never consulted here.

Rule shape (arbitrarily nestable):
    {"operator": "AND"|"OR", "conditions": [ <leaf-or-group>, ... ]}
    leaf:  {"field": str, "operator": "=="|"!="|">"|">="|"<"|"<="|"IN"|"NOT_IN", "value": Any}
    group: {"operator": "AND"|"OR", "conditions": [...]}

Evaluation uses three-valued logic (True / False / None-for-missing) so that
"we don't know yet" is never silently collapsed into "not eligible".

Every explanation sentence is built from app/i18n/strings.py templates, so
the same evaluation logic produces a fully localized explanation in
whichever language the caller asks for — the *decision* is language
independent, only the phrasing around it is translated.
"""
from __future__ import annotations

from app.i18n.strings import CONDITION_TEMPLATES, bool_label, field_label, translate
from app.schemas.eligibility import ConditionResult, EligibilityResult

OPERATORS = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    "IN": lambda a, b: a in b,
    "NOT_IN": lambda a, b: a not in b,
}


def _display(value: object, language: str) -> str:
    if isinstance(value, bool):
        return bool_label(value, language)
    if isinstance(value, list):
        return ", ".join(_display(v, language) for v in value)
    return str(value)


def _evaluate_leaf(condition: dict, profile: dict, language: str) -> ConditionResult:
    field = condition["field"]
    operator = condition["operator"]
    expected = condition["value"]
    actual = profile.get(field)
    label = field_label(field, language)

    if actual is None:
        return ConditionResult(
            field=field,
            operator=operator,
            expected_value=expected,
            actual_value=None,
            result=None,
            reason=translate("condition_missing", language, CONDITION_TEMPLATES, field=label),
        )

    if operator not in OPERATORS:
        return ConditionResult(
            field=field,
            operator=operator,
            expected_value=expected,
            actual_value=actual,
            result=None,
            reason=translate("unknown_operator", language, CONDITION_TEMPLATES, field=label, operator=operator),
        )

    try:
        # normalize simple string case-insensitivity for equality/IN checks
        cmp_actual = actual
        cmp_expected = expected
        if isinstance(actual, str) and isinstance(expected, str):
            cmp_actual, cmp_expected = actual.lower(), expected.lower()
        elif isinstance(actual, str) and isinstance(expected, list):
            cmp_actual = actual.lower()
            cmp_expected = [v.lower() if isinstance(v, str) else v for v in expected]

        result = bool(OPERATORS[operator](cmp_actual, cmp_expected))
    except TypeError:
        return ConditionResult(
            field=field,
            operator=operator,
            expected_value=expected,
            actual_value=actual,
            result=None,
            reason=translate("condition_uncomparable", language, CONDITION_TEMPLATES, field=label),
        )

    template_key = "condition_met" if result else "condition_not_met"
    reason = translate(
        template_key,
        language,
        CONDITION_TEMPLATES,
        field=label,
        value=_display(actual, language),
        operator=operator,
        expected=_display(expected, language),
    )

    return ConditionResult(
        field=field, operator=operator, expected_value=expected, actual_value=actual, result=result, reason=reason
    )


def _evaluate_group(
    group: dict, profile: dict, language: str
) -> tuple[bool | None, list[ConditionResult], list[ConditionResult], list[ConditionResult]]:
    """Recursively evaluate a (possibly nested) AND/OR group.

    Returns (tri-state result, matched, failed, missing) with the leaf
    ConditionResults collected across the whole subtree, for a flat,
    explainable breakdown in the UI.
    """
    logic = str(group.get("operator", "AND")).upper()
    items = group.get("conditions", [])

    matched: list[ConditionResult] = []
    failed: list[ConditionResult] = []
    missing: list[ConditionResult] = []
    child_results: list[bool | None] = []

    for item in items:
        if "field" in item:
            leaf = _evaluate_leaf(item, profile, language)
            child_results.append(leaf.result)
            if leaf.result is True:
                matched.append(leaf)
            elif leaf.result is False:
                failed.append(leaf)
            else:
                missing.append(leaf)
        elif "conditions" in item:
            sub_result, sub_matched, sub_failed, sub_missing = _evaluate_group(item, profile, language)
            child_results.append(sub_result)
            matched.extend(sub_matched)
            failed.extend(sub_failed)
            missing.extend(sub_missing)

    if not child_results:
        return None, matched, failed, missing

    if logic == "OR":
        if any(r is True for r in child_results):
            overall = True
        elif any(r is None for r in child_results):
            overall = None
        else:
            overall = False
    else:  # AND (default)
        if any(r is False for r in child_results):
            overall = False
        elif any(r is None for r in child_results):
            overall = None
        else:
            overall = True

    return overall, matched, failed, missing


def evaluate_eligibility(scheme_id: str, eligibility_rules: dict, profile: dict, language: str = "en") -> EligibilityResult:
    """Evaluate a scheme's eligibility_rules against a user profile.

    Returns a transparent, explainable result — never an arbitrary percentage.
    `language` only affects the phrasing of `reason`/`explanation`; the
    decision itself is computed identically regardless of language.
    """
    if not eligibility_rules or not eligibility_rules.get("conditions"):
        return EligibilityResult(
            scheme_id=scheme_id,
            status="unable_to_determine",
            explanation=translate("status_no_rules", language, CONDITION_TEMPLATES),
        )

    overall, matched, failed, missing = _evaluate_group(eligibility_rules, profile, language)

    if overall is True:
        status = "likely_eligible"
        explanation = translate("status_likely_eligible", language, CONDITION_TEMPLATES)
    elif overall is False:
        status = "not_matching"
        explanation = translate("status_not_matching", language, CONDITION_TEMPLATES)
    else:
        status = "missing_information"
        key = "status_missing_with_matches" if matched else "status_missing_no_matches"
        explanation = translate(key, language, CONDITION_TEMPLATES)

    explanation += " " + translate("final_authority_note", language, CONDITION_TEMPLATES)

    return EligibilityResult(
        scheme_id=scheme_id,
        status=status,
        matched_conditions=matched,
        failed_conditions=failed,
        missing_conditions=missing,
        explanation=explanation,
    )
