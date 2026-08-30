# knowledge_graph/extraction.py
import spacy
from typing import List, Tuple, Dict
from storage.models import Entity, Relationship

nlp = spacy.load("en_core_web_sm")


def extract_entities_and_relations(text: str) -> Tuple[List[Dict], List[Dict]]:
    doc = nlp(text)
    entities = []
    # Named entities
    for ent in doc.ents:
        entities.append({"name": ent.text, "type": ent.label_})
    # Also add noun chunks as "CONCEPT" if not already present
    for chunk in doc.noun_chunks:
        if not any(e["name"] == chunk.text for e in entities):
            entities.append({"name": chunk.text, "type": "CONCEPT"})

    # Relation extraction: simple SVO pattern
    relations = []
    for token in doc:
        if token.dep_ in ("nsubj", "nsubjpass") and token.head.pos_ == "VERB":
            subject = token.text
            verb = token.head.lemma_
            # Find object (direct object)
            for child in token.head.children:
                if child.dep_ in ("dobj", "attr", "prep"):
                    obj = child.text
                    relations.append(
                        {"source": subject, "relation": verb, "target": obj}
                    )
                    break  # take first object
    return entities, relations
