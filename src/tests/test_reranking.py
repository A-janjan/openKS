import pytest
from unittest.mock import patch, MagicMock
from retrieval.reranking import rerank

@patch("retrieval.reranking.get_reranker")
def test_rerank(mock_get_reranker):
    mock_model = MagicMock()
    mock_model.predict.return_value = [0.9, 0.3, 0.7]
    mock_get_reranker.return_value = mock_model

    candidates = [
        {"id": "1", "content": "foo"},
        {"id": "2", "content": "bar"},
        {"id": "3", "content": "baz"}
    ]
    result = rerank("query", candidates, top_k=2)
    assert len(result) == 2
    assert result[0]["id"] == "1"   # highest score
    assert "rerank_score" in result[0]