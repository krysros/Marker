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
@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_company_autofill_success(mock_load, mock_gemini, mock_geo):
    mock_load.return_value = "test page content"
    mock_gemini.return_value = {
        "name": "TestCo",
        "street": "ul. Testowa 1",
        "postcode": "00-001",
        "city": "Warsaw",
    }
    mock_geo.return_value = {
        "country_code": "PL",
        "state": "Mazowieckie",
    }
    result = company_autofill_from_website("https://example.com")
    assert result["name"] == "TestCo"
    assert result["country"] == "PL"
    assert result["subdivision"] == "PL-14"


@patch("marker.utils.website_autofill.location_details")
@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_project_autofill_success(mock_load, mock_gemini, mock_geo):
    mock_load.return_value = "test page content"
    mock_gemini.return_value = {"name": "TestProject", "city": "Krakow"}
    mock_geo.return_value = None
    result = project_autofill_from_website("https://example.com")
    assert result["name"] == "TestProject"
    assert result["city"] == "Krakow"


@patch(
    "marker.utils.website_autofill._gemini_json",
    side_effect=ValueError("API key not configured"),
)
@patch(
    "marker.utils.website_autofill._load_page_content", return_value="test page content"
)
def test_autofill_missing_api_key(mock_load, mock_gemini):
    with pytest.raises(ValueError):
        company_autofill_from_website("https://example.com")


@patch("marker.utils.website_autofill.location_details")
@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_autofill_no_street_prefix(mock_load, mock_gemini, mock_geo):
    mock_load.return_value = "test page content"
    mock_gemini.return_value = {"name": "Co", "street": "Testowa 1", "city": "Warsaw"}
    mock_geo.return_value = None
    result = company_autofill_from_website("https://example.com")
    assert result["street"] == "Testowa 1"


@patch("marker.utils.website_autofill.location_details")
@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_autofill_geo_no_subdivision_code(mock_load, mock_gemini, mock_geo):
    mock_load.return_value = "test page content"
    mock_gemini.return_value = {"name": "Co", "city": "Unknown"}
    mock_geo.return_value = {
        "country_code": "PL",
        "state": "NonexistentState",
    }
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
@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_autofill_country_full_name_normalized(mock_load, mock_gemini, mock_geo):
    """LLM returns full country name (e.g. 'Poland') — should be normalized to alpha_2 'PL'."""
    mock_load.return_value = "test page content"
    mock_gemini.return_value = {"name": "Co", "city": "Warsaw", "country": "Poland"}
    mock_geo.return_value = None
    result = company_autofill_from_website("https://example.com")
    assert result["country"] == "PL"


@patch("marker.utils.website_autofill.location_details")
@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_autofill_country_empty_defaults_to_pl(mock_load, mock_gemini, mock_geo):
    """LLM returns no country — with explicit default_country='PL' should return 'PL'."""
    mock_load.return_value = "test page content"
    mock_gemini.return_value = {"name": "Co", "city": "Warsaw"}
    mock_geo.return_value = None
    result = company_autofill_from_website("https://example.com", default_country="PL")
    assert result["country"] == "PL"


@patch("marker.utils.website_autofill.location_details")
@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_autofill_country_empty_no_default(mock_load, mock_gemini, mock_geo):
    """LLM returns no country and no default_country — should return empty string."""
    mock_load.return_value = "test page content"
    mock_gemini.return_value = {"name": "Co", "city": "Warsaw"}
    mock_geo.return_value = None
    result = company_autofill_from_website("https://example.com")
    assert result["country"] == ""


@patch("marker.utils.website_autofill.location_details")
@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_autofill_country_lookup_error_defaults_to_pl(mock_load, mock_gemini, mock_geo):
    """LLM returns unrecognizable country and fuzzy search raises LookupError — falls back to default_country."""
    mock_load.return_value = "test page content"
    mock_gemini.return_value = {"name": "Co", "country": "xyzzy_not_a_country"}
    mock_geo.return_value = None
    with patch("pycountry.countries.search_fuzzy", side_effect=LookupError):
        result = company_autofill_from_website(
            "https://example.com", default_country="PL"
        )
    assert result["country"] == "PL"


def test_subdivision_code_fuzzy_contained_match():
    # Trigger the fuzzy "subdivision_folded in folded" branch (line 134)
    # "region mazowieckie area" doesn't match exactly but contains the subdivision name
    result = _subdivision_code_from_value("region mazowieckie area", "PL")
    assert result == "PL-14"


@patch("marker.utils.website_autofill._load_page_content", return_value="")
def test_autofill_empty_docs_raises(mock_load):
    """Empty content should raise ValueError."""
    import marker.forms.ts as ts_mod

    with patch.object(ts_mod.TranslationString, "__str__", lambda self: self.msg):
        with pytest.raises(ValueError, match="Could not load content from"):
            company_autofill_from_website("https://empty.example.com")


@patch("marker.utils.website_autofill.location_details")
@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_autofill_geo_provides_postcode(mock_load, mock_gemini, mock_geo):
    """Geo lookup provides postcode when result has none."""
    mock_load.return_value = "test content"
    mock_gemini.return_value = {"name": "Co", "city": "Warsaw"}
    mock_geo.return_value = {
        "country_code": "PL",
        "state": "Mazowieckie",
        "postcode": "00-001",
    }
    result = company_autofill_from_website("https://example.com")
    assert result["postcode"] == "00-001"


# ===========================================================================
# contacts_autofill_from_website
# ===========================================================================


def _make_load_page_side_effect(*items):
    """Return a side_effect function for patching _load_page_content.

    Each item can be a string (returned as content) or an Exception (raised).
    """
    queue = list(items)

    def side_effect(url):
        if queue:
            item = queue.pop(0)
        else:
            item = Exception("unexpected call")
        if isinstance(item, Exception):
            raise item
        return item

    return side_effect


@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_contacts_autofill_list_result(mock_load, mock_gemini):
    """Happy path: main page + subpage load, LLM returns a list."""
    # Call 0: main page
    # Call 1: /kontakt fails → continue
    # Call 2: /contact returns > 200 chars → break
    long_content = "x" * 300
    mock_load.side_effect = _make_load_page_side_effect(
        "main page content",
        Exception("not found"),
        long_content,
    )
    mock_gemini.return_value = [
        {"name": "Alice", "role": "CEO", "phone": "123", "email": "a@e.com"}
    ]

    result = contacts_autofill_from_website("https://example.com")

    assert len(result) == 1
    assert result[0]["name"] == "Alice"


@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_contacts_autofill_dict_contacts_key(mock_load, mock_gemini):
    """LLM returns dict with 'contacts' key → unwrap it."""
    mock_load.side_effect = _make_load_page_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )
    mock_gemini.return_value = {"contacts": [{"name": "Bob", "role": "CTO"}]}

    result = contacts_autofill_from_website("https://example.com")

    assert result[0]["name"] == "Bob"


@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_contacts_autofill_dict_people_key(mock_load, mock_gemini):
    """LLM returns dict with 'people' key → unwrap it."""
    mock_load.side_effect = _make_load_page_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )
    mock_gemini.return_value = {"people": [{"name": "Carol", "role": "Dev"}]}

    result = contacts_autofill_from_website("https://example.com")

    assert result[0]["name"] == "Carol"


@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_contacts_autofill_dict_no_matching_key(mock_load, mock_gemini):
    """LLM returns dict with no recognised key → returns []."""
    mock_load.side_effect = _make_load_page_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )
    mock_gemini.return_value = {"unknown_key": [{"name": "Nobody"}]}

    result = contacts_autofill_from_website("https://example.com")

    assert result == []


@patch("marker.forms.ts.get_current_request")
@patch("marker.utils.website_autofill._load_page_content")
def test_contacts_autofill_all_loads_fail(mock_load_page, mock_get_request):
    """All page loads fail → ValueError."""
    mock_req = MagicMock()
    mock_req.translate.side_effect = lambda msg: msg
    mock_get_request.return_value = mock_req

    mock_load_page.side_effect = Exception("connection refused")

    with pytest.raises(ValueError):
        contacts_autofill_from_website("https://example.com")


@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_contacts_autofill_url_skip(mock_load, mock_gemini):
    """When website URL matches a contact sub-path, that path is skipped."""
    # website = "https://example.com/kontakt" → /kontakt sub-path will be skipped
    # Call 0: main page (https://example.com/kontakt) → main page content
    # Call 1: /contact → 404
    # Call 2-5: remaining paths → 404
    mock_load.side_effect = _make_load_page_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )
    mock_gemini.return_value = [{"name": "Dave", "role": "PM"}]

    result = contacts_autofill_from_website("https://example.com/kontakt")

    assert result[0]["name"] == "Dave"


# ===========================================================================
# tags_autofill_from_website
# ===========================================================================


@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_tags_autofill_list_result(mock_load, mock_gemini):
    """Happy path: main page + subpage load, LLM returns a tag list."""
    long_content = "y" * 300
    mock_load.side_effect = _make_load_page_side_effect(
        "main page content",
        Exception("404"),
        long_content,
    )
    mock_gemini.return_value = ["Construction", "Real estate"]

    result = tags_autofill_from_website("https://example.com")

    assert "Construction" in result
    assert "Real estate" in result


@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_tags_autofill_with_existing_tags(mock_load, mock_gemini):
    """existing_tags are passed to the LLM prompt."""
    mock_load.side_effect = _make_load_page_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )
    mock_gemini.return_value = ["Construction"]

    result = tags_autofill_from_website(
        "https://example.com",
        existing_tags=["Construction", "IT", "Finance"],
    )

    assert result == ["Construction"]
    # Verify the _gemini_json call included the existing tags in the prompt
    call_args = mock_gemini.call_args[0][0]
    assert "Construction" in call_args


@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_tags_autofill_dict_tags_key(mock_load, mock_gemini):
    """LLM returns dict with 'tags' key → unwrap it."""
    mock_load.side_effect = _make_load_page_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )
    mock_gemini.return_value = {"tags": ["BIM", "Architecture"]}

    result = tags_autofill_from_website("https://example.com")

    assert "BIM" in result


@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_tags_autofill_dict_no_matching_key(mock_load, mock_gemini):
    """LLM returns dict with no recognised key → returns []."""
    mock_load.side_effect = _make_load_page_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )
    mock_gemini.return_value = {"other": ["BIM"]}

    result = tags_autofill_from_website("https://example.com")

    assert result == []


@patch("marker.forms.ts.get_current_request")
@patch("marker.utils.website_autofill._load_page_content")
def test_tags_autofill_all_loads_fail(mock_load_page, mock_get_request):
    """All page loads fail → ValueError."""
    mock_req = MagicMock()
    mock_req.translate.side_effect = lambda msg: msg
    mock_get_request.return_value = mock_req

    mock_load_page.side_effect = Exception("connection refused")

    with pytest.raises(ValueError):
        tags_autofill_from_website("https://example.com")


@patch("marker.utils.website_autofill._gemini_json")
@patch("marker.utils.website_autofill._load_page_content")
def test_tags_autofill_url_skip(mock_load, mock_gemini):
    """When website URL matches a sub-path, that path is skipped."""
    # website = "https://example.com/oferta" → /oferta will be skipped
    mock_load.side_effect = _make_load_page_side_effect(
        "main page content",
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
        Exception("404"),
    )
    mock_gemini.return_value = ["Design"]

    result = tags_autofill_from_website("https://example.com/oferta")

    assert result == ["Design"]
