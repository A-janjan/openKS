from google import genai
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Initialize client once (reuse across calls)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_answer(query: str, context: str, citations: List[Dict]) -> str:
    """
    Generate a grounded answer using Gemini.

    Args:
        query: User question
        context: Retrieved text chunks (with citation markers)
        citations: List of citation metadata (optional, used for prompt)

    Returns:
        Generated answer as a string
    """
    model_name = "gemini-2.5-flash"  # or "gemini-2.5-pro"  (more capable)

    prompt = f"""
You are a knowledgeable assistant. Answer the question based solely on the provided context.
If the context doesn't contain the answer, say "I don't have enough information."

Context:
{context}

Question: {query}

Citations: {citations}

Provide a concise answer and list your sources (citations) at the end.
"""
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        return response.text or ""
    except Exception as e:
        # Log the error or re-raise with context
        raise RuntimeError(f"Generation failed: {e}")
