from retrieval.search import hybrid_search
from generation.llm import generate_answer
from typing import List, Dict


def build_context(results: List[Dict], max_tokens: int = 3000) -> str:
    """Concatenate chunk contents, preserving order and source info."""
    # Group by document to avoid redundancy, but for simplicity we just concatenate
    context = ""
    for i, res in enumerate(results):
        context += f"[{i+1}] {res['content']}\n\n"
    return context


def answer_query(query: str, limit: int = 5) -> Dict:
    """Full RAG pipeline: retrieve, build context, generate answer."""
    # 1. Retrieve top chunks
    results = hybrid_search(query, limit=limit)
    # 2. Build context
    context = build_context(results)
    # 3. Generate answer with LLM
    answer = generate_answer(
        query, context, results
    )  # we'll handle citations in LLM prompt
    # 4. Return answer and sources
    return {
        "query": query,
        "answer": answer,
        "citations": results,  # we can extract from answer or provide raw
    }
