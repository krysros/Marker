from marker.forms.ts import TranslationString


class DummyRequest:
    def __init__(self):
        self.translated = None

    def translate(self, msg):
        self.translated = msg
        return f"translated:{msg}"


def test_translationstring_str(monkeypatch):
    # Restore the original __str__ method
    monkeypatch.setattr(TranslationString, "__str__", TranslationString._original_str)
    monkeypatch.setattr("marker.forms.ts.get_current_request", lambda: None)
    ts = TranslationString("foo")
    result = str(ts)
    assert result == "foo"


def test_translationstring_str_no_request(monkeypatch):
    monkeypatch.setattr(TranslationString, "__str__", TranslationString._original_str)
    monkeypatch.setattr("marker.forms.ts.get_current_request", lambda: None)
    ts = TranslationString("bar")
    # If there is no request, it should return the original text
    assert str(ts) == "bar"


def test_translationstring_str_with_request(monkeypatch):
    class DummyRequestWithTranslate:
        def translate(self, msg):
            return f"translated:{msg}"

    monkeypatch.setattr(TranslationString, "__str__", TranslationString._original_str)
    monkeypatch.setattr("marker.forms.ts.get_current_request", lambda: DummyRequestWithTranslate())
    ts = TranslationString("hello")
    assert str(ts) == "translated:hello"



