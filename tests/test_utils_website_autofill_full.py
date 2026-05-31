import pytest
import types
from marker.utils import website_autofill
from marker.utils import langchain_ai


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

    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            class Response:
                content = '{"country": "Nolandia"}'

            return Response()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM)
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

    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            class Response:
                content = "{}"

            return Response()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM)
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


def test_web_base_loader_decode_error(monkeypatch):
    import urllib.request

    class DummyResponse:
        def __init__(self):
            # headers with invalid charset
            self.headers = type(
                "H",
                (),
                {"get_content_charset": lambda *a, **kw: "invalid-charset-name"},
            )()

        def read(self):
            return b"<html><body>Hello World!</body></html>"

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(
        urllib.request, "urlopen", lambda req, timeout=None: DummyResponse()
    )
    loader = website_autofill.WebBaseLoader("http://dummy-url.com")
    docs = loader.load()
    assert "Hello World" in docs[0].page_content


def test_autofill_geo_field_postcode_fallbacks(monkeypatch):
    # Tests postcode resolution chain (postalcode, postal, postal_code)
    # also tests when _subdivision_code_from_value returns empty string (line 116)
    class DummyDoc:
        page_content = "{}"

    monkeypatch.setattr(
        website_autofill,
        "WebBaseLoader",
        lambda url: type("L", (), {"load": lambda self: [DummyDoc()]})(),
    )

    # Patch ChatGoogleGenerativeAI
    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            return type("R", (), {"content": '{"country": "PL"}'})()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM)
    monkeypatch.setattr(website_autofill, "get_configured_model", lambda: "test-model")

    # 1. postalcode fallback
    monkeypatch.setattr(
        website_autofill,
        "location_details",
        lambda **kw: {
            "postalcode": "11-222",
            "country_code": "pl",
            "state": "UnknownState",
        },
    )
    res1 = website_autofill._autofill_from_website("http://dummy.com", "prompt")
    assert res1["postcode"] == "11-222"
    assert (
        res1["subdivision"] == ""
    )  # fallback empty because UnknownState subdivision is not matched

    # 2. postal fallback
    monkeypatch.setattr(
        website_autofill,
        "location_details",
        lambda **kw: {"postal": "33-444", "country_code": "pl"},
    )
    res2 = website_autofill._autofill_from_website("http://dummy.com", "prompt")
    assert res2["postcode"] == "33-444"

    # 3. postal_code fallback
    monkeypatch.setattr(
        website_autofill,
        "location_details",
        lambda **kw: {"postal_code": "55-666", "country_code": "pl"},
    )
    res3 = website_autofill._autofill_from_website("http://dummy.com", "prompt")
    assert res3["postcode"] == "55-666"


def test_autofill_fuzzy_country_match(monkeypatch):
    class DummyDoc:
        page_content = "{}"

    monkeypatch.setattr(
        website_autofill,
        "WebBaseLoader",
        lambda url: type("L", (), {"load": lambda self: [DummyDoc()]})(),
    )

    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            # Country name that triggers search_fuzzy
            return type("R", (), {"content": '{"country": "Polska"}'})()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM)
    monkeypatch.setattr(website_autofill, "get_configured_model", lambda: "test-model")
    monkeypatch.setattr(website_autofill, "location_details", lambda **kw: None)

    # Mock pycountry fuzzy search
    class CountryMock:
        alpha_2 = "PL"

    monkeypatch.setattr(
        website_autofill.pycountry.countries,
        "search_fuzzy",
        lambda query: [CountryMock()],
    )

    res = website_autofill._autofill_from_website("http://dummy.com", "prompt")
    assert res["country"] == "PL"


def test_contacts_loader_main_page_exception(monkeypatch):
    # Test that when loader throws on the main page, it catches it and can still load from a subpage
    calls = []

    def mock_load(self):
        calls.append(self.url)
        if "kontakt" in self.url:
            return [
                type(
                    "D",
                    (),
                    {
                        "page_content": "John Doe - Manager, tel: 1234, email: a@b.com"
                        * 20
                    },
                )()
            ]
        raise RuntimeError("Load failed")

    monkeypatch.setattr(website_autofill.WebBaseLoader, "load", mock_load)
    monkeypatch.setattr(website_autofill, "get_configured_model", lambda: "test-model")

    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            return type("R", (), {"content": "[]"})()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM)

    # Should succeed by loading from subpage and not raising
    res = website_autofill.contacts_autofill_from_website("http://abc.com")
    assert isinstance(res, list)
    assert len(calls) > 1


def test_contacts_parser_variants_and_fallbacks(monkeypatch):
    monkeypatch.setattr(website_autofill, "get_configured_model", lambda: "test-model")
    # Mock main load
    monkeypatch.setattr(
        website_autofill,
        "WebBaseLoader",
        lambda url: type(
            "L", (), {"load": lambda self: [type("D", (), {"page_content": "xyz"})()]}
        )(),
    )

    # 1. Single dict contact result (line 255)
    class DummyLLM_SingleDict:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            return type(
                "R", (), {"content": '{"name": "Jan Kowalski", "role": "CEO"}'}
            )()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM_SingleDict)
    res = website_autofill.contacts_autofill_from_website("http://www.abc.com")
    assert len(res) == 1
    assert res[0]["name"] == "Jan Kowalski"

    # 2. List containing a non-dict contact element (line 260) and empty name with fallback company name (line 282)
    # also tests www prefix pruning (line 222)
    class DummyLLM_InvalidList:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            # first element is non-dict (string), second is empty name with role
            return type(
                "R",
                (),
                {
                    "content": '["not-a-dict", {"name": "", "role": "Director", "email": "dir@abc.com"}]'
                },
            )()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM_InvalidList)
    res2 = website_autofill.contacts_autofill_from_website("http://www.abc.com")
    assert len(res2) == 1
    assert res2[0]["name"] == "Abc"  # capitalized domain name from www.abc.com
    assert res2[0]["role"] == "Director"


def test_contacts_company_fallback_parsing_exception(monkeypatch):
    monkeypatch.setattr(website_autofill, "get_configured_model", lambda: "test-model")
    monkeypatch.setattr(
        website_autofill,
        "WebBaseLoader",
        lambda url: type(
            "L", (), {"load": lambda self: [type("D", (), {"page_content": "xyz"})()]}
        )(),
    )

    # Force parse exception on urlparse specifically inside the fallback_company_name try-except
    class FaultyParsed:
        scheme = "http"
        netloc = ""

        @property
        def path(self):
            raise AttributeError("mocked error")

    monkeypatch.setattr(website_autofill, "urlparse", lambda url: FaultyParsed())

    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            return type(
                "R",
                (),
                {"content": '[{"name": "", "role": "Staff", "email": "a@b.com"}]'},
            )()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM)
    res = website_autofill.contacts_autofill_from_website("http://abc.com")
    assert len(res) == 1
    assert (
        res[0]["name"] == "Company"
    )  # Default fallback because exception occurred when getting domain


def test_tags_loader_main_page_exception(monkeypatch):
    # Test tags loader throws exception on main page
    monkeypatch.setattr(website_autofill, "get_configured_model", lambda: "test-model")
    calls = []

    def mock_load(self):
        calls.append(self.url)
        if "o-nas" in self.url:
            return [type("D", (), {"page_content": "Offer text " * 50})()]
        raise RuntimeError("Load failed")

    monkeypatch.setattr(website_autofill.WebBaseLoader, "load", mock_load)

    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            return type("R", (), {"content": '["Tag1"]'})()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM)
    res = website_autofill.tags_autofill_from_website("http://abc.com")
    assert res == ["Tag1"]
    assert len(calls) > 1


def test_tags_autofill_as_dict(monkeypatch):
    monkeypatch.setattr(website_autofill, "get_configured_model", lambda: "test-model")
    monkeypatch.setattr(
        website_autofill,
        "WebBaseLoader",
        lambda url: type(
            "L", (), {"load": lambda self: [type("D", (), {"page_content": "xyz"})()]}
        )(),
    )

    # Test when Gemini returns a dictionary containing a "tags" list
    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            return type(
                "R", (), {"content": '{"tags": ["Architecture", "Woodwork"]}'}
            )()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM)
    res = website_autofill.tags_autofill_from_website("http://abc.com")
    assert res == ["Architecture", "Woodwork"]


def test_subdivision_partial_substring_match(monkeypatch):
    # subdivision_folded in folded matching (lines 390-395)
    class Sub:
        def __init__(self, code, name):
            self.code = code
            self.name = name

    # Database subdivision is "Mazury"
    subs = [Sub("PL-MZ", "Mazury")]
    monkeypatch.setattr(
        website_autofill.pycountry.subdivisions, "get", lambda country_code=None: subs
    )
    # Search value is "Warmia i Mazury" -> subdivision_folded "mazury" in folded "warmia i mazury"
    code = website_autofill._subdivision_code_from_value("Warmia i Mazury", "PL")
    assert code == "PL-MZ"


def test_website_autofill_subpage_overlap_edge_cases(monkeypatch):
    monkeypatch.setattr(website_autofill, "get_configured_model", lambda: "test-model")

    # 1. For contacts_autofill_from_website when the website itself ends with /kontakt
    class DummyDoc:
        page_content = "some text"

    monkeypatch.setattr(
        website_autofill,
        "WebBaseLoader",
        lambda url: type("L", (), {"load": lambda self: [DummyDoc()]})(),
    )

    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            return type("R", (), {"content": "[]"})()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM)

    # website ends with /kontakt, so when /kontakt is joined, url.rstrip('/') == website.rstrip('/')
    website_autofill.contacts_autofill_from_website("http://abc.com/kontakt")

    # 2. For tags_autofill_from_website when the website itself ends with /oferta
    class DummyDocTags:
        page_content = "some text"

    monkeypatch.setattr(
        website_autofill,
        "WebBaseLoader",
        lambda url: type("L", (), {"load": lambda self: [DummyDocTags()]})(),
    )
    website_autofill.tags_autofill_from_website("http://abc.com/oferta")


def test_web_base_loader_errors_and_script_decompose(monkeypatch):
    # Test that exception in urlopen raises ValueError (lines 43-44)
    import urllib.request

    def mock_urlopen_fail(*args, **kwargs):
        raise RuntimeError("Network error")

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen_fail)

    loader = website_autofill.WebBaseLoader("http://example-fail.com")
    with pytest.raises(ValueError) as exc:
        loader.load()
    assert "Could not load content from" in str(exc.value)

    # Test script and style elements are decomposed (line 48)
    class DummyResponse:
        def __init__(self):
            self.headers = type(
                "H", (), {"get_content_charset": lambda *a, **k: "utf-8"}
            )()

        def read(self):
            return b"<html><head><style>body {color: red;}</style></head><body>Hello<script>alert(1);</script></body></html>"

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    monkeypatch.setattr(
        urllib.request, "urlopen", lambda req, timeout=None: DummyResponse()
    )
    loader = website_autofill.WebBaseLoader("http://example-script.com")
    docs = loader.load()
    assert "Hello" in docs[0].page_content
    assert "alert" not in docs[0].page_content
    assert "color" not in docs[0].page_content


def test_company_autofill_from_website_locales(monkeypatch):
    monkeypatch.setattr(website_autofill, "get_configured_model", lambda: "test-model")

    class DummyDoc:
        page_content = "some text"

    monkeypatch.setattr(
        website_autofill,
        "WebBaseLoader",
        lambda url: type("L", (), {"load": lambda self: [DummyDoc()]})(),
    )

    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            return type(
                "R", (), {"content": '{"name": "Test Company", "country": "PL"}'}
            )()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM)

    # Test PL locale (line 162-169)
    res_pl = website_autofill.company_autofill_from_website(
        "http://test.com", locale="pl"
    )
    assert res_pl["name"] == "Test Company"

    # Test EN/other locale (line 171-177)
    res_en = website_autofill.company_autofill_from_website(
        "http://test.com", locale="en"
    )
    assert res_en["name"] == "Test Company"


def test_project_autofill_from_website_locales(monkeypatch):
    monkeypatch.setattr(website_autofill, "get_configured_model", lambda: "test-model")

    class DummyDoc:
        page_content = "some text"

    monkeypatch.setattr(
        website_autofill,
        "WebBaseLoader",
        lambda url: type("L", (), {"load": lambda self: [DummyDoc()]})(),
    )

    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            return type(
                "R", (), {"content": '{"name": "Test Project", "country": "PL"}'}
            )()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM)

    # Test PL locale (line 183-190)
    res_pl = website_autofill.project_autofill_from_website(
        "http://test.com", locale="pl"
    )
    assert res_pl["name"] == "Test Project"

    # Test EN/other locale (line 192-198)
    res_en = website_autofill.project_autofill_from_website(
        "http://test.com", locale="en"
    )
    assert res_en["name"] == "Test Project"


def test_contacts_autofill_subpage_exception_continue(monkeypatch):
    monkeypatch.setattr(website_autofill, "get_configured_model", lambda: "test-model")

    def mock_load(self):
        if "kontakt" in self.url or "contact" in self.url:
            raise RuntimeError("Subpage fetch failed")
        return [type("D", (), {"page_content": "Main page content"})()]

    monkeypatch.setattr(website_autofill.WebBaseLoader, "load", mock_load)

    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            return type("R", (), {"content": "[]"})()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM)

    res = website_autofill.contacts_autofill_from_website("http://abc.com")
    assert res == []


def test_contacts_autofill_pl_locale_and_phone_strip(monkeypatch):
    monkeypatch.setattr(website_autofill, "get_configured_model", lambda: "test-model")

    class DummyDoc:
        page_content = "some text"

    monkeypatch.setattr(
        website_autofill,
        "WebBaseLoader",
        lambda url: type("L", (), {"load": lambda self: [DummyDoc()]})(),
    )

    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            return type(
                "R",
                (),
                {
                    "content": '[{"name": "Jan Kowalski", "role": "CEO", "phone": "  123456  ", "email": "jan@kowalski.pl"}]'
                },
            )()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM)

    res = website_autofill.contacts_autofill_from_website(
        "http://test.com", locale="pl"
    )
    assert len(res) == 1
    assert res[0]["name"] == "Jan Kowalski"
    assert res[0]["phone"] == "123456"  # covered line 341


def test_tags_autofill_with_existing_tags(monkeypatch):
    monkeypatch.setattr(website_autofill, "get_configured_model", lambda: "test-model")

    class DummyDoc:
        page_content = "some text"

    monkeypatch.setattr(
        website_autofill,
        "WebBaseLoader",
        lambda url: type("L", (), {"load": lambda self: [DummyDoc()]})(),
    )

    class DummyLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            return type("R", (), {"content": '["Tag1", "Tag2"]'})()

    monkeypatch.setattr(langchain_ai, "ChatGoogleGenerativeAI", DummyLLM)

    # Test with pl locale and existing tags (lines 447-452)
    res_pl = website_autofill.tags_autofill_from_website(
        "http://test.com", existing_tags=["Tag1"], locale="pl"
    )
    assert res_pl == ["Tag1", "Tag2"]

    # Test with en locale and existing tags (lines 454-458)
    res_en = website_autofill.tags_autofill_from_website(
        "http://test.com", existing_tags=["Tag1"], locale="en"
    )
    assert res_en == ["Tag1", "Tag2"]
