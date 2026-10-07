from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.i18n.strings import translate
from app.models.scheme import SavedScheme
from app.models.user import User
from app.services import eligibility_service, rag_service, scheme_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/{user_id}")
def get_dashboard(user_id: str, language: str = "en", db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = user.to_profile_dict()
    candidates = rag_service.retrieve_candidate_schemes(db, profile)

    likely_eligible = []
    needs_info = []
    for scheme in candidates:
        result = eligibility_service.evaluate_eligibility(scheme.id, scheme.eligibility_rules, profile, language)
        if result.status in ("likely_eligible", "possibly_eligible"):
            likely_eligible.append(scheme.id)
        elif result.status == "missing_information":
            needs_info.append(scheme.id)

    saved = db.query(SavedScheme).filter(SavedScheme.user_id == user_id).all()

    recommended_actions = []
    if needs_info:
        recommended_actions.append(translate("dashboard_action_complete_profile", language))
    if likely_eligible:
        recommended_actions.append(translate("dashboard_action_review_eligible", language))
    if not likely_eligible and not needs_info:
        recommended_actions.append(translate("dashboard_action_tell_more", language))

    return {
        "likely_eligible_count": len(likely_eligible),
        "needs_verification_count": len(needs_info),
        "saved_count": len(saved),
        "likely_eligible_scheme_ids": likely_eligible,
        "needs_verification_scheme_ids": needs_info,
        "saved_scheme_ids": [s.scheme_id for s in saved],
        "recommended_actions": recommended_actions,
    }
