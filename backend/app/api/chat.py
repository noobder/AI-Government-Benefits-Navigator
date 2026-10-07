from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.graph.workflow import run_chat_workflow
from app.models.conversation import Conversation
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import ranking_service
from app.utils.logging import get_logger, safe_profile_for_logging

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = get_logger(__name__)


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    known_profile = dict(payload.known_profile)
    if payload.user_id:
        user = db.get(User, payload.user_id)
        if user:
            known_profile = {**user.to_profile_dict(), **known_profile}

    state = run_chat_workflow(db, payload.message, payload.language, known_profile)

    logger.info("chat query processed profile=%s candidates=%s", safe_profile_for_logging(state.user_profile), len(state.candidate_scheme_ids))

    recommendations = [
        ranking_service.build_recommendation(scheme, result, payload.language)
        for scheme, result in state.eligibility_results
    ]

    db.add(
        Conversation(
            user_id=payload.user_id,
            language=payload.language,
            user_query=payload.message,
            extracted_profile=state.newly_extracted,
            missing_fields=state.missing_fields,
            candidate_scheme_ids=state.candidate_scheme_ids,
            final_response=state.final_response,
        )
    )
    db.commit()

    if payload.user_id:
        user = db.get(User, payload.user_id)
        if user:
            for k, v in state.newly_extracted.items():
                if hasattr(user, k):
                    setattr(user, k, v)
            db.commit()

    return ChatResponse(
        reply_text=state.final_response,
        language=payload.language,
        extracted_profile=state.user_profile,
        missing_fields=state.missing_fields,
        follow_up_question=state.follow_up_question,
        recommendations=recommendations,
    )
