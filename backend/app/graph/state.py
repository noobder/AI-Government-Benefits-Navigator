from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConversationState:
    """Structured state threaded through the chat workflow graph."""

    user_query: str = ""
    language: str = "en"
    user_profile: dict = field(default_factory=dict)
    newly_extracted: dict = field(default_factory=dict)
    missing_fields: list[str] = field(default_factory=list)
    follow_up_question: str | None = None
    candidate_scheme_ids: list[str] = field(default_factory=list)
    eligibility_results: list = field(default_factory=list)  # list[tuple[Scheme, EligibilityResult]]
    retrieved_evidence: list[str] = field(default_factory=list)
    final_response: str = ""
