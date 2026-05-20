from marker.forms.ts import TranslationString


class DummyRequest:
    def __init__(self):
        self.translated = None

    def translate(self, msg):
        self.translated = msg
        return f"translated:{msg}"


def test_translationstring_str(monkeypatch):
    # The current TranslationString returns self.msg if no request or translate is present
    monkeypatch.setattr("pyramid.threadlocal.get_current_request", lambda: None)
    ts = TranslationString("foo")
    result = str(ts)
    assert result == "foo"


def test_translationstring_str_no_request(monkeypatch):
    monkeypatch.setattr("pyramid.threadlocal.get_current_request", lambda: None)
    ts = TranslationString("bar")
    # If there is no request, it should return the original text
    assert str(ts) == "bar"
