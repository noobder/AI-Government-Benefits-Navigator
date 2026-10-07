from __future__ import annotations

from sqlalchemy.orm import Session

from app.rag.retriever import retrieve_scheme_ids
from app.services import scheme_service


def retrieve_candidate_schemes(db: Session, profile: dict, query_text: str = "") -> list:
    """Retrieve candidate Scheme rows relevant to the user's profile/query.

    Combines free-text semantic-ish retrieval with a state filter. Falls back
    to all schemes (still state-filtered) if the query yields nothing, so a
    guided-profile flow (no free text) still works.
    """
    state = profile.get("state")
    occupation_terms = " ".join(
        str(v) for k, v in profile.items() if k in ("occupation", "course", "education_level", "employment_status")
    )
    combined_query = f"{query_text} {occupation_terms}".strip()

    scheme_ids: list[str] = []
    if combined_query:
        scheme_ids = retrieve_scheme_ids(db, combined_query, state=state, top_k=8)

    if not scheme_ids:
        schemes = scheme_service.list_schemes(db, state=state)
        return schemes

    schemes = [scheme_service.get_scheme(db, sid) for sid in scheme_ids]
    return [s for s in schemes if s is not None]
