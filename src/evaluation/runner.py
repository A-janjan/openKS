from typing import List, Dict, Any
from retrieval.search import bm25_search, vector_search, hybrid_search
from evaluation.dataset import build_evaluation_dataset
from evaluation.metrics import recall_at_k, mrr, ndcg_at_k
import logging

logging.basicConfig(level=logging.INFO)


def evaluate_retrieval(
    method: str, dataset: List[Dict], k_values: List[int] = [5, 10]
) -> Dict[str, float]:
    """
    method: 'bm25', 'vector', 'hybrid', 'hybrid_rerank'
    Returns dict of average metrics per k.
    """
    # Initialize accumulators
    metrics = {
        f"{metric}@{k}": [] for metric in ["recall", "mrr", "ndcg"] for k in k_values
    }
    # Add mrr@all (only one MRR per query, not per k)
    metrics["mrr"] = []

    for item in dataset:
        query = item["query"]
        relevant = set(item["relevant_chunk_ids"])
        if not relevant:
            logging.warning(f"No relevant chunks for query: {query}")
            continue

        # Retrieve based on method
        if method == "bm25":
            retrieved = bm25_search(query, limit=max(k_values) * 2)  # get enough
        elif method == "vector":
            retrieved = vector_search(query, limit=max(k_values) * 2)
        elif method == "hybrid":
            retrieved = hybrid_search(
                query, limit=max(k_values) * 2, use_reranker=False
            )
        elif method == "hybrid_rerank":
            retrieved = hybrid_search(query, limit=max(k_values) * 2, use_reranker=True)
        else:
            raise ValueError(f"Unknown method: {method}")

        retrieved_ids = [r["id"] for r in retrieved]

        # Compute per-query metrics
        for k in k_values:
            metrics[f"recall@{k}"].append(recall_at_k(retrieved_ids, relevant, k))
            # MRR is not per-k, but we can compute once per query
        metrics["mrr"].append(mrr(retrieved_ids, relevant))
        # NDCG per k
        for k in k_values:
            metrics[f"ndcg@{k}"].append(ndcg_at_k(retrieved_ids, relevant, k))

    # Average
    avg_results = {}
    for metric, values in metrics.items():
        if values:
            avg_results[metric] = sum(values) / len(values)
        else:
            avg_results[metric] = 0.0
    return avg_results


def run_all_experiments() -> Dict[str, Any]:
    dataset = build_evaluation_dataset()
    methods = ["bm25", "vector", "hybrid", "hybrid_rerank"]
    results = {}
    for method in methods:
        logging.info(f"Running evaluation for {method}")
        results[method] = evaluate_retrieval(method, dataset, k_values=[5, 10])
    return results


if __name__ == "__main__":
    # Run experiments and print results
    results = run_all_experiments()
    print("\n=== Retrieval Evaluation Results ===\n")
    for method, metrics in results.items():
        print(f"{method.upper()}:")
        for k in [5, 10]:
            print(f"  Recall@{k}: {metrics.get(f'recall@{k}', 0):.4f}")
            print(f"  NDCG@{k}:  {metrics.get(f'ndcg@{k}', 0):.4f}")
        print(f"  MRR:       {metrics.get('mrr', 0):.4f}")
        print()
