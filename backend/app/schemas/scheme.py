from pydantic import BaseModel, Field


class SchemeOut(BaseModel):
    scheme_id: str
    scheme_name: str
    description: str
    category: str
    ministry: str | None = None
    department: str | None = None
    level: str
    applicable_states: list[str] = []
    target_beneficiaries: list[str] = []
    benefits: list[str] = []
    required_documents: list[str] = []
    application_steps: list[str] = []
    official_url: str
    source_url: str
    source_name: str
    last_verified: str
    languages: list[str] = []
    is_demo: bool = True

    class Config:
        from_attributes = True


class SchemeAdminOut(SchemeOut):
    """Adds the fields only an admin needs to see: the raw eligibility rule
    tree and exclusions, which the public API intentionally omits."""

    eligibility_rules: dict = {}
    exclusions: list[str] = []
    translations: dict = {}


class SchemeIn(BaseModel):
    """Full payload to create a new scheme. scheme_id is a stable slug, not
    auto-generated, so admins can reference it predictably."""

    scheme_id: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_\-]+$")
    scheme_name: str = Field(min_length=1, max_length=300)
    description: str = ""
    category: str
    ministry: str | None = None
    department: str | None = None
    level: str = "State"
    applicable_states: list[str] = []
    target_beneficiaries: list[str] = []
    eligibility_rules: dict = {}
    exclusions: list[str] = []
    benefits: list[str] = []
    required_documents: list[str] = []
    application_steps: list[str] = []
    official_url: str = ""
    source_url: str = ""
    source_name: str = ""
    last_verified: str = ""
    languages: list[str] = ["en"]
    is_demo: bool = True
    translations: dict = {}


class SchemeUpdate(BaseModel):
    """Every field optional — only fields provided are changed (PATCH-style)."""

    scheme_name: str | None = None
    description: str | None = None
    category: str | None = None
    ministry: str | None = None
    department: str | None = None
    level: str | None = None
    applicable_states: list[str] | None = None
    target_beneficiaries: list[str] | None = None
    eligibility_rules: dict | None = None
    exclusions: list[str] | None = None
    benefits: list[str] | None = None
    required_documents: list[str] | None = None
    application_steps: list[str] | None = None
    official_url: str | None = None
    source_url: str | None = None
    source_name: str | None = None
    last_verified: str | None = None
    languages: list[str] | None = None
    is_demo: bool | None = None
    translations: dict | None = None
