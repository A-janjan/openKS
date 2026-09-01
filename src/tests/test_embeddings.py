import pytest
from unittest.mock import patch, MagicMock
from ingestion.embeddings import get_embedding

@patch("ingestion.embeddings.client")
def test_get_embedding(mock_client):
    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=[0.1]*768)]
    mock_client.models.embed_content.return_value = mock_response
    emb = get_embedding("test")
    assert len(emb) == 768
    assert isinstance(emb, list)