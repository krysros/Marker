from marker.forms.ts import TranslationString


class DummyRequest:
    def __init__(self):
        self.translated = None

    def translate(self, msg):
        self.translated = msg
        return f"translated:{msg}"


def test_translationstring_str(monkeypatch):
    req = DummyRequest()
    monkeypatch.setattr("pyramid.threadlocal.get_current_request", lambda: req)
    ts = TranslationString("foo")
    assert str(ts) == "foo"
