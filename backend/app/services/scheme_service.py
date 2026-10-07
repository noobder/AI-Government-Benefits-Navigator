from __future__ import annotations

import json
import os

from sqlalchemy.orm import Session

from app.models.scheme import Scheme, SavedScheme, UserSchemeMatch
from app.config import get_settings


def load_seed_schemes() -> list[dict]:
    settings = get_settings()
    configured = settings.seed_data_path

    if os.path.isabs(configured):
        candidates = [configured]
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            # backend/app/services/../../../data/seed_schemes.json -> repo_root/data/...
            os.path.normpath(os.path.join(here, "..", "..", configured)),
            # fallback: relative to the current working directory (e.g. Docker
            # image where only backend/ is copied and data/ is mounted separately)
            os.path.normpath(os.path.join(os.getcwd(), configured)),
        ]

    for path in candidates:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

    raise FileNotFoundError(
        f"Could not find seed scheme data. Tried: {candidates}. "
        "Set SEED_DATA_PATH to an absolute path if running in a container."
    )


def seed_database(db: Session) -> int:
    """Idempotently load seed schemes into the DB. Returns count inserted/updated."""
    schemes = load_seed_schemes()
    count = 0
    for s in schemes:
        existing = db.get(Scheme, s["scheme_id"])
        if existing:
            row = existing
        else:
            row = Scheme(id=s["scheme_id"])
            db.add(row)
        row.scheme_name = s["scheme_name"]
        row.description = s["description"]
        row.category = s["category"]
        row.ministry = s.get("ministry")
        row.department = s.get("department")
        row.level = s["level"]
        row.applicable_states = s.get("applicable_states", [])
        row.target_beneficiaries = s.get("target_beneficiaries", [])
        row.eligibility_rules = s.get("eligibility_rules", {})
        row.exclusions = s.get("exclusions", [])
        row.benefits = s.get("benefits", [])
        row.required_documents = s.get("required_documents", [])
        row.application_steps = s.get("application_steps", [])
        row.official_url = s["official_url"]
        row.source_url = s["source_url"]
        row.source_name = s["source_name"]
        row.last_verified = s["last_verified"]
        row.languages = s.get("languages", [])
        row.is_demo = s.get("is_demo", True)
        row.translations = s.get("translations", {})
        count += 1
    db.commit()
    return count


def list_schemes(db: Session, category: str | None = None, state: str | None = None) -> list[Scheme]:
    query = db.query(Scheme)
    if category:
        query = query.filter(Scheme.category == category)
    schemes = query.all()
    if state:
        schemes = [
            s for s in schemes if "All States" in s.applicable_states or state in s.applicable_states
        ]
    return schemes


def get_scheme(db: Session, scheme_id: str) -> Scheme | None:
    return db.get(Scheme, scheme_id)


def save_scheme_for_user(db: Session, user_id: str, scheme_id: str) -> SavedScheme:
    existing = (
        db.query(SavedScheme)
        .filter(SavedScheme.user_id == user_id, SavedScheme.scheme_id == scheme_id)
        .first()
    )
    if existing:
        return existing
    row = SavedScheme(user_id=user_id, scheme_id=scheme_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def record_match(db: Session, user_id: str, result) -> UserSchemeMatch:
    row = UserSchemeMatch(
        user_id=user_id,
        scheme_id=result.scheme_id,
        status=result.status,
        matched_conditions=[c.model_dump() for c in result.matched_conditions],
        failed_conditions=[c.model_dump() for c in result.failed_conditions],
        missing_conditions=[c.model_dump() for c in result.missing_conditions],
        explanation=result.explanation,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def scheme_to_out_dict(s: Scheme, language: str = "en") -> dict:
    """Structured scheme facts never come from the LLM — only which language
    they're phrased in varies. `translations[language]` overrides individual
    text fields (scheme_name, description, benefits, required_documents,
    application_steps) when present; anything not translated falls back to
    the English field, so a partially-translated scheme still renders
    completely rather than showing blanks."""
    tr = (s.translations or {}).get(language, {}) if language != "en" else {}
    return {
        "scheme_id": s.id,
        "scheme_name": tr.get("scheme_name", s.scheme_name),
        "description": tr.get("description", s.description),
        "category": s.category,
        "ministry": s.ministry,
        "department": s.department,
        "level": s.level,
        "applicable_states": s.applicable_states,
        "target_beneficiaries": s.target_beneficiaries,
        "benefits": tr.get("benefits", s.benefits),
        "required_documents": tr.get("required_documents", s.required_documents),
        "application_steps": tr.get("application_steps", s.application_steps),
        "official_url": s.official_url,
        "source_url": s.source_url,
        "source_name": s.source_name,
        "last_verified": s.last_verified,
        "languages": s.languages,
        "is_demo": s.is_demo,
    }


def scheme_to_admin_out_dict(s: Scheme, language: str = "en") -> dict:
    return {**scheme_to_out_dict(s, language), "eligibility_rules": s.eligibility_rules, "exclusions": s.exclusions}


def create_scheme(db: Session, payload) -> Scheme:
    """payload: schemas.scheme.SchemeIn. Raises ValueError if scheme_id already exists."""
    if db.get(Scheme, payload.scheme_id):
        raise ValueError(f"A scheme with id '{payload.scheme_id}' already exists.")
    row = Scheme(id=payload.scheme_id, **payload.model_dump(exclude={"scheme_id"}))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_scheme(db: Session, scheme_id: str, payload) -> Scheme | None:
    """payload: schemas.scheme.SchemeUpdate. Only provided fields are changed."""
    row = db.get(Scheme, scheme_id)
    if not row:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row


def delete_scheme(db: Session, scheme_id: str) -> bool:
    row = db.get(Scheme, scheme_id)
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True
