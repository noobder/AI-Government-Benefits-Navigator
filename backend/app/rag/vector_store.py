"""Vector store abstraction.

The default implementation (`KeywordVectorStore`) uses pure-Python TF-IDF-like
keyword scoring so the RAG pipeline works with zero external services or API
keys — important for a hackathon MVP. Swap in FaissVectorStore / ChromaStore
(stubs below) by setting a real EMBEDDING_PROVIDER once an API key is
available; nothing else in the app needs to change since callers only use
the VectorStore interface.
"""
from __future__ import annotations

import math
import re
from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)


TOKEN_RE = re.compile(r"[a-zA-Z஀-௿]+")


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]


class VectorStore(ABC):
    @abstractmethod
    def add(self, chunks: list[Chunk]) -> None: ...

    @abstractmethod
    def query(self, text: str, top_k: int = 5, metadata_filter: dict | None = None) -> list[tuple[Chunk, float]]: ...


class KeywordVectorStore(VectorStore):
    """A simple TF-IDF cosine-similarity store, no external dependencies."""

    def __init__(self):
        self._chunks: list[Chunk] = []
        self._doc_freq: Counter = Counter()

    def add(self, chunks: list[Chunk]) -> None:
        for c in chunks:
            self._chunks.append(c)
            for term in set(tokenize(c.text)):
                self._doc_freq[term] += 1

    def _score(self, query_terms: list[str], chunk: Chunk) -> float:
        chunk_terms = tokenize(chunk.text)
        if not chunk_terms:
            return 0.0
        chunk_tf = Counter(chunk_terms)
        n_docs = max(len(self._chunks), 1)
        score = 0.0
        for term in query_terms:
            tf = chunk_tf.get(term, 0)
            if tf == 0:
                continue
            df = self._doc_freq.get(term, 1)
            idf = math.log((n_docs + 1) / df) + 1
            score += tf * idf
        return score / math.sqrt(len(chunk_terms))

    def query(self, text: str, top_k: int = 5, metadata_filter: dict | None = None) -> list[tuple[Chunk, float]]:
        query_terms = tokenize(text)
        candidates = self._chunks
        if metadata_filter:
            candidates = [
                c for c in candidates
                if all(
                    (c.metadata.get(k) == v)
                    or (isinstance(c.metadata.get(k), list) and v in c.metadata.get(k))
                    or (v == "*")
                    for k, v in metadata_filter.items()
                )
            ]
        scored = [(c, self._score(query_terms, c)) for c in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def clear(self) -> None:
        self._chunks = []
        self._doc_freq = Counter()


class FaissVectorStore(VectorStore):
    """Placeholder for a real embedding-backed FAISS store.

    Not used unless EMBEDDING_PROVIDER=openai (or similar) is configured with
    a valid API key. Kept here to show the swap point requested by the
    architecture: retrieval code depends only on the VectorStore interface.
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "FaissVectorStore requires the 'faiss-cpu' package and an embedding API key. "
            "Install faiss-cpu and set EMBEDDING_PROVIDER accordingly to enable it."
        )

    def add(self, chunks: list[Chunk]) -> None:  # pragma: no cover
        raise NotImplementedError

    def query(self, text: str, top_k: int = 5, metadata_filter: dict | None = None):  # pragma: no cover
        raise NotImplementedError


_store_instance: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _store_instance
    if _store_instance is None:
        _store_instance = KeywordVectorStore()
    return _store_instance
