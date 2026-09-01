from generation.rag import build_context


def test_build_context():
    results = [{"content": "First chunk."}, {"content": "Second chunk."}]
    context = build_context(results)
    assert "[1] First chunk." in context
    assert "[2] Second chunk." in context
