import pytest
from marker.views import report
from pyramid.testing import DummyRequest


@pytest.mark.parametrize(
    "rel,expected",
    [
        ("companies-tags", "companies-tags"),
        ("projects-tags", "projects-tags"),
        ("companies-subdivisions", "companies-subdivisions"),
        ("companies-cities", "companies-cities"),
        ("users-companies", "users-companies"),
        ("users-projects", "users-projects"),
        ("companies-projects", "companies-projects"),
    ],
)
def test_report_view_cases(rel, expected):
    req = DummyRequest(matchdict={"rel": rel}, params={"page": 1})
    # Use a MagicMock for dbsession to avoid AttributeError
    from unittest.mock import MagicMock

    req.dbsession = MagicMock()
    req.dbsession.execute.return_value.all.return_value = []
    req.registry = type("Reg", (), {"settings": {}})()
    # Patch route_url to avoid AttributeError from missing getUtility
    req.route_url = lambda *a, **kw: "/dummy-url"
    view = report.ReportView(req)
    # Should not raise
    view.view()


def test_report_view_companies_stars():
    from marker.views.report import ReportView
    from unittest.mock import MagicMock

    req = DummyRequest(matchdict={"rel": "companies-stars"}, params={"page": 1})
    req.dbsession = MagicMock()
    req.dbsession.execute.return_value.all.return_value = []
    req.registry = type("Reg", (), {"settings": {}})()
    req.route_url = lambda *a, **kw: "/dummy-url"
    view = ReportView(req)
    # Should not raise
    view.view()


def test_gemini_ai_options_fallback_and_retries():
    from marker.views.report import ReportView

    class DummyReq:
        def __init__(self):
            self.registry = type(
                "Reg",
                (),
                {
                    "settings": {
                        "gemini.fallback_model": "fallback",
                        "gemini.retries": "2",
                    }
                },
            )()

    req = DummyReq()
    view = ReportView(req)
    opts = view._gemini_ai_options()
    assert opts["fallback_model"] == "fallback"
    assert opts["retries"] == 2


def test_gemini_ai_options_invalid_retries():
    from marker.views.report import ReportView

    class DummyReq:
        def __init__(self):
            self.registry = type(
                "Reg", (), {"settings": {"gemini.retries": "notanint"}}
            )()

    req = DummyReq()
    view = ReportView(req)
    opts = view._gemini_ai_options()
    assert "retries" not in opts
