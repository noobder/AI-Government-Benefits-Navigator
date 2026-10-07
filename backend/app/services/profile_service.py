"""Converts natural-language user messages into a structured profile.

Uses the LLMProvider abstraction for extraction, but NEVER fabricates values:
only fields explicitly present (or clearly implied, e.g. "engineering
student" -> student=true, course=engineering) are set. Ambiguous statements
like "I farm on my uncle's land" must not be assumed to mean ownership.
"""
from __future__ import annotations

from app.i18n.strings import FIELD_QUESTIONS, translate
from app.services.llm_service import get_llm_provider

PROFILE_SCHEMA_HINT = (
    "age (int), gender (male/female), state, district, residence_type (rural/urban), "
    "occupation, annual_income (number in INR), education_level, student (bool), course, "
    "previous_academic_percentage (number), family_size (int), land_ownership "
    "(owned/leased/family/unknown), land_area_acres (number), employment_status, "
    "disability_status (bool)"
)

# Fields that at least one scheme in the demo dataset depends on; used to
# decide what to ask about next when a user's profile is incomplete.
COMMONLY_REQUIRED_FIELDS = [
    "age",
    "state",
    "annual_income",
    "occupation",
    "student",
]


_NUMBER_FIELDS = {"annual_income", "previous_academic_percentage", "land_area_acres"}
_INT_FIELDS = {"age", "family_size"}
_BOOL_FIELDS = {"student", "disability_status"}
_TEXT_FIELDS = {
    "gender", "state", "district", "residence_type", "occupation", "education_level",
    "course", "land_ownership", "employment_status",
}
PROFILE_FIELDS = _NUMBER_FIELDS | _INT_FIELDS | _BOOL_FIELDS | _TEXT_FIELDS


def _clean_value(field: str, value):
    """Coerce a provider-returned value to the field's expected type, or None if unusable."""
    if value is None or value == "":
        return None
    try:
        if field in _INT_FIELDS:
            return int(float(str(value).replace(",", "")))
        if field in _NUMBER_FIELDS:
            return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None
    if field in _BOOL_FIELDS:
        if isinstance(value, bool):
            return value
        if str(value).strip().lower() in {"true", "yes", "1"}:
            return True
        if str(value).strip().lower() in {"false", "no", "0"}:
            return False
        return None
    text = str(value).strip()
    return text.lower() if field in {"gender", "residence_type", "land_ownership"} and text else text or None


def extract_profile_from_text(text: str) -> dict:
    provider = get_llm_provider()
    extracted = provider.structured_output(text, PROFILE_SCHEMA_HINT)
    # Defensive: a real LLM may return unknown keys, nulls, or wrongly typed
    # values (e.g. "1,50,000" as a string) — keep only known, well-typed fields.
    cleaned = {k: _clean_value(k, v) for k, v in extracted.items() if k in PROFILE_FIELDS}
    return {k: v for k, v in cleaned.items() if v is not None}


def merge_profile(existing: dict, new_fields: dict) -> dict:
    merged = dict(existing)
    merged.update({k: v for k, v in new_fields.items() if v is not None})
    return merged


def detect_missing_fields(profile: dict, relevant_scheme_fields: set[str] | None = None) -> list[str]:
    """Return fields worth asking about next, prioritizing fields actually
    used by candidate schemes' eligibility rules over the generic list."""
    candidates = relevant_scheme_fields or set(COMMONLY_REQUIRED_FIELDS)
    return [f for f in candidates if profile.get(f) is None and f in FIELD_QUESTIONS]


def get_follow_up_question(field: str, language: str = "en") -> str:
    if field not in FIELD_QUESTIONS:
        return translate("generic_follow_up", language)
    return translate(field, language, FIELD_QUESTIONS)
