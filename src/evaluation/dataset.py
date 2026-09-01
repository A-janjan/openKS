from typing import List, Dict, Set
from storage.database import SessionLocal
from storage.models import Document, Chunk


def get_chunk_ids_by_document_title(title: str) -> List[str]:
    """Return chunk IDs for a given document title."""
    db = SessionLocal()
    docs = db.query(Document).filter(Document.title == title).first()
    if not docs:
        db.close()
        return []
    chunk_ids = []
    for doc in docs:
        chunks = db.query(Chunk).filter(Chunk.document_id == doc.id).all()
        chunk_ids.extend([str(ch.id) for ch in chunks])
    db.close()
    return chunk_ids


# Define queries with document titles that are relevant
EVALUATION_QUERIES = [
    {
        "query": "How does the grift economy work?",
        "relevant_document_titles": [
            "text1.txt",
            "text2.md",
        ],  # both discuss the mechanics
        "expected_answer": "The grift economy is massive and participatory; people become unpaid distributors; it's a pyramid system.",
    },
    {
        "query": "What is the role of platforms in the grift economy?",
        "relevant_document_titles": [
            "text1.md",
            "text2.txt",
        ],  # platforms as enablers and RL systems
        "expected_answer": "Platforms detect vulnerability, optimise pitches, and use recommendation systems to extract fear and greed.",
    },
    {
        "query": "How do recommendation systems contribute to grift?",
        "relevant_document_titles": [
            "text2.txt"
        ],  # directly mentions RL loops and experiments on weakness
        "expected_answer": "Recommendation systems are reinforcement-learning loops that continuously experiment on human weakness to maximize attention and conversion.",
    },
]


def build_evaluation_dataset():
    """Resolve document titles to chunk IDs."""
    dataset = []
    for item in EVALUATION_QUERIES:
        relevant_ids = []
        for title in item.get("relevant_document_titles", []):
            ids = get_chunk_ids_by_document_title(title)
            relevant_ids.extend(ids)
        dataset.append(
            {
                "query": item["query"],
                "relevant_chunk_ids": relevant_ids,
                "expected_answer": item.get("expected_answer", ""),
            }
        )
    return dataset
