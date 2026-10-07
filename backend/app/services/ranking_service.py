"""Explainable scheme ranking.

Ranking is based on transparent, listed factors — never an arbitrary
"97% match" score. Each recommendation carries a plain-language reason.
"""
from __future__ import annotations

from app.i18n.strings import field_label
from app.models.scheme import Scheme
from app.schemas.eligibility import EligibilityResult

STATUS_WEIGHT = {
    "likely_eligible": 3,
    "possibly_eligible": 2,
    "missing_information": 1,
    "unable_to_determine": 0,
    "not_matching": -1,
}


def rank_schemes(pairs: list[tuple[Scheme, EligibilityResult]]) -> list[tuple[Scheme, EligibilityResult]]:
    """Sort by: eligibility status weight, then number of matched conditions,
    then fewer missing conditions (more profile-complete matches first)."""

    def key(pair: tuple[Scheme, EligibilityResult]):
        _, result = pair
        return (
            STATUS_WEIGHT.get(result.status, -2),
            len(result.matched_conditions),
            -len(result.missing_conditions),
        )

    return sorted(pairs, key=key, reverse=True)


_WHY_TEMPLATE = {
    "en": "Your {field} matches the requirement.",
    "hi": "आपकी {field} आवश्यकता से मेल खाती है।",
    "ta": "உங்கள் {field} தேவையுடன் பொருந்துகிறது.",
}
_CATEGORY_TEMPLATE = {
    "en": "This scheme falls under the {category} category.",
    "hi": "यह योजना {category} श्रेणी के अंतर्गत आती है।",
    "ta": "இந்தத் திட்டம் {category} வகையின் கீழ் வரும்.",
}
_MISSING_TEMPLATE = {
    "en": "We need your {field} to fully determine eligibility.",
    "hi": "पात्रता पूरी तरह तय करने के लिए हमें आपकी {field} चाहिए।",
    "ta": "தகுதியை முழுமையாகத் தீர்மானிக்க உங்கள் {field} தேவை.",
}


def build_why_recommended(scheme: Scheme, result: EligibilityResult, language: str = "en") -> list[str]:
    why_tpl = _WHY_TEMPLATE.get(language, _WHY_TEMPLATE["en"])
    cat_tpl = _CATEGORY_TEMPLATE.get(language, _CATEGORY_TEMPLATE["en"])
    reasons = [why_tpl.format(field=field_label(c.field, language)) for c in result.matched_conditions]
    if scheme.category:
        reasons.append(cat_tpl.format(category=scheme.category))
    return reasons


def build_missing_information(result: EligibilityResult, language: str = "en") -> list[str]:
    tpl = _MISSING_TEMPLATE.get(language, _MISSING_TEMPLATE["en"])
    return [tpl.format(field=field_label(c.field, language)) for c in result.missing_conditions]


def build_document_checklist(scheme: Scheme, result: EligibilityResult, language: str = "en") -> list[dict]:
    """Documents are only ever sourced from the verified scheme record. The
    'status' communicates confidence, not invented certainty."""
    status = "required" if result.status in ("likely_eligible", "possibly_eligible") else "possibly_required"
    from app.services.scheme_service import scheme_to_out_dict

    documents = scheme_to_out_dict(scheme, language)["required_documents"]
    return [{"name": doc, "status": status} for doc in documents]


def build_recommendation(scheme: Scheme, result: EligibilityResult, language: str = "en") -> dict:
    from app.services.scheme_service import scheme_to_out_dict

    return {
        "scheme": scheme_to_out_dict(scheme, language),
        "eligibility": result.model_dump(),
        "why_recommended": build_why_recommended(scheme, result, language),
        "missing_information": build_missing_information(result, language),
        "documents": build_document_checklist(scheme, result, language),
    }
