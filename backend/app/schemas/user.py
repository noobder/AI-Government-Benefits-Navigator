from pydantic import BaseModel, Field, field_validator


class UserProfileIn(BaseModel):
    """Fields the user may provide. Nothing here is a sensitive identifier."""

    age: int | None = Field(default=None, ge=0, le=130)
    gender: str | None = None
    state: str | None = None
    district: str | None = None
    residence_type: str | None = None  # rural / urban
    occupation: str | None = None
    annual_income: float | None = Field(default=None, ge=0)
    education_level: str | None = None
    student: bool | None = None
    course: str | None = None
    previous_academic_percentage: float | None = Field(default=None, ge=0, le=100)
    family_size: int | None = Field(default=None, ge=1, le=50)
    land_ownership: str | None = None
    land_area_acres: float | None = Field(default=None, ge=0)
    employment_status: str | None = None
    disability_status: bool | None = None
    extra_attributes: dict = Field(default_factory=dict)
    language: str = "en"

    @field_validator("state", "district", "occupation", "education_level", "course", "land_ownership", "employment_status", "gender", mode="before")
    @classmethod
    def _strip_and_cap_strings(cls, v):
        if isinstance(v, str):
            v = v.strip()[:200]
            return v or None
        return v


class UserProfileOut(UserProfileIn):
    id: str


class UserProfilePatch(BaseModel):
    """Partial update, e.g. answering one missing-information question."""

    fields: dict = Field(default_factory=dict)
