from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services import help_assistant_service

router = APIRouter(prefix="/api/help", tags=["help"])


class HelpAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    language: str = "en"


@router.post("/ask")
def ask(payload: HelpAskRequest):
    return help_assistant_service.answer_question(payload.question, payload.language)


@router.get("/tutorial")
def tutorial(language: str = "en"):
    return help_assistant_service.get_tutorial(language)
