from pydantic import BaseModel, Field

from app.schemas.eligibility import EligibilityResult
from app.schemas.scheme import SchemeOut


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    user_id: str | None = None
    language: str = "en"
    # profile fields accumulated so far in this conversation (client keeps this
    # or the server-stored profile identified by user_id is used)
    known_profile: dict = Field(default_factory=dict)


class RecommendedScheme(BaseModel):
    scheme: SchemeOut
    eligibility: EligibilityResult
    why_recommended: list[str]
    missing_information: list[str]
    documents: list[dict]  # {"name": str, "status": "required"|"possibly_required"}


class ChatResponse(BaseModel):
    reply_text: str
    language: str
    extracted_profile: dict
    missing_fields: list[str]
    follow_up_question: str | None = None
    recommendations: list[RecommendedScheme] = []
