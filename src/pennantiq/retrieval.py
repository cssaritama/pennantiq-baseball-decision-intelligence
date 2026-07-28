from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import settings

_DEFAULT_INDEX_CACHE = None


@dataclass
class Document:
    doc_id: str
    title: str
    text: str
    source: str


def _chunks(text: str, size: int = 850, overlap: int = 120):
    clean = re.sub(r"\s+", " ", text).strip()
    start = 0
    while start < len(clean):
        yield clean[start : start + size]
        start += max(1, size - overlap)


def load_documents(path: str | Path | None = None) -> list[Document]:
    root = settings.resolve(Path(path)) if path else settings.resolve(settings.knowledge_path)
    documents: list[Document] = []
    for file in sorted(root.glob("*.md")):
        text = file.read_text(encoding="utf-8")
        title = next(
            (line.lstrip("# ").strip() for line in text.splitlines() if line.startswith("#")),
            file.stem,
        )
        for index, chunk in enumerate(_chunks(text)):
            documents.append(
                Document(
                    f"{file.stem}:{index}",
                    title,
                    chunk,
                    str(file.relative_to(settings.root)),
                )
            )
    return documents


def rewrite_query(query: str) -> str:
    lower = query.strip().lower()
    replacements = {
        "best pitch": "pitch family and zone with strongest evidence",
        "beat": "reduce expected offensive damage against",
        "hot": "recent performance change",
        "why": "evidence and limitations for",
    }
    for source, target in replacements.items():
        lower = lower.replace(source, target)
    return lower


class Retriever:
    def __init__(self, docs: list[Document] | None = None):
        global _DEFAULT_INDEX_CACHE
        if docs is None and _DEFAULT_INDEX_CACHE is not None:
            self.docs, self.texts, self.vectorizer, self.matrix = _DEFAULT_INDEX_CACHE
            return

        self.docs = docs or load_documents()
        self.texts = [document.text for document in self.docs]
        self.vectorizer = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 2), min_df=1
        )
        self.matrix = self.vectorizer.fit_transform(self.texts) if self.texts else None

        if docs is None:
            _DEFAULT_INDEX_CACHE = (self.docs, self.texts, self.vectorizer, self.matrix)

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", text.lower())

    def keyword(self, query: str, k: int = 5):
        query_tokens = set(self._tokens(query))
        scored = []
        for document in self.docs:
            tokens = self._tokens(document.text)
            term_frequency = sum(1 for token in tokens if token in query_tokens)
            score = term_frequency / (math.sqrt(len(tokens)) + 1)
            scored.append((score, document))
        return sorted(scored, key=lambda item: item[0], reverse=True)[:k]

    def vector(self, query: str, k: int = 5):
        if self.matrix is None:
            return []
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix)[0]
        indexes = np.argsort(scores)[::-1][:k]
        return [(float(scores[index]), self.docs[index]) for index in indexes]

    def _hybrid_candidates(self, query: str, k: int):
        rewritten = rewrite_query(query)
        pool_size = max(k * 4, 12)
        keyword_scores = {
            document.doc_id: score
            for score, document in self.keyword(rewritten, k=pool_size)
        }
        vector_scores = {
            document.doc_id: score
            for score, document in self.vector(rewritten, k=pool_size)
        }
        by_id = {document.doc_id: document for document in self.docs}
        candidates = []
        for doc_id in set(keyword_scores) | set(vector_scores):
            score = 0.42 * keyword_scores.get(doc_id, 0.0) + 0.58 * vector_scores.get(doc_id, 0.0)
            candidates.append((score, by_id[doc_id]))
        return rewritten, sorted(candidates, key=lambda item: item[0], reverse=True)

    def hybrid(self, query: str, k: int = 5):
        _, candidates = self._hybrid_candidates(query, k)
        return candidates[:k]

    def hybrid_rerank(self, query: str, k: int = 5):
        rewritten, candidates = self._hybrid_candidates(query, k)
        query_tokens = set(self._tokens(rewritten))
        reranked = []
        for score, document in candidates[: max(k * 3, 10)]:
            title_overlap = len(query_tokens & set(self._tokens(document.title)))
            body_overlap = len(
                query_tokens & set(self._tokens(document.text[:350]))
            )
            rerank_score = score + 0.06 * title_overlap + 0.015 * body_overlap
            reranked.append((rerank_score, document))
        return sorted(reranked, key=lambda item: item[0], reverse=True)[:k]
    def best(self, query: str, k: int = 5):
        """Use the retrieval method selected by evaluation or RETRIEVAL_METHOD."""
        import json
        import os
        method = os.getenv("RETRIEVAL_METHOD", "").strip()
        if not method:
            result_path = settings.root / "evaluation" / "results" / "best_retrieval_method.json"
            if result_path.exists():
                try:
                    method = json.loads(result_path.read_text(encoding="utf-8"))["selected"]["method"]
                except Exception:
                    method = "hybrid_rerank"
            else:
                method = "hybrid_rerank"
        if method not in {"keyword", "vector", "hybrid", "hybrid_rerank"}:
            method = "hybrid_rerank"
        return getattr(self, method)(query, k=k)

