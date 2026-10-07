import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Scheme(Base):
    """A government benefit scheme. Structured, verified data — never LLM-generated."""

    __tablename__ = "schemes"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # scheme_id from seed data
    scheme_name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String, index=True)
    ministry: Mapped[str | None] = mapped_column(String, nullable=True)
    department: Mapped[str | None] = mapped_column(String, nullable=True)
    level: Mapped[str] = mapped_column(String)  # Central / State
    applicable_states: Mapped[list] = mapped_column(JSON, default=list)
    target_beneficiaries: Mapped[list] = mapped_column(JSON, default=list)
    eligibility_rules: Mapped[dict] = mapped_column(JSON, default=dict)
    exclusions: Mapped[list] = mapped_column(JSON, default=list)
    benefits: Mapped[list] = mapped_column(JSON, default=list)
    required_documents: Mapped[list] = mapped_column(JSON, default=list)
    application_steps: Mapped[list] = mapped_column(JSON, default=list)
    official_url: Mapped[str] = mapped_column(String)
    source_url: Mapped[str] = mapped_column(String)
    source_name: Mapped[str] = mapped_column(String)
    last_verified: Mapped[str] = mapped_column(String)
    languages: Mapped[list] = mapped_column(JSON, default=list)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)

    # {"hi": {"scheme_name":..., "description":..., "benefits":[...],
    #  "required_documents":[...], "application_steps":[...]}, "ta": {...}}
    # Falls back to the English fields above for any language/field missing
    # here — see scheme_service.scheme_to_out_dict.
    translations: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )


class UserSchemeMatch(Base):
    __tablename__ = "user_scheme_matches"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    scheme_id: Mapped[str] = mapped_column(String, ForeignKey("schemes.id"))
    status: Mapped[str] = mapped_column(String)
    matched_conditions: Mapped[list] = mapped_column(JSON, default=list)
    failed_conditions: Mapped[list] = mapped_column(JSON, default=list)
    missing_conditions: Mapped[list] = mapped_column(JSON, default=list)
    explanation: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class SavedScheme(Base):
    __tablename__ = "saved_schemes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    scheme_id: Mapped[str] = mapped_column(String, ForeignKey("schemes.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
