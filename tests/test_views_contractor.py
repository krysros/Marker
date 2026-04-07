"""Tests for marker/views/contractor.py"""

from unittest.mock import MagicMock

import pytest
import transaction
from webob.multidict import MultiDict

import marker.forms.ts
from marker.models.association import Activity
from marker.models.comment import Comment
from marker.models.company import Company
from marker.models.project import Project
from marker.models.tag import Tag
from marker.models.user import User
from marker.views.contractor import ContractorView
from tests.conftest import DummyRequestWithIdentity


@pytest.fixture(autouse=True)
def patch_translationstring_str(monkeypatch):
    monkeypatch.setattr(
        marker.forms.ts.TranslationString, "__str__", lambda self: self.msg
    )
    yield


def _req(dbsession, user, method="GET", params=None):
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = method
    request.GET = MultiDict(params or {})
    request.POST = MultiDict()
    request.params = MultiDict(params or {})
    request.locale_name = "en"
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/contractor"
    request.session = MagicMock()
    request.response = MagicMock()
    request.response.headers = {}
    request.context = MagicMock()
    request.matchdict = {}
    request.matched_route = MagicMock()
    request.matched_route.name = "contractor_all"
    request.environ = {}
    request.environ["webob._parsed_get_vars"] = (MultiDict(params or {}), MultiDict())
    request.environ["webob._parsed_post_vars"] = (MultiDict(), MultiDict())
    request.environ["webob._parsed_params_vars"] = (
        MultiDict(params or {}),
        MultiDict(),
    )
    request.path_qs = "/contractor"
    request.query_string = ""
    request.referrer = "/home"
    request.headers = {}
    return request


def _user(dbsession, name="contuser"):
    user = User(
        name=name,
        fullname="Test User",
        email=f"{name}@e.com",
        role="admin",
        password="pw",
    )
    dbsession.add(user)
    dbsession.flush()
    return user


def _company_with_activity(dbsession, user, name="ConCo"):
    company = Company(
        name=name,
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="http://x.com",
        color="",
        NIP="n",
        REGON="r",
        KRS="k",
    )
    company.created_by = user
    dbsession.add(company)
    dbsession.flush()

    project = Project(
        name=f"{name}Proj",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="http://x.com",
        color="",
        deadline=None,
        stage="",
        delivery_method="",
    )
    project.created_by = user
    dbsession.add(project)
    dbsession.flush()

    activity = Activity(company_id=company.id, project_id=project.id, role="investor")
    dbsession.add(activity)
    dbsession.flush()
    return company, project


def test_contractor_all_default(dbsession):
    user = _user(dbsession)
    _company_with_activity(dbsession, user)
    transaction.commit()
    request = _req(dbsession, user)
    view = ContractorView(request)
    result = view.all()
    assert "paginator" in result
    assert "counter" in result


def test_contractor_all_invalid_sort_order(dbsession):
    user = _user(dbsession, "contsortinv")
    _company_with_activity(dbsession, user, "ConSortInvCo")
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = ContractorView(request)
    result = view.all()
    assert result["q"]["sort"] == "created_at"
    assert result["q"]["order"] == "desc"


def test_contractor_all_sort_stars(dbsession):
    user = _user(dbsession, "contstarssrt")
    co, _ = _company_with_activity(dbsession, user, "ConStarsSrtCo")
    user.companies_stars.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "stars",
            "order": "asc",
        },
    )
    view = ContractorView(request)
    result = view.all()
    assert result["q"]["sort"] == "stars"


def test_contractor_all_sort_stars_desc(dbsession):
    user = _user(dbsession, "contstarsd")
    co, _ = _company_with_activity(dbsession, user, "ConStarsDCo")
    user.companies_stars.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "stars",
            "order": "desc",
        },
    )
    view = ContractorView(request)
    result = view.all()
    assert result["q"]["sort"] == "stars"


def test_contractor_all_sort_comments(dbsession):
    user = _user(dbsession, "contcmtsrt")
    co, _ = _company_with_activity(dbsession, user, "ConCmtSrtCo")
    comment = Comment(comment="test")
    comment.created_by = user
    comment.company_id = co.id
    dbsession.add(comment)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "comments",
            "order": "asc",
        },
    )
    view = ContractorView(request)
    result = view.all()
    assert result["q"]["sort"] == "comments"


def test_contractor_all_sort_comments_desc(dbsession):
    user = _user(dbsession, "contcmtd")
    co, _ = _company_with_activity(dbsession, user, "ConCmtDCo")
    comment = Comment(comment="test")
    comment.created_by = user
    comment.company_id = co.id
    dbsession.add(comment)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "comments",
            "order": "desc",
        },
    )
    view = ContractorView(request)
    result = view.all()
    assert result["q"]["sort"] == "comments"


def test_contractor_all_filter_role(dbsession):
    user = _user(dbsession, "controle")
    _company_with_activity(dbsession, user, "ConRoleCo")
    transaction.commit()
    request = _req(dbsession, user, params={"role": "investor"})
    view = ContractorView(request)
    result = view.all()
    assert "investor" in result["q"].get("role", [])


def test_contractor_all_filter_tag(dbsession):
    user = _user(dbsession, "conttag")
    co, _ = _company_with_activity(dbsession, user, "ConTagCo")
    tag = Tag(name="ConTag")
    tag.created_by = user
    tag.companies.append(co)
    dbsession.add(tag)
    transaction.commit()
    request = _req(dbsession, user, params={"tag": "ConTag"})
    view = ContractorView(request)
    result = view.all()
    assert "paginator" in result


def test_contractor_all_bulk_select(dbsession):
    user = _user(dbsession, "contbulk")
    _company_with_activity(dbsession, user, "ConBulkCo")
    transaction.commit()
    request = _req(
        dbsession, user, method="POST", params={"_select_all": "1", "checked": "1"}
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = ContractorView(request)
    result = view.all()
    assert result is request.response


def test_contractor_available_tags_empty_name(dbsession):
    """Cover line 44: skip tags with empty name in _available_tags."""
    user = _user(dbsession, "contemptytag")
    co, _ = _company_with_activity(dbsession, user, "EmptyTagCo")
    tag = Tag(name="")
    tag.created_by = user
    tag.companies.append(co)
    dbsession.add(tag)
    valid_tag = Tag(name="ValidTag")
    valid_tag.created_by = user
    valid_tag.companies.append(co)
    dbsession.add(valid_tag)
    transaction.commit()
    request = _req(dbsession, user)
    view = ContractorView(request)
    tags = view._available_tags()
    assert "ValidTag" in tags
    assert "" not in tags
