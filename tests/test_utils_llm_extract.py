"""Tests for marker/utils/llm_extract.py"""

from unittest.mock import MagicMock, patch

import pytest

from marker.utils.llm_extract import extract_fields_llm


def test_extract_fields_llm_missing_api_key():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(RuntimeError, match="GEMINI_API_KEY is missing"):
            extract_fields_llm("<html></html>")


@patch("marker.utils.llm_extract.genai")
def test_extract_fields_llm_success(mock_genai):
    mock_response = MagicMock()
    mock_response.text = '{"name": "TestCo", "city": "Warsaw"}'
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    mock_genai.Client.return_value = mock_client

    result = extract_fields_llm("<html>test</html>", api_key="fake-key")
    assert result == {"name": "TestCo", "city": "Warsaw"}


@patch("marker.utils.llm_extract.genai")
def test_extract_fields_llm_rate_limit_429(mock_genai):
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("429 Too Many Requests")
    mock_genai.Client.return_value = mock_client

    with pytest.raises(RuntimeError, match="rate limit"):
        extract_fields_llm("<html></html>", api_key="fake-key")


@patch("marker.utils.llm_extract.genai")
def test_extract_fields_llm_resource_exhausted(mock_genai):
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception(
        "RESOURCE_EXHAUSTED: quota exceeded"
    )
    mock_genai.Client.return_value = mock_client

    with pytest.raises(RuntimeError, match="quota exceeded"):
        extract_fields_llm("<html></html>", api_key="fake-key")


@patch("marker.utils.llm_extract.genai")
def test_extract_fields_llm_model_not_found(mock_genai):
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("404 Model not found")
    mock_genai.Client.return_value = mock_client

    with pytest.raises(RuntimeError, match="not available"):
        extract_fields_llm("<html></html>", api_key="fake-key")


@patch("marker.utils.llm_extract.genai")
def test_extract_fields_llm_generic_exception(mock_genai):
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = ValueError("unknown error")
    mock_genai.Client.return_value = mock_client

    with pytest.raises(ValueError, match="unknown error"):
        extract_fields_llm("<html></html>", api_key="fake-key")


@patch("marker.utils.llm_extract.genai")
def test_extract_fields_llm_bad_json_response(mock_genai):
    mock_response = MagicMock()
    mock_response.text = "not json"
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    mock_genai.Client.return_value = mock_client

    with pytest.raises(RuntimeError, match="LLM response decode error"):
        extract_fields_llm("<html></html>", api_key="fake-key")
