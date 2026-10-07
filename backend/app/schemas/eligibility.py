from typing import Literal
from pydantic import BaseModel

EligibilityStatus = Literal[
    "likely_eligible",
    "possibly_eligible",
    "missing_information",
    "not_matching",
    "unable_to_determine",
]


class ConditionResult(BaseModel):
    field: str
    operator: str
    expected_value: object
    actual_value: object | None = None
    result: bool | None = None  # True/False/None(unknown)
    reason: str


class EligibilityResult(BaseModel):
    scheme_id: str
    status: EligibilityStatus
    matched_conditions: list[ConditionResult] = []
    failed_conditions: list[ConditionResult] = []
    missing_conditions: list[ConditionResult] = []
    explanation: str


class EligibilityCheckRequest(BaseModel):
    profile: dict
    scheme_id: str | None = None  # if omitted, check against all schemes
    language: str = "en"
