from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.scheme import Scheme
from app.rag.vector_store import Chunk, VectorStore, get_vector_store

_indexed = False


def _scheme_to_chunks(s: Scheme) -> list[Chunk]:
    metadata = {
        "scheme_id": s.id,
        "scheme_name": s.scheme_name,
        "category": s.category,
        "states": s.applicable_states,
        "ministry": s.ministry,
        "source": s.source_name,
        "document_name": f"{s.scheme_name} - official scheme record",
        "last_verified": s.last_verified,
    }
    chunks = [
        Chunk(id=f"{s.id}::overview", text=f"{s.scheme_name}. {s.description}", metadata={**metadata, "section": "overview"}),
        Chunk(
            id=f"{s.id}::beneficiaries",
            text=f"Target beneficiaries: {', '.join(s.target_beneficiaries)}. Benefits: {', '.join(s.benefits)}.",
            metadata={**metadata, "section": "beneficiaries"},
        ),
        Chunk(
            id=f"{s.id}::documents",
            text=f"Required documents: {', '.join(s.required_documents)}.",
            metadata={**metadata, "section": "documents"},
        ),
    ]
    return chunks


def build_index(db: Session, store: VectorStore | None = None, force: bool = False) -> int:
    """Index all schemes in the DB into the vector store. Idempotent per process."""
    global _indexed
    store = store or get_vector_store()
    if _indexed and not force:
        return 0
    if hasattr(store, "clear"):
        store.clear()
    schemes = db.query(Scheme).all()
    total_chunks = 0
    for s in schemes:
        chunks = _scheme_to_chunks(s)
        store.add(chunks)
        total_chunks += len(chunks)
    _indexed = True
    return total_chunks


def retrieve_scheme_ids(
    db: Session, query_text: str, state: str | None = None, category: str | None = None, top_k: int = 10
) -> list[str]:
    """Retrieve candidate scheme_ids relevant to a free-text query, optionally
    filtered by state (falls back to 'All States' schemes automatically)."""
    build_index(db)
    store = get_vector_store()

    metadata_filter = {}
    if category:
        metadata_filter["category"] = category

    results = store.query(query_text, top_k=top_k * 3, metadata_filter=metadata_filter or None)

    seen: dict[str, float] = {}
    for chunk, score in results:
        sid = chunk.metadata["scheme_id"]
        states = chunk.metadata.get("states", [])
        if state and states and "All States" not in states and state not in states:
            continue
        seen[sid] = max(seen.get(sid, 0.0), score)

    ranked = sorted(seen.items(), key=lambda x: x[1], reverse=True)
    return [sid for sid, _ in ranked[:top_k]]
