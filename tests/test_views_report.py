"""Tests for marker/views/report.py"""

from unittest.mock import MagicMock

import transaction
from webob.multidict import MultiDict

from marker.models.company import Company
from marker.models.project import Project
from marker.models.tag import Tag
from marker.models.user import User
from marker.views.report import ReportView
from tests.conftest import DummyRequestWithIdentity


def _make_request(dbsession, matchdict=None, params=None):
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.method = "GET"
    request.GET = MultiDict()
    request.params = MultiDict(params or {})
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/report"
    request.session = MagicMock()
    request.response = MagicMock()
    request.matchdict = matchdict or {}
    return request


def test_report_all(dbsession):
    request = _make_request(dbsession)
    view = ReportView(request)
    result = view.all()
    assert "heading" in result
    assert "reports" in result
    assert "counter" in result
    assert result["counter"] > 0


def test_report_view_companies_tags(dbsession):
    user = User(
        name="rptuser", fullname="R U", email="r@e.com", role="admin", password="pw"
    )
    dbsession.add(user)
    dbsession.flush()
    tag = Tag(name="ReportTag")
    tag.created_by = user
    dbsession.add(tag)
    company = Company(
        name="ReportCo",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company.created_by = user
    dbsession.add(company)
    dbsession.flush()
    company.tags.append(tag)
    transaction.commit()

    request = _make_request(dbsession, matchdict={"rel": "companies-tags"})
    view = ReportView(request)
    result = view.view()
    assert "paginator" in result
    assert result["rel"] == "companies-tags"


def test_report_view_projects_tags(dbsession):
    user = User(
        name="rptuser2", fullname="R U2", email="r2@e.com", role="admin", password="pw"
    )
    dbsession.add(user)
    dbsession.flush()
    tag = Tag(name="ReportTag2")
    tag.created_by = user
    dbsession.add(tag)
    project = Project(
        name="ReportProj",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        deadline=None,
        stage="",
        delivery_method="",
    )
    project.created_by = user
    dbsession.add(project)
    dbsession.flush()
    project.tags.append(tag)
    transaction.commit()

    request = _make_request(dbsession, matchdict={"rel": "projects-tags"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "projects-tags"


def test_report_view_companies_subdivisions(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "companies-subdivisions"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "companies-subdivisions"


def test_report_view_companies_cities(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "companies-cities"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "companies-cities"


def test_report_view_companies_comments(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "companies-comments"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "companies-comments"


def test_report_view_projects_subdivisions(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "projects-subdivisions"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "projects-subdivisions"


def test_report_view_projects_cities(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "projects-cities"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "projects-cities"


def test_report_view_projects_comments(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "projects-comments"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "projects-comments"


def test_report_view_users_companies(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "users-companies"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "users-companies"


def test_report_view_users_projects(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "users-projects"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "users-projects"


def test_report_view_companies_projects(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "companies-projects"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "companies-projects"


def test_report_view_companies_stars(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "companies-stars"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "companies-stars"


def test_report_view_projects_stars(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "projects-stars"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "projects-stars"


def test_report_view_companies_announcement(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "companies-announcement"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "companies-announcement"


def test_report_view_companies_tenders(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "companies-tenders"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "companies-tenders"


def test_report_view_companies_constructions(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "companies-constructions"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "companies-constructions"


def test_report_view_designers(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "designers"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "designers"


def test_report_view_purchasers(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "purchasers"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "purchasers"


def test_report_view_investors(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "investors"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "investors"


def test_report_view_general_contractors(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "general-contractors"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "general-contractors"


def test_report_view_subcontractors(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "subcontractors"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "subcontractors"


def test_report_view_suppliers(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "suppliers"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "suppliers"


def test_report_view_projects_companies(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "projects-companies"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "projects-companies"


def test_report_view_projects_highest_value(dbsession):
    request = _make_request(dbsession, matchdict={"rel": "projects-highest-value"})
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "projects-highest-value"


def test_report_view_projects_highest_usable_area(dbsession):
    request = _make_request(
        dbsession, matchdict={"rel": "projects-highest-usable-area"}
    )
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "projects-highest-usable-area"


def test_report_view_projects_highest_cubic_volume(dbsession):
    request = _make_request(
        dbsession, matchdict={"rel": "projects-highest-cubic-volume"}
    )
    view = ReportView(request)
    result = view.view()
    assert result["rel"] == "projects-highest-cubic-volume"


def test_report_view_not_found(dbsession):
    from pyramid.httpexceptions import HTTPNotFound

    request = _make_request(dbsession, matchdict={"rel": "nonexistent-report"})
    view = ReportView(request)
    try:
        view.view()
        assert False, "Should have raised HTTPNotFound"
    except HTTPNotFound:
        pass


# ===========================================================================
# prompt()
# ===========================================================================


def _make_post_request(dbsession, post_data=None):
    request = _make_request(dbsession)
    request.method = "POST"
    request.POST = MultiDict(post_data or {})
    return request


def test_prompt_get(dbsession):
    request = _make_request(dbsession)
    view = ReportView(request)
    result = view.prompt()
    assert result["prompt"] == ""
    assert result["columns"] is None
    assert result["rows"] is None
    assert result["error"] is None
    assert result["sql_generated"] is None


def test_prompt_post_empty_prompt(dbsession):
    request = _make_post_request(dbsession, {"prompt": ""})
    view = ReportView(request)
    result = view.prompt()
    assert result["error"] is not None
    assert result["columns"] is None


def test_prompt_post_no_api_key(dbsession, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    request = _make_post_request(dbsession, {"prompt": "show all companies"})
    view = ReportView(request)
    result = view.prompt()
    assert result["error"] is not None
    assert result["columns"] is None


def test_prompt_post_with_mock_llm(dbsession, monkeypatch):
    from unittest.mock import patch

    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    sql = "SELECT name FROM companies LIMIT 10"
    with patch(
        "marker.views.report.ReportView.prompt.__wrapped__"
        if hasattr(ReportView.prompt, "__wrapped__")
        else "marker.utils.llm_report.generate_report_sql",
        return_value=sql,
    ):
        with patch(
            "marker.utils.llm_report.generate_report_sql", return_value=sql
        ):
            request = _make_post_request(
                dbsession, {"prompt": "show all companies"}
            )
            view = ReportView(request)
            result = view.prompt()
            assert result["sql_generated"] == sql
            assert result["columns"] is not None
            assert result["error"] is None


def test_prompt_post_exception(dbsession, monkeypatch):
    from unittest.mock import patch

    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    with patch(
        "marker.utils.llm_report.generate_report_sql",
        side_effect=RuntimeError("LLM call failed"),
    ):
        request = _make_post_request(dbsession, {"prompt": "show all companies"})
        view = ReportView(request)
        result = view.prompt()
        assert result["error"] == "LLM call failed"
        assert result["columns"] is None
        assert result["rows"] is None

