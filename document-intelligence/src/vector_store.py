"""In-memory retrieval helper for Q&A."""

from __future__ import annotations

from dataclasses import dataclass

from src.text_processor import tokenize


@dataclass(slots=True)
class ChunkScore:
    chunk_id: int
    text: str
    score: float


def retrieve_chunks(chunks: list[str], query: str, top_k: int = 3) -> list[ChunkScore]:
    query_tokens = set(tokenize(query))
    if not query_tokens:
        return []

    scored: list[ChunkScore] = []
    for idx, chunk in enumerate(chunks):
        chunk_tokens = set(tokenize(chunk))
        if not chunk_tokens:
            continue

        overlap = query_tokens.intersection(chunk_tokens)
        if not overlap:
            continue

        lexical = len(overlap) / max(len(query_tokens), 1)
        density = len(overlap) / max(len(chunk_tokens), 1)
        score = round((lexical * 0.75) + (density * 0.25), 4)
        scored.append(ChunkScore(chunk_id=idx + 1, text=chunk, score=score))

    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:top_k]
