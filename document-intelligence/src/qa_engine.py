"""Question answering based on retrieved document chunks."""

from __future__ import annotations

from src.text_processor import sentence_split, tokenize
from src.vector_store import retrieve_chunks


def answer_question(question: str, chunks: list[str]) -> dict[str, object]:
    retrieval = retrieve_chunks(chunks, question, top_k=3)
    if not retrieval:
        return {
            "answer": "I could not find enough evidence in the uploaded document to answer that question.",
            "sources": [],
            "confidence": 0.0,
        }

    query_tokens = set(tokenize(question))
    best_sentences: list[str] = []

    for hit in retrieval:
        for sentence in sentence_split(hit.text):
            sentence_tokens = set(tokenize(sentence))
            if query_tokens.intersection(sentence_tokens):
                best_sentences.append(sentence)
            if len(best_sentences) >= 2:
                break
        if len(best_sentences) >= 2:
            break

    if not best_sentences:
        best_sentences = [retrieval[0].text[:320].strip()]

    sources = [f"Chunk {item.chunk_id}" for item in retrieval]
    confidence = max(min(retrieval[0].score + 0.15, 0.99), 0.45)

    return {
        "answer": " ".join(best_sentences),
        "sources": sources,
        "confidence": round(confidence, 2),
    }
