from __future__ import annotations

import math
import os
import re
from collections import Counter
from collections.abc import Iterable

from huggingface_hub import InferenceClient

from app.data import RUNBOOKS
from app.models import Evidence


TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> Counter[str]:
    return Counter(TOKEN_RE.findall(text.lower()))


def _cosine(left: Iterable[float], right: Iterable[float]) -> float:
    left_values = list(left)
    right_values = list(right)
    numerator = sum(a * b for a, b in zip(left_values, right_values, strict=False))
    left_norm = math.sqrt(sum(value * value for value in left_values))
    right_norm = math.sqrt(sum(value * value for value in right_values))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


def _lexical_score(query: str, document: str) -> float:
    query_tokens = _tokens(query)
    document_tokens = _tokens(document)
    vocabulary = sorted(set(query_tokens) | set(document_tokens))
    return _cosine(
        (query_tokens[token] for token in vocabulary),
        (document_tokens[token] for token in vocabulary),
    )


class RunbookRetriever:
    """Semantic retrieval through Hugging Face, with a no-key local fallback."""

    def __init__(self) -> None:
        self.token = os.getenv("HF_TOKEN")
        self.model = os.getenv(
            "HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )

    def _hf_vectors(self, texts: list[str]) -> list[list[float]]:
        client = InferenceClient(api_key=self.token)
        vectors = client.feature_extraction(texts, model=self.model)
        return [list(map(float, vector)) for vector in vectors]

    def search(self, query: str, limit: int = 2) -> list[Evidence]:
        documents = [f"{item['title']}. {item['content']}" for item in RUNBOOKS]
        scores: list[float]
        if self.token:
            try:
                vectors = self._hf_vectors([query, *documents])
                scores = [_cosine(vectors[0], vector) for vector in vectors[1:]]
            except Exception:
                scores = [_lexical_score(query, document) for document in documents]
        else:
            scores = [_lexical_score(query, document) for document in documents]

        ranked = sorted(zip(RUNBOOKS, scores, strict=True), key=lambda item: item[1], reverse=True)
        return [
            Evidence(
                id=item["id"],
                source="runbook",
                content=f"{item['title']}: {item['content']}",
                score=round(score, 4),
            )
            for item, score in ranked[:limit]
        ]

