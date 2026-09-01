from retrieval.search import hybrid_search
from generation.llm import generate_answer, verify_grounding
from typing import List, Dict
import re


def build_context(results: List[Dict], max_tokens: int = 3000) -> str:
    """Concatenate chunk contents, preserving order and source info."""
    # Group by document to avoid redundancy, but for simplicity we just concatenate
    context = ""
    for i, res in enumerate(results):
        context += f"[{i+1}] {res['content']}\n\n"
    return context


def extract_citations(answer: str) -> List[int]:
    """Find all citation numbers like [1], [2] in the answer."""
    pattern = r"\[(\d+)\]"
    return [int(match) for match in re.findall(pattern, answer)]


def answer_query(query: str, limit: int = 10) -> Dict:
    results = hybrid_search(query, limit=limit)
    answer_text = generate_answer(query, results)
    
    citation_numbers = extract_citations(answer_text)
    cited_chunks = []
    seen_ids = set()
    for num in citation_numbers:
        idx = num - 1
        if 0 <= idx < len(results):
            chunk = results[idx]
            if chunk["id"] not in seen_ids:
                seen_ids.add(chunk["id"])
                cited_chunks.append(chunk)
                

    # Now call grounding check (see below)
    context = build_context(results)  # or use the numbered context from LLM
    grounding = verify_grounding(query, answer_text, context)
    
    return {
        "query": query,
        "answer": answer_text,
        "citations": cited_chunks,
        "grounded": grounding["grounded"],
        "explanation": grounding["explanation"]
    }
