from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.eligibility import EligibilityCheckRequest, EligibilityResult
from app.services import eligibility_service, scheme_service

router = APIRouter(prefix="/api/eligibility", tags=["eligibility"])


@router.post("/check", response_model=list[EligibilityResult])
def check_eligibility(payload: EligibilityCheckRequest, db: Session = Depends(get_db)):
    if payload.scheme_id:
        scheme = scheme_service.get_scheme(db, payload.scheme_id)
        if not scheme:
            raise HTTPException(status_code=404, detail="Scheme not found")
        schemes = [scheme]
    else:
        schemes = scheme_service.list_schemes(db)

    return [
        eligibility_service.evaluate_eligibility(s.id, s.eligibility_rules, payload.profile, payload.language)
        for s in schemes
    ]
