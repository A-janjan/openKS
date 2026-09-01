from sentence_transformers import CrossEncoder
from typing import List, Dict

# Load once at module import (or lazy load)
_reranker = None


def get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")
    return _reranker


def rerank(query: str, candidates: List[Dict], top_k: int = 10) -> List[Dict]:
    """
    candidates: list of dicts with at least 'content' key.
    Returns top_k candidates with added 'rerank_score'.
    """
    if not candidates:
        return []

    model = get_reranker()
    # Prepare pairs: (query, candidate content)
    pairs = [(query, cand["content"]) for cand in candidates]
    scores = model.predict(pairs)

    for cand, score in zip(candidates, scores):
        cand["rerank_score"] = float(score)

    sorted_candidates = sorted(
        candidates, key=lambda x: x["rerank_score"], reverse=True
    )
    return sorted_candidates[:top_k]
