import pytest
from unittest.mock import patch, MagicMock
from generation.llm import generate_answer


@patch("generation.llm.client")
def test_generate_answer(mock_client):
    mock_response = MagicMock()
    mock_response.text = "Mocked answer."
    mock_client.models.generate_content.return_value = mock_response

    answer = generate_answer("query", "context", [])
    assert answer == "Mocked answer."
