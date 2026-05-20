import pytest
import types
import marker.utils.website_autofill as autofill


class DummyLLM:
    def __init__(self, content):
        self.content = content

    def invoke(self, prompt):
        return types.SimpleNamespace(content=self.content)


class DummyLoader:
    def __init__(self, docs):
        self._docs = docs

    def load(self):
        return self._docs


def test_autofill_from_website_valueerror(monkeypatch):
    monkeypatch.setattr(autofill, "WebBaseLoader", lambda url: DummyLoader([]))
    with pytest.raises(ValueError):
        autofill._autofill_from_website("http://x", "prompt")


def test_autofill_from_website_street_cleanup(monkeypatch):
    doc = types.SimpleNamespace(page_content="irrelevant")
    monkeypatch.setattr(autofill, "WebBaseLoader", lambda url: DummyLoader([doc]))
    monkeypatch.setattr(
        autofill,
        "ChatGoogleGenerativeAI",
        lambda **kwargs: DummyLLM('{"street": "ul. Testowa 1"}'),
    )
    res = autofill._autofill_from_website("http://x", "prompt")
    assert res["street"] == "Testowa 1"


def test_autofill_from_website_country_fallback(monkeypatch):
    doc = types.SimpleNamespace(page_content="irrelevant")
    monkeypatch.setattr(autofill, "WebBaseLoader", lambda url: DummyLoader([doc]))
    monkeypatch.setattr(
        autofill,
        "ChatGoogleGenerativeAI",
        lambda **kwargs: DummyLLM('{"country": "Neverland"}'),
    )
    res = autofill._autofill_from_website("http://x", "prompt", default_country="PL")
    assert res["country"] == "PL"


def test_country_from_locale():
    assert autofill._country_from_locale("pl_PL") == "PL"
    assert autofill._country_from_locale("pl") == "PL"
    assert autofill._country_from_locale("") == ""
    assert autofill._country_from_locale("xx") == ""


def test_contacts_autofill_from_website_list(monkeypatch):
    doc = types.SimpleNamespace(page_content="abc")
    monkeypatch.setattr(autofill, "WebBaseLoader", lambda url: DummyLoader([doc]))
    monkeypatch.setattr(
        autofill, "ChatGoogleGenerativeAI", lambda **kwargs: DummyLLM('[{"name": "A"}]')
    )
    res = autofill.contacts_autofill_from_website("http://x")
    assert isinstance(res, list) and res and res[0]["name"] == "A"


def test_contacts_autofill_from_website_dict(monkeypatch):
    doc = types.SimpleNamespace(page_content="abc")
    monkeypatch.setattr(autofill, "WebBaseLoader", lambda url: DummyLoader([doc]))
    monkeypatch.setattr(
        autofill,
        "ChatGoogleGenerativeAI",
        lambda **kwargs: DummyLLM('{"contacts": [{"name": "B"}]}'),
    )
    res = autofill.contacts_autofill_from_website("http://x")
    assert isinstance(res, list) and res and res[0]["name"] == "B"


def test_contacts_autofill_from_website_empty(monkeypatch):
    doc = types.SimpleNamespace(page_content="abc")
    monkeypatch.setattr(autofill, "WebBaseLoader", lambda url: DummyLoader([doc]))
    monkeypatch.setattr(
        autofill, "ChatGoogleGenerativeAI", lambda **kwargs: DummyLLM("{}")
    )
    res = autofill.contacts_autofill_from_website("http://x")
    assert res == []


def test_contacts_autofill_from_website_valueerror(monkeypatch):
    monkeypatch.setattr(autofill, "WebBaseLoader", lambda url: DummyLoader([]))
    with pytest.raises(ValueError):
        autofill.contacts_autofill_from_website("http://x")


def test_tags_autofill_from_website_list(monkeypatch):
    doc = types.SimpleNamespace(page_content="abc")
    monkeypatch.setattr(autofill, "WebBaseLoader", lambda url: DummyLoader([doc]))
    monkeypatch.setattr(
        autofill, "ChatGoogleGenerativeAI", lambda **kwargs: DummyLLM('["A", "B"]')
    )
    res = autofill.tags_autofill_from_website("http://x")
    assert res == ["A", "B"]


def test_tags_autofill_from_website_dict(monkeypatch):
    doc = types.SimpleNamespace(page_content="abc")
    monkeypatch.setattr(autofill, "WebBaseLoader", lambda url: DummyLoader([doc]))
    monkeypatch.setattr(
        autofill,
        "ChatGoogleGenerativeAI",
        lambda **kwargs: DummyLLM('{"tags": ["C", "D"]}'),
    )
    res = autofill.tags_autofill_from_website("http://x")
    assert res == ["C", "D"]


def test_tags_autofill_from_website_empty(monkeypatch):
    doc = types.SimpleNamespace(page_content="abc")
    monkeypatch.setattr(autofill, "WebBaseLoader", lambda url: DummyLoader([doc]))
    monkeypatch.setattr(
        autofill, "ChatGoogleGenerativeAI", lambda **kwargs: DummyLLM("{}")
    )
    res = autofill.tags_autofill_from_website("http://x")
    assert res == []


def test_tags_autofill_from_website_valueerror(monkeypatch):
    monkeypatch.setattr(autofill, "WebBaseLoader", lambda url: DummyLoader([]))
    with pytest.raises(ValueError):
        autofill.tags_autofill_from_website("http://x")
