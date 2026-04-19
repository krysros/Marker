"""Tests for marker/utils/website_autofill.py"""

from unittest.mock import MagicMock, patch

import pytest

from marker.utils.website_autofill import (
    _fold_text,
    _normalize_whitespace,
    _subdivision_code_from_value,
    company_autofill_from_website,
    project_autofill_from_website,
)


def test_normalize_whitespace():
    assert _normalize_whitespace("  hello   world  ") == "hello world"
    assert _normalize_whitespace(None) == ""
    assert _normalize_whitespace("") == ""


def test_fold_text():
    assert _fold_text("Łódzkie") == "lodzkie"
    assert _fold_text("MAZOWIECKIE") == "mazowieckie"
    assert _fold_text("") == ""


def test_subdivision_code_from_value_empty():
    assert _subdivision_code_from_value("", "PL") == ""
    assert _subdivision_code_from_value("test", "") == ""


def test_subdivision_code_from_value_direct_match():
    result = _subdivision_code_from_value("PL-14", "PL")
    assert result == "PL-14"


def test_subdivision_code_from_value_by_name():
    result = _subdivision_code_from_value("Mazowieckie", "PL")
    assert result == "PL-14"


def test_subdivision_code_from_value_folded():
    result = _subdivision_code_from_value("łódzkie", "PL")
    assert result == "PL-10"


def test_subdivision_code_from_value_prefix_strip():
    result = _subdivision_code_from_value("woj. Mazowieckie", "PL")
    assert result == "PL-14"


def test_subdivision_code_from_value_not_found():
    result = _subdivision_code_from_value("Nonexistent", "PL")
    assert result == ""


@patch("marker.utils.website_autofill.location_details")
@patch("langchain_google_genai.ChatGoogleGenerativeAI.invoke")
@patch("langchain_community.document_loaders.WebBaseLoader.load")
def test_company_autofill_success(mock_loader, mock_llm, mock_geo):
    mock_loader.return_value = [MagicMock(page_content="test page content")]
    mock_llm.return_value = MagicMock(
        content='{"name": "TestCo", "street": "ul. Testowa 1", "postcode": "00-001", "city": "Warsaw"}'
    )
    mock_geo.return_value = {
        "country_code": "PL",
        "state": "Mazowieckie",
    }
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake"}):
        result = company_autofill_from_website("https://example.com")
    assert result["name"] == "TestCo"
    assert result["country"] == "PL"
    assert result["subdivision"] == "PL-14"


@patch("marker.utils.website_autofill.location_details")
@patch("langchain_google_genai.ChatGoogleGenerativeAI.invoke")
@patch("langchain_community.document_loaders.WebBaseLoader.load")
def test_project_autofill_success(mock_loader, mock_llm, mock_geo):
    mock_loader.return_value = [MagicMock(page_content="test page content")]
    mock_llm.return_value = MagicMock(
        content='{"name": "TestProject", "city": "Krakow"}'
    )
    mock_geo.return_value = None
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake"}):
        result = project_autofill_from_website("https://example.com")
    assert result["name"] == "TestProject"
    assert result["city"] == "Krakow"


@patch("langchain_community.document_loaders.WebBaseLoader.load")
def test_autofill_missing_api_key(mock_loader):
    mock_loader.return_value = [MagicMock(page_content="test page content")]
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError):
            company_autofill_from_website("https://example.com")


@patch("marker.utils.website_autofill.location_details")
@patch("langchain_google_genai.ChatGoogleGenerativeAI.invoke")
@patch("langchain_community.document_loaders.WebBaseLoader.load")
def test_autofill_no_street_prefix(mock_loader, mock_llm, mock_geo):
    mock_loader.return_value = [MagicMock(page_content="test page content")]
    mock_llm.return_value = MagicMock(
        content='{"name": "Co", "street": "Testowa 1", "city": "Warsaw"}'
    )
    mock_geo.return_value = None
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake"}):
        result = company_autofill_from_website("https://example.com")
    assert result["street"] == "Testowa 1"


@patch("marker.utils.website_autofill.location_details")
@patch("langchain_google_genai.ChatGoogleGenerativeAI.invoke")
@patch("langchain_community.document_loaders.WebBaseLoader.load")
def test_autofill_geo_no_subdivision_code(mock_loader, mock_llm, mock_geo):
    mock_loader.return_value = [MagicMock(page_content="test page content")]
    mock_llm.return_value = MagicMock(content='{"name": "Co", "city": "Unknown"}')
    mock_geo.return_value = {
        "country_code": "PL",
        "state": "NonexistentState",
    }
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake"}):
        result = company_autofill_from_website("https://example.com")
    # Falls back to state name when no ISO code found
    assert result.get("subdivision") == "NonexistentState"


def test_subdivision_code_partial_match():
    # Test that partial matching works (subdivision name contained in input)
    result = _subdivision_code_from_value("województwo mazowieckie", "PL")
    assert result == "PL-14"


def test_subdivision_code_fuzzy_contained_match():
    # Trigger the fuzzy "subdivision_folded in folded" branch (line 134)
    # "region mazowieckie area" doesn't match exactly but contains the subdivision name
    result = _subdivision_code_from_value("region mazowieckie area", "PL")
    assert result == "PL-14"
