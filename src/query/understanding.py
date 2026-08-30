import spacy
from typing import List, Dict

nlp = spacy.load("en_core_web_sm")

INTENT_KEYWORDS = {
    "comparison": ["difference", "compare", "versus", "vs", "contrast"],
    "definition": ["what is", "define", "meaning", "what does", "explain"],
    "troubleshooting": ["why", "error", "fail", "problem", "issue", "not working"],
    "multi-hop": ["which", "how does", "what causes", "lead to", "result in"],
    # default will be "factual" or "exploration"
}


def extract_entities(query: str) -> List[Dict]:
    """Return list of entities with text, label, and optionally type."""
    doc = nlp(query)
    entities = []
    for ent in doc.ents:
        entities.append(
            {
                "text": ent.text,
                "label": ent.label_,  # e.g., ORG, PERSON, PRODUCT
            }
        )
    # Also extract noun chunks (potential concepts)
    for chunk in doc.noun_chunks:
        # Avoid duplicates with named entities
        if not any(chunk.text == e["text"] for e in entities):
            entities.append(
                {
                    "text": chunk.text,
                    "label": "CONCEPT",  # generic
                }
            )
    return entities


def classify_intent(query: str) -> str:
    """Return one of the predefined intents."""
    query_lower = query.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in query_lower:
                return intent
    # If no match, check for question words
    if query_lower.startswith(("what", "how", "why", "when", "where")):
        return "factual"
    return "exploration"


def analyze_query(query: str) -> Dict:
    """Full analysis: intent, entities, tokenized words."""
    return {
        "original_query": query,
        "intent": classify_intent(query),
        "entities": extract_entities(query),
        "tokens": [token.text for token in nlp(query) if not token.is_stop and not token.is_punct]
    }

