"""Conversational workflow.

Implemented as an explicit node chain over a typed ConversationState. This
mirrors a LangGraph StateGraph (UNDERSTAND -> EXTRACT -> CHECK_COMPLETENESS ->
[ASK | RETRIEVE] -> ELIGIBILITY -> RANK -> EVIDENCE -> EXPLAIN -> DOCUMENTS ->
APPLICATION_GUIDANCE -> END) without requiring the `langgraph` package as a
hard dependency, so the hackathon MVP runs with a minimal install. Swapping
this for a real LangGraph StateGraph is a drop-in change since each node is
already a pure function of ConversationState.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.graph.state import ConversationState
from app.services import eligibility_service, profile_service, ranking_service, rag_service, translation_service
from app.utils.logging import get_logger

logger = get_logger(__name__)


def node_understand_and_extract(state: ConversationState) -> ConversationState:
    try:
        state.newly_extracted = profile_service.extract_profile_from_text(state.user_query)
    except Exception:  # LLM/extraction failure must never crash the request
        logger.exception("Profile extraction failed; continuing with the profile already known.")
        state.newly_extracted = {}
    state.user_profile = profile_service.merge_profile(state.user_profile, state.newly_extracted)
    return state


def node_check_completeness(state: ConversationState, relevant_fields: set[str] | None = None) -> ConversationState:
    state.missing_fields = profile_service.detect_missing_fields(state.user_profile, relevant_fields)
    if state.missing_fields:
        state.follow_up_question = profile_service.get_follow_up_question(state.missing_fields[0], state.language)
    else:
        state.follow_up_question = None
    return state


def node_retrieve_schemes(db: Session, state: ConversationState) -> ConversationState:
    try:
        schemes = rag_service.retrieve_candidate_schemes(db, state.user_profile, state.user_query)
    except Exception:
        # RAG/retrieval failure: fall back to a plain structured scheme search
        # rather than hallucinating an answer (see app requirement: never
        # answer without grounded, verified scheme data).
        logger.exception("Scheme retrieval failed; falling back to structured search.")
        from app.services import scheme_service

        schemes = scheme_service.list_schemes(db, state=state.user_profile.get("state"))
    state.candidate_scheme_ids = [s.id for s in schemes]
    state.retrieved_evidence = [f"{s.scheme_name} ({s.source_name})" for s in schemes]
    return state


def node_evaluate_eligibility(db: Session, state: ConversationState) -> ConversationState:
    from app.services.scheme_service import get_scheme

    pairs = []
    for sid in state.candidate_scheme_ids:
        scheme = get_scheme(db, sid)
        if not scheme:
            continue
        result = eligibility_service.evaluate_eligibility(
            scheme.id, scheme.eligibility_rules, state.user_profile, state.language
        )
        if result.status == "not_matching":
            continue  # don't recommend schemes the user clearly doesn't match
        if result.status == "missing_information" and not result.matched_conditions:
            continue  # no confirmed overlap at all yet — too weak a signal to surface
        pairs.append((scheme, result))
    state.eligibility_results = ranking_service.rank_schemes(pairs)
    return state


def node_generate_response(state: ConversationState) -> str:
    if not state.eligibility_results:
        return translation_service.translate_phrase("no_schemes_found", state.language)
    return translation_service.translate_phrase(
        "eligible_intro", state.language, count=len(state.eligibility_results)
    )


def run_chat_workflow(db: Session, user_query: str, language: str, known_profile: dict) -> ConversationState:
    state = ConversationState(user_query=user_query, language=language, user_profile=dict(known_profile))

    state = node_understand_and_extract(state)
    state = node_retrieve_schemes(db, state)

    # Determine which fields actually matter for the retrieved candidates,
    # so we only ask about information relevant to this user's situation.
    from app.services.scheme_service import get_scheme

    relevant_fields: set[str] = set(profile_service.COMMONLY_REQUIRED_FIELDS)
    for sid in state.candidate_scheme_ids[:10]:
        scheme = get_scheme(db, sid)
        if scheme and scheme.eligibility_rules:
            for c in scheme.eligibility_rules.get("conditions", []):
                if "field" in c:
                    relevant_fields.add(c["field"])

    state = node_check_completeness(state, relevant_fields)
    state = node_evaluate_eligibility(db, state)
    state.final_response = node_generate_response(state)
    return state
