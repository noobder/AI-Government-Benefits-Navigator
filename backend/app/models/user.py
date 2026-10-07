import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    """An anonymous/temporary profile. No sensitive identifiers are stored."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)

    # Optional link to a login account — anonymous profiles (account_id is
    # null) are fully supported and remain the default; linking an account
    # only ever adds cross-device sync, it's never required.
    account_id: Mapped[str | None] = mapped_column(String, ForeignKey("accounts.id"), nullable=True)

    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String, nullable=True)
    state: Mapped[str | None] = mapped_column(String, nullable=True)
    district: Mapped[str | None] = mapped_column(String, nullable=True)
    residence_type: Mapped[str | None] = mapped_column(String, nullable=True)  # rural/urban
    occupation: Mapped[str | None] = mapped_column(String, nullable=True)
    annual_income: Mapped[float | None] = mapped_column(Float, nullable=True)
    education_level: Mapped[str | None] = mapped_column(String, nullable=True)
    student: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    course: Mapped[str | None] = mapped_column(String, nullable=True)
    previous_academic_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    family_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    land_ownership: Mapped[str | None] = mapped_column(String, nullable=True)  # owned/leased/family/unknown
    land_area_acres: Mapped[float | None] = mapped_column(Float, nullable=True)
    employment_status: Mapped[str | None] = mapped_column(String, nullable=True)
    disability_status: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # extra freeform bucket for scheme-specific attributes not in the fixed schema
    extra_attributes: Mapped[dict] = mapped_column(JSON, default=dict)

    language: Mapped[str] = mapped_column(String, default="en")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    def to_profile_dict(self) -> dict:
        """Return only non-null fields, merged with extra_attributes."""
        base = {
            "age": self.age,
            "gender": self.gender,
            "state": self.state,
            "district": self.district,
            "residence_type": self.residence_type,
            "occupation": self.occupation,
            "annual_income": self.annual_income,
            "education_level": self.education_level,
            "student": self.student,
            "course": self.course,
            "previous_academic_percentage": self.previous_academic_percentage,
            "family_size": self.family_size,
            "land_ownership": self.land_ownership,
            "land_area_acres": self.land_area_acres,
            "employment_status": self.employment_status,
            "disability_status": self.disability_status,
        }
        base = {k: v for k, v in base.items() if v is not None}
        base.update(self.extra_attributes or {})
        return base
