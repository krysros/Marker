"""Tests for marker/utils/website_autofill.py"""

from unittest.mock import MagicMock, patch

import pytest

from marker.utils.website_autofill import (
    _country_from_locale,
    _fold_text,
    _normalize_whitespace,
    _subdivision_code_from_value,
    company_autofill_from_website,
    contacts_autofill_from_website,
    project_autofill_from_website,
    tags_autofill_from_website,
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
    # Falls back to empty string when no ISO code found (raw state name would fail form validation)
    assert result.get("subdivision") == ""


def test_country_from_locale_bare_language():
    # 'pl' has likely subtag PL
    assert _country_from_locale("pl") == "PL"


def test_country_from_locale_with_territory():
    # 'pl_PL' already has territory
    assert _country_from_locale("pl_PL") == "PL"


def test_country_from_locale_empty():
    assert _country_from_locale("") == ""


def test_country_from_locale_invalid():
    assert _country_from_locale("zzz_invalid") == ""


def test_subdivision_code_partial_match():
    # Test that partial matching works (subdivision name contained in input)
    result = _subdivision_code_from_value("województwo mazowieckie", "PL")
    assert result == "PL-14"


@patch("marker.utils.website_autofill.location_details")
@patch("langchain_google_genai.ChatGoogleGenerativeAI.invoke")
@patch("langchain_community.document_loaders.WebBaseLoader.load")
def test_autofill_country_full_name_normalized(mock_loader, mock_llm, mock_geo):
    """LLM returns full country name (e.g. 'Poland') — should be normalized to alpha_2 'PL'."""
    mock_loader.return_value = [MagicMock(page_content="test page content")]
    mock_llm.return_value = MagicMock(
        content='{"name": "Co", "city": "Warsaw", "country": "Poland"}'
    )
    mock_geo.return_value = None
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake"}):
        result = company_autofill_from_website("https://example.com")
    assert result["country"] == "PL"


@patch("marker.utils.website_autofill.location_details")
@patch("langchain_google_genai.ChatGoogleGenerativeAI.invoke")
@patch("langchain_community.document_loaders.WebBaseLoader.load")
def test_autofill_country_empty_defaults_to_pl(mock_loader, mock_llm, mock_geo):
    """LLM returns no country — with explicit default_country='PL' should return 'PL'."""
    mock_loader.return_value = [MagicMock(page_content="test page content")]
    mock_llm.return_value = MagicMock(content='{"name": "Co", "city": "Warsaw"}')
    mock_geo.return_value = None
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake"}):
        result = company_autofill_from_website(
            "https://example.com", default_country="PL"
        )
    assert result["country"] == "PL"


@patch("marker.utils.website_autofill.location_details")
@patch("langchain_google_genai.ChatGoogleGenerativeAI.invoke")
@patch("langchain_community.document_loaders.WebBaseLoader.load")
def test_autofill_country_empty_no_default(mock_loader, mock_llm, mock_geo):
    """LLM returns no country and no default_country — should return empty string."""
    mock_loader.return_value = [MagicMock(page_content="test page content")]
    mock_llm.return_value = MagicMock(content='{"name": "Co", "city": "Warsaw"}')
    mock_geo.return_value = None
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake"}):
        result = company_autofill_from_website("https://example.com")
    assert result["country"] == ""


@patch("marker.utils.website_autofill.location_details")
@patch("langchain_google_genai.ChatGoogleGenerativeAI.invoke")
@patch("langchain_community.document_loaders.WebBaseLoader.load")
def test_autofill_country_lookup_error_defaults_to_pl(mock_loader, mock_llm, mock_geo):
    """LLM returns unrecognizable country and fuzzy search raises LookupError — falls back to default_country."""
    mock_loader.return_value = [MagicMock(page_content="test page content")]
    mock_llm.return_value = MagicMock(
        content='{"name": "Co", "country": "xyzzy_not_a_country"}'
    )
    mock_geo.return_value = None
    with patch("pycountry.countries.search_fuzzy", side_effect=LookupError):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "fake"}):
            result = company_autofill_from_website(
                "https://example.com", default_country="PL"
            )
    assert result["country"] == "PL"


def test_subdivision_code_fuzzy_contained_match():
    # Trigger the fuzzy "subdivision_folded in folded" branch (line 134)
    # "region mazowieckie area" doesn't match exactly but contains the subdivision name
    result = _subdivision_code_from_value("region mazowieckie area", "PL")
    assert result == "PL-14"


@patch("langchain_community.document_loaders.WebBaseLoader.load")
def test_autofill_empty_docs_raises(mock_loader):
    """Empty docs list should raise ValueError."""
    import marker.forms.ts as ts_mod

    mock_loader.return_value = []
    with patch.object(ts_mod.TranslationString, "__str__", lambda self: self.msg):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "fake"}):
            with pytest.raises(ValueError, match="Could not load content from"):
                company_autofill_from_website("https://empty.example.com")


@patch("marker.utils.website_autofill.location_details")
@patch("langchain_google_genai.ChatGoogleGenerativeAI.invoke")
@patch("langchain_community.document_loaders.WebBaseLoader.load")
def test_autofill_geo_provides_postcode(mock_loader, mock_llm, mock_geo):
    """Geo lookup provides postcode when result has none."""
    mock_loader.return_value = [MagicMock(page_content="test content")]
    mock_llm.return_value = MagicMock(content='{"name": "Co", "city": "Warsaw"}')
    mock_geo.return_value = {
        "country_code": "PL",
        "state": "Mazowieckie",
        "postcode": "00-001",
    }
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake"}):
        result = company_autofill_from_website("https://example.com")
    assert result["postcode"] == "00-001"


# ===========================================================================
# contacts_autofill_from_website
# ===========================================================================


def _make_loader_side_effect(*url_content_pairs):
    """Return a side_effect callable for WebBaseLoader class mock.

    *url_content_pairs* is a sequence of (url_fragment, content | Exception).
    Falls back to an Exception for unrecognised URLs.
    """
    call_count = {"n": 0}

    def factory(url):
        idx = call_count["n"]
        call_count["n"] += 1
        if idx < len(url_content_pairs):
            content_or_exc = url_content_pairs[idx]
        else:
            content_or_exc = Exception("unexpected call")

        instance = MagicMock()
        if isinstance(content_or_exc, Exception):
            instance.load.side_effect = content_or_exc
        else:
            instance.load.return_value = [MagicMock(page_content=content_or_exc)]
        return instance

    return factory


@patch("marker.utils.website_autofill.ChatGoogleGenerativeAI")
@patch("marker.utils.website_autofill.WebBaseLoader")
def test_contacts_autofill_list_result(mock_loader_class, mock_llm_class):
    """Happy path: main page + subpage load, LLM returns a list."""
    # Call 0: main page
    # Call 1: /kontakt fails → continue
    # Call 2: /contact returns > 200 chars → break
    long_content = "x" * 300
    mock_loader_class.side_effect = _make_loader_side_effect(
        "main page content",
        Exception("not found"),
        long_content,
    )

    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = MagicMock(
        content='[{"name": "Alice", "role": "CEO", "phone": "123", "email": "a@e.com"}]'
    )
    mock_llm_class.return_value = mock_llm_instance

    result = contacts_autofill_from_website("https://example.com")

    assert len(result) == 1
    assert result[0]["name"] == "Alice"


@patch("marker.utils.website_autofill.ChatGoogleGenerativeAI")
@patch("marker.utils.website_autofill.WebBaseLoader")
def test_contacts_autofill_dict_contacts_key(mock_loader_class, mock_llm_class):
    """LLM returns dict with 'contacts' key → unwrap it."""
    mock_loader_class.side_effect = _make_loader_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )

    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = MagicMock(
        content='{"contacts": [{"name": "Bob", "role": "CTO"}]}'
    )
    mock_llm_class.return_value = mock_llm_instance

    result = contacts_autofill_from_website("https://example.com")

    assert result[0]["name"] == "Bob"


@patch("marker.utils.website_autofill.ChatGoogleGenerativeAI")
@patch("marker.utils.website_autofill.WebBaseLoader")
def test_contacts_autofill_dict_people_key(mock_loader_class, mock_llm_class):
    """LLM returns dict with 'people' key → unwrap it."""
    mock_loader_class.side_effect = _make_loader_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )

    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = MagicMock(
        content='{"people": [{"name": "Carol", "role": "Dev"}]}'
    )
    mock_llm_class.return_value = mock_llm_instance

    result = contacts_autofill_from_website("https://example.com")

    assert result[0]["name"] == "Carol"


@patch("marker.utils.website_autofill.ChatGoogleGenerativeAI")
@patch("marker.utils.website_autofill.WebBaseLoader")
def test_contacts_autofill_dict_no_matching_key(mock_loader_class, mock_llm_class):
    """LLM returns dict with no recognised key → returns []."""
    mock_loader_class.side_effect = _make_loader_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )

    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = MagicMock(
        content='{"unknown_key": [{"name": "Nobody"}]}'
    )
    mock_llm_class.return_value = mock_llm_instance

    result = contacts_autofill_from_website("https://example.com")

    assert result == []


@patch("marker.forms.ts.get_current_request")
@patch("marker.utils.website_autofill.WebBaseLoader")
def test_contacts_autofill_all_loads_fail(mock_loader_class, mock_get_request):
    """All page loads fail → ValueError."""
    mock_req = MagicMock()
    mock_req.translate.side_effect = lambda msg: msg
    mock_get_request.return_value = mock_req

    instance = MagicMock()
    instance.load.side_effect = Exception("connection refused")
    mock_loader_class.return_value = instance

    with pytest.raises(ValueError):
        contacts_autofill_from_website("https://example.com")


@patch("marker.utils.website_autofill.ChatGoogleGenerativeAI")
@patch("marker.utils.website_autofill.WebBaseLoader")
def test_contacts_autofill_url_skip(mock_loader_class, mock_llm_class):
    """When website URL matches a contact sub-path, that path is skipped."""
    # website = "https://example.com/kontakt" → /kontakt sub-path will be skipped
    # Call 0: main page (https://example.com/kontakt) → main page content
    # Call 1: /contact → 404
    # Call 2-5: remaining paths → 404
    mock_loader_class.side_effect = _make_loader_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )

    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = MagicMock(
        content='[{"name": "Dave", "role": "PM"}]'
    )
    mock_llm_class.return_value = mock_llm_instance

    result = contacts_autofill_from_website("https://example.com/kontakt")

    assert result[0]["name"] == "Dave"


# ===========================================================================
# tags_autofill_from_website
# ===========================================================================


@patch("marker.utils.website_autofill.ChatGoogleGenerativeAI")
@patch("marker.utils.website_autofill.WebBaseLoader")
def test_tags_autofill_list_result(mock_loader_class, mock_llm_class):
    """Happy path: main page + subpage load, LLM returns a tag list."""
    long_content = "y" * 300
    mock_loader_class.side_effect = _make_loader_side_effect(
        "main page content",
        Exception("404"),
        long_content,
    )

    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = MagicMock(
        content='["Construction", "Real estate"]'
    )
    mock_llm_class.return_value = mock_llm_instance

    result = tags_autofill_from_website("https://example.com")

    assert "Construction" in result
    assert "Real estate" in result


@patch("marker.utils.website_autofill.ChatGoogleGenerativeAI")
@patch("marker.utils.website_autofill.WebBaseLoader")
def test_tags_autofill_with_existing_tags(mock_loader_class, mock_llm_class):
    """existing_tags are passed to the LLM prompt."""
    mock_loader_class.side_effect = _make_loader_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )

    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = MagicMock(content='["Construction"]')
    mock_llm_class.return_value = mock_llm_instance

    result = tags_autofill_from_website(
        "https://example.com",
        existing_tags=["Construction", "IT", "Finance"],
    )

    assert result == ["Construction"]
    # Verify the invoke call included the existing tags
    call_args = mock_llm_instance.invoke.call_args[0][0]
    assert "Construction" in call_args


@patch("marker.utils.website_autofill.ChatGoogleGenerativeAI")
@patch("marker.utils.website_autofill.WebBaseLoader")
def test_tags_autofill_dict_tags_key(mock_loader_class, mock_llm_class):
    """LLM returns dict with 'tags' key → unwrap it."""
    mock_loader_class.side_effect = _make_loader_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )

    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = MagicMock(
        content='{"tags": ["BIM", "Architecture"]}'
    )
    mock_llm_class.return_value = mock_llm_instance

    result = tags_autofill_from_website("https://example.com")

    assert "BIM" in result


@patch("marker.utils.website_autofill.ChatGoogleGenerativeAI")
@patch("marker.utils.website_autofill.WebBaseLoader")
def test_tags_autofill_dict_no_matching_key(mock_loader_class, mock_llm_class):
    """LLM returns dict with no recognised key → returns []."""
    mock_loader_class.side_effect = _make_loader_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )

    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = MagicMock(content='{"other": ["BIM"]}')
    mock_llm_class.return_value = mock_llm_instance

    result = tags_autofill_from_website("https://example.com")

    assert result == []


@patch("marker.forms.ts.get_current_request")
@patch("marker.utils.website_autofill.WebBaseLoader")
def test_tags_autofill_all_loads_fail(mock_loader_class, mock_get_request):
    """All page loads fail → ValueError."""
    mock_req = MagicMock()
    mock_req.translate.side_effect = lambda msg: msg
    mock_get_request.return_value = mock_req

    instance = MagicMock()
    instance.load.side_effect = Exception("connection refused")
    mock_loader_class.return_value = instance

    with pytest.raises(ValueError):
        tags_autofill_from_website("https://example.com")


@patch("marker.utils.website_autofill.ChatGoogleGenerativeAI")
@patch("marker.utils.website_autofill.WebBaseLoader")
def test_tags_autofill_url_skip(mock_loader_class, mock_llm_class):
    """When website URL matches a sub-path, that path is skipped."""
    # website = "https://example.com/oferta" → /oferta will be skipped
    mock_loader_class.side_effect = _make_loader_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )

    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = MagicMock(content='["Design"]')
    mock_llm_class.return_value = mock_llm_instance

    result = tags_autofill_from_website("https://example.com/oferta")

    assert result == ["Design"]
