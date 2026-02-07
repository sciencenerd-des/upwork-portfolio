"""Lightweight extractive summarization utilities."""

from __future__ import annotations

from collections import Counter

from src.text_processor import sentence_split, tokenize


def generate_summary(text: str, max_sentences: int = 4) -> str:
    sentences = sentence_split(text)
    if not sentences:
        return "No summary available."
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    frequencies = Counter(tokenize(text))
    sentence_scores: list[tuple[int, float]] = []

    for index, sentence in enumerate(sentences):
        words = tokenize(sentence)
        if not words:
            continue
        score = sum(frequencies[word] for word in words) / len(words)
        sentence_scores.append((index, score))

    ranked = sorted(sentence_scores, key=lambda item: item[1], reverse=True)[:max_sentences]
    selected_indices = sorted(index for index, _ in ranked)
    return " ".join(sentences[index] for index in selected_indices)


def key_points(text: str, max_points: int = 6) -> list[str]:
    sentences = sentence_split(text)
    if not sentences:
        return ["No key points extracted."]

    summary_sentences = sentence_split(generate_summary(text, max_sentences=max_points))
    trimmed = [sentence.rstrip(".") for sentence in summary_sentences if sentence.strip()]
    return trimmed[:max_points]
