import math
from typing import List, Set


def recall_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    if not relevant_ids:
        return 0.0
    retrieved_set = set(retrieved_ids[:k])
    return len(retrieved_set & relevant_ids) / len(relevant_ids)


def mrr(retrieved_ids: List[str], relevant_ids: Set[str]) -> float:
    for rank, idx in enumerate(retrieved_ids, start=1):
        if idx in relevant_ids:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    if not relevant_ids:
        return 0.0
    # Compute DCG
    dcg = 0.0
    for i, idx in enumerate(retrieved_ids[:k], start=1):
        rel = 1.0 if idx in relevant_ids else 0.0
        dcg += rel / math.log2(i + 1)
    # Ideal DCG: all relevant at top
    ideal_relevance = [1.0] * min(len(relevant_ids), k) + [0.0] * (
        k - min(len(relevant_ids), k)
    )
    idcg = 0.0
    for i, rel in enumerate(ideal_relevance, start=1):
        idcg += rel / math.log2(i + 1)
    if idcg == 0:
        return 0.0
    return dcg / idcg
