import pytest
import types
from marker.utils import website_autofill


def test_subdivision_code_from_value_empty():
    assert website_autofill._subdivision_code_from_value("", "PL") == ""
    assert website_autofill._subdivision_code_from_value("Mazowieckie", "") == ""


def test_normalize_whitespace():
    assert website_autofill._normalize_whitespace("  a  b   c ") == "a b c"


def test_fold_text():
    s = "łódź ß đ ø"
    folded = website_autofill._fold_text(s)
    assert "l" in folded and "ss" in folded and "d" in folded and "o" in folded
    # Should remove diacritics
    assert "ł" not in folded and "ß" not in folded


def test_valueerror_on_content_parts(monkeypatch):
    # Coverage: ValueError when content cannot be retrieved
    monkeypatch.setattr(
        website_autofill,
        "WebBaseLoader",
        lambda url: types.SimpleNamespace(load=lambda: []),
    )
    with pytest.raises(ValueError):
        website_autofill._autofill_from_website("http://example.com", "prompt")


def test_country_normalization_fallback(monkeypatch):
    # Should fallback to default_country if country cannot be resolved
    # Simulate _autofill_from_website logic
    class DummyDoc:
        page_content = "{}"

    monkeypatch.setattr(
        website_autofill,
        "WebBaseLoader",
        lambda url: type("L", (), {"load": lambda self: [DummyDoc()]})(),
    )
    monkeypatch.setattr(website_autofill, "location_details", lambda **kwargs: {})
    monkeypatch.setattr(
        website_autofill.pycountry.countries, "search_fuzzy", lambda val: []
    )
    monkeypatch.setattr(
        website_autofill.pycountry.countries, "get", lambda alpha_2=None: None
    )
    monkeypatch.setattr(
        website_autofill.json, "loads", lambda s: {"country": "Nolandia"}
    )
    # Patch ChatGoogleGenerativeAI to avoid real API call
    from marker.utils import website_autofill as wa

    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            class Response:
                content = '{"country": "Nolandia"}'

            return Response()

    monkeypatch.setattr(wa, "ChatGoogleGenerativeAI", DummyLLM)
    result = website_autofill._autofill_from_website(
        "http://example.com", "prompt", default_country="PL"
    )
    assert result["country"] == "PL"


def test_contact_and_offer_subpages(monkeypatch):
    # Should append content from subpages if found
    # Simulate via _autofill_from_website (which calls subpage logic internally)
    class DummyDoc:
        page_content = "{}"

    def loader(url):
        # Return long content for subpages
        if url.endswith("/kontakt") or url.endswith("/oferta"):
            return type(
                "L",
                (),
                {"load": lambda self: [type("D", (), {"page_content": "x" * 201})()]},
            )()
        return type("L", (), {"load": lambda self: [DummyDoc()]})()

    monkeypatch.setattr(website_autofill, "WebBaseLoader", loader)
    monkeypatch.setattr(website_autofill, "location_details", lambda **kwargs: {})
    monkeypatch.setattr(
        website_autofill.pycountry.countries, "get", lambda alpha_2=None: True
    )
    monkeypatch.setattr(website_autofill.json, "loads", lambda s: {})
    # Patch ChatGoogleGenerativeAI to avoid real API call
    from marker.utils import website_autofill as wa

    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            class Response:
                content = "{}"

            return Response()

    monkeypatch.setattr(wa, "ChatGoogleGenerativeAI", DummyLLM)
    # Should not raise
    website_autofill._autofill_from_website("http://example.com", "prompt")


def test_subdivision_code_from_value_matches(monkeypatch):
    # Should match by code, folded name, and partial folded name
    class Sub:
        def __init__(self, code, name):
            self.code = code
            self.name = name

    subs = [Sub("PL-MZ", "Mazowieckie"), Sub("PL-KR", "Krakowskie")]
    monkeypatch.setattr(
        website_autofill.pycountry.subdivisions, "get", lambda country_code=None: subs
    )
    # By code
    assert website_autofill._subdivision_code_from_value("PL-MZ", "PL") == "PL-MZ"
    # By folded name
    assert website_autofill._subdivision_code_from_value("mazowieckie", "PL") == "PL-MZ"
    # By partial folded name
    assert (
        website_autofill._subdivision_code_from_value("woj. mazowieckie", "PL")
        == "PL-MZ"
    )


def test_country_from_locale_edge_cases():
    # Empty input
    assert website_autofill._country_from_locale("") == ""
    # Invalid input
    assert website_autofill._country_from_locale("not_a_locale") == ""
    # Language code as country
    assert website_autofill._country_from_locale("pl") == "PL"


def test_contacts_autofill_from_website_valueerror(monkeypatch):
    # Should raise ValueError if no content is loaded
    monkeypatch.setattr(
        website_autofill,
        "WebBaseLoader",
        lambda url: types.SimpleNamespace(load=lambda: []),
    )
    with pytest.raises(ValueError):
        website_autofill.contacts_autofill_from_website("http://example.com")


def test_tags_autofill_from_website_valueerror(monkeypatch):
    # Should raise ValueError if no content is loaded
    monkeypatch.setattr(
        website_autofill,
        "WebBaseLoader",
        lambda url: types.SimpleNamespace(load=lambda: []),
    )
    with pytest.raises(ValueError):
        website_autofill.tags_autofill_from_website("http://example.com")


def test_subdivision_code_from_value_edge_cases():
    # Partial/invalid input
    assert website_autofill._subdivision_code_from_value(None, "PL") == ""
    assert website_autofill._subdivision_code_from_value("", None) == ""
    assert website_autofill._subdivision_code_from_value(None, None) == ""


def test_normalize_whitespace_and_fold_text_edge_cases():
    # Empty and None input
    assert website_autofill._normalize_whitespace("") == ""
    assert website_autofill._normalize_whitespace(None) == ""
    assert website_autofill._fold_text("") == ""
    assert website_autofill._fold_text(None) == ""
