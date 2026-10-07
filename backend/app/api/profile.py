from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserProfileIn, UserProfileOut, UserProfilePatch
from app.services import profile_service

router = APIRouter(prefix="/api/profile", tags=["profile"])


class ExtractRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


@router.post("/extract")
def extract_profile(payload: ExtractRequest):
    """Turn a free-text description into structured profile fields, without
    running the full chat/eligibility pipeline — used by the "Fill with AI"
    assist on the guided profile form. Same extraction the chat assistant
    uses, so behavior (and its guarantees against fabricating values) is
    identical either way."""
    return profile_service.extract_profile_from_text(payload.text)


def _to_out(user: User) -> dict:
    fields = payload_fields = {
        c.name: getattr(user, c.name)
        for c in User.__table__.columns
        if c.name not in ("id", "created_at", "updated_at", "extra_attributes")
    }
    return {"id": user.id, **fields, "extra_attributes": user.extra_attributes or {}}


@router.post("", response_model=UserProfileOut)
def create_profile(payload: UserProfileIn, db: Session = Depends(get_db)):
    user = User(**payload.model_dump(exclude={"extra_attributes"}), extra_attributes=payload.extra_attributes)
    db.add(user)
    db.commit()
    db.refresh(user)
    return _to_out(user)


@router.get("/{user_id}", response_model=UserProfileOut)
def get_profile(user_id: str, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _to_out(user)


@router.patch("/{user_id}", response_model=UserProfileOut)
def patch_profile(user_id: str, payload: UserProfilePatch, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")
    known_columns = {c.name for c in User.__table__.columns}
    for k, v in payload.fields.items():
        if k in known_columns and k != "id":
            setattr(user, k, v)
        else:
            user.extra_attributes = {**(user.extra_attributes or {}), k: v}
    db.commit()
    db.refresh(user)
    return _to_out(user)
