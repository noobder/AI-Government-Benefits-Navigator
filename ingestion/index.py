"""Write chunks + metadata into the vector store used by the backend."""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.rag.vector_store import Chunk, get_vector_store  # noqa: E402


def index_chunks(chunks_with_metadata: list[tuple[str, dict]]) -> int:
    store = get_vector_store()
    chunks = [
        Chunk(id=f"{meta.get('scheme_id', 'doc')}::{i}", text=text, metadata=meta)
        for i, (text, meta) in enumerate(chunks_with_metadata)
    ]
    store.add(chunks)
    return len(chunks)
