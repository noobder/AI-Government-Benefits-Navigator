from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.scheme import SchemeOut
from app.services import eligibility_service, ranking_service, rag_service, scheme_service

router = APIRouter(prefix="/api/schemes", tags=["schemes"])


@router.get("", response_model=list[SchemeOut])
def get_schemes(
    category: str | None = None, state: str | None = None, language: str = "en", db: Session = Depends(get_db)
):
    schemes = scheme_service.list_schemes(db, category=category, state=state)
    return [scheme_service.scheme_to_out_dict(s, language) for s in schemes]


@router.get("/{scheme_id}", response_model=SchemeOut)
def get_scheme(scheme_id: str, language: str = "en", db: Session = Depends(get_db)):
    scheme = scheme_service.get_scheme(db, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme_service.scheme_to_out_dict(scheme, language)


class MatchRequest(BaseModel):
    profile: dict
    query_text: str = ""
    language: str = "en"


@router.post("/match")
def match_schemes(payload: MatchRequest, db: Session = Depends(get_db)):
    candidates = rag_service.retrieve_candidate_schemes(db, payload.profile, payload.query_text)
    pairs = []
    for scheme in candidates:
        result = eligibility_service.evaluate_eligibility(
            scheme.id, scheme.eligibility_rules, payload.profile, payload.language
        )
        if result.status == "not_matching":
            continue
        if result.status == "missing_information" and not result.matched_conditions:
            continue
        pairs.append((scheme, result))
    ranked = ranking_service.rank_schemes(pairs)
    return [ranking_service.build_recommendation(scheme, result, payload.language) for scheme, result in ranked]


class SaveRequest(BaseModel):
    user_id: str


@router.post("/{scheme_id}/save")
def save_scheme(scheme_id: str, payload: SaveRequest, db: Session = Depends(get_db)):
    scheme = scheme_service.get_scheme(db, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    if not db.get(User, payload.user_id):
        raise HTTPException(status_code=404, detail="User profile not found")
    saved = scheme_service.save_scheme_for_user(db, payload.user_id, scheme_id)
    return {"saved": True, "id": saved.id}
