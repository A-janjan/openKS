import pytest
from ingestion.pipeline import chunking_text


def test_chunk_text():
    text = " ".join(["word"] * 1000)
    chunks = chunking_text(text, chunk_size=100, overlap=10)
    assert len(chunks) > 1
    # check overlap
    assert chunks[1].startswith("word")  # simple
