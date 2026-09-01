from google import genai
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Initialize client once (reuse across calls)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_answer(query: str, context_chunks: List[Dict]) -> str:
    """
    context_chunks: list of dicts with 'content' and optionally 'document_id'.
    Returns answer with citations like [1], [2].
    """
    # Build numbered context
    numbered_context = ""
    for i, chunk in enumerate(context_chunks, 1):
        numbered_context += f"[{i}] {chunk['content']}\n\n"

    prompt = f"""
You are a knowledgeable assistant. Answer the question based **only** on the provided context.
If the context does not contain the answer, say "I don't have enough information."

Use citations like [1], [2] to reference the source numbers provided in the context.
Cite only the most relevant sources (maximum 3-5). Do not repeat citations.

Context:
{numbered_context}

Question: {query}

Answer (with citations):
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text or ""
    except Exception as e:
        raise RuntimeError(f"Generation failed: {e}")


# generation/llm.py
def verify_grounding(query: str, answer: str, context: str) -> Dict:
    """Returns {'grounded': bool, 'explanation': str}."""
    prompt = f"""
You are a fact-checker. Given the query, the answer, and the context, determine if the answer is fully supported by the context.
- If all claims are supported, output "true".
- If any claim is not supported, output "false".
- Provide a brief explanation.

Query: {query}
Answer: {answer}
Context: {context}

Supported? (true/false):
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    text = (response.text or "").strip().lower()
    if "true" in text[:10]:
        return {"grounded": True, "explanation": text}
    else:
        return {"grounded": False, "explanation": text}
