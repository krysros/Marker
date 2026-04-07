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


def test_report_view_not_found(dbsession):
    from pyramid.httpexceptions import HTTPNotFound

    request = _make_request(dbsession, matchdict={"rel": "nonexistent-report"})
    view = ReportView(request)
    try:
        view.view()
        assert False, "Should have raised HTTPNotFound"
    except HTTPNotFound:
        pass
