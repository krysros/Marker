import pytest
from marker.views import report
from pyramid.testing import DummyRequest


class DummySession:
    def execute(self, stmt):
        class Result:
            def keys(self):
                return ["col1", "col2"]

            def fetchall(self):
                return [(1, 2), (3, 4)]

        return Result()


def test_report_prompt_post(monkeypatch):
    req = DummyRequest(post={"prompt": "foo"}, method="POST")
    req.dbsession = DummySession()
    req.registry = type("Reg", (), {"settings": {"gemini.model": "test"}})()
    monkeypatch.setattr(
        "marker.utils.llm_report.generate_report_sql", lambda *a, **k: "SELECT 1"
    )
    monkeypatch.setattr("marker.utils.llm_report.validate_sql", lambda sql: sql)
    view = report.ReportView(req)
    result = view.prompt()
    assert result["columns"] == ["col1", "col2"]
    assert result["rows"] == [(1, 2), (3, 4)]
    assert result["error"] is None
    assert result["sql_generated"] == "SELECT 1"


def test_report_prompt_post_no_prompt():
    req = DummyRequest(post={"prompt": ""}, method="POST")
    req.dbsession = DummySession()
    req.registry = type("Reg", (), {"settings": {}})()
    req.translate = lambda x: x
    view = report.ReportView(req)
    result = view.prompt()
    assert "Please enter a prompt." in result["error"]


def test_report_prompt_post_no_api_key():
    req = DummyRequest(post={"prompt": "foo"}, method="POST")
    req.dbsession = DummySession()
    req.registry = type("Reg", (), {"settings": {}})()
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("GEMINI_API_KEY", "")
    req.translate = lambda x: x
    view = report.ReportView(req)
    result = view.prompt()
    assert "GEMINI_API_KEY is not configured" in result["error"]
    monkeypatch.undo()
