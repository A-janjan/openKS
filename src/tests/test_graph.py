from knowledge_graph.extraction import extract_entities_and_relations


def test_extract_entities_and_relations():
    text = "PostgreSQL implements MVCC."
    entities, relations = extract_entities_and_relations(text)
    # Should find entities: PostgreSQL, MVCC
    entity_names = [e["name"] for e in entities]
    assert (
        "PostgreSQL" in entity_names or "postgresql" in entity_names
    )  # case sensitive
    # Relations: PostgreSQL -> implements -> MVCC
    assert len(relations) > 0
    # Check relation
    rel = relations[0]
    assert rel["source"] == "PostgreSQL"
    assert rel["relation"] == "implement"
    assert rel["target"] == "MVCC"
