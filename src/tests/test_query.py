from query.understanding import classify_intent, extract_entities


def test_classify_intent():
    assert classify_intent("difference between A and B") == "comparison"
    assert classify_intent("what is X?") == "definition"
    assert classify_intent("why does X fail?") == "troubleshooting"
    assert classify_intent("how does X work?") == "multi-hop"
    assert classify_intent("tell me about X") == "exploration"


def test_extract_entities():
    # spaCy needs model; we can mock or test with a simple string but requires download.
    # For CI, we can skip or use a small model.
    # We'll test that it returns a list.
    entities = extract_entities("Apple is a company in California.")
    # We don't assert specific labels because spaCy may vary, but ensure non-empty.
    assert len(entities) > 0
