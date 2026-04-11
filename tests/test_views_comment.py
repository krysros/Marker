from unittest.mock import MagicMock

import pytest
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.testing import DummyRequest
from webob.multidict import MultiDict

from marker.forms.comment import CommentFilterForm, CommentSearchForm
from marker.models import Comment
from marker.views.comment import CommentView


class DummyRequestWithIdentity:
    def __init__(self, *args, **kwargs):
        self._request = DummyRequest(*args, **kwargs)
        self._identity = None

    def __getattr__(self, name):
        return getattr(self._request, name)

    @property
    def identity(self):
        return self._identity

    @identity.setter
    def identity(self, value):
        self._identity = value


class DummyDBSession:
    def __init__(self, comments=None):
        self._comments = comments or []
        self.deleted = []

    def execute(self, stmt):
        class Result:
            def scalar(self_inner):
                return len(self._comments)

            def scalars(self_inner):
                class All:
                    def all(self_):
                        return self._comments

                return All()

        return Result()

    def delete(self, obj):
        self.deleted.append(obj)


class DummyIdentity:
    def __init__(self, name="tester"):
        self.name = name


class DummyComment:
    def __init__(self, comment="Test comment"):
        self.comment = comment
        self.company_id = None
        self.project_id = None


@pytest.fixture
def dummy_request():
    req = DummyRequestWithIdentity()
    req.dbsession = DummyDBSession([DummyComment()])
    req.identity = DummyIdentity()
    req.translate = lambda x: x
    req.route_url = lambda *a, **kw: "/next"
    req.response = MagicMock()
    req.context = MagicMock()
    req.context.comment = DummyComment()
    req.GET = MultiDict()
    req.POST = MultiDict()
    return req


def test_all_view_returns_expected_keys(dummy_request):
    view = CommentView(dummy_request)
    result = view.all()
    assert set(result.keys()) >= {
        "q",
        "paginator",
        "next_page",
        "counter",
        "order_criteria",
        "categories",
        "form",
    }
    assert isinstance(result["form"], CommentFilterForm)


def test_count_view_returns_int(dummy_request):
    view = CommentView(dummy_request)
    result = view.count()
    assert isinstance(result, int)


# ===========================================================================
# Database-backed tests for uncovered branches
# ===========================================================================

import transaction

import marker.forms.ts
from marker.models.company import Company
from marker.models.project import Project
from marker.models.user import User
from tests.conftest import DummyRequestWithIdentity


@pytest.fixture(autouse=True)
def patch_ts(monkeypatch):
    monkeypatch.setattr(
        marker.forms.ts.TranslationString, "__str__", lambda self: self.msg
    )
    yield


def _req(dbsession, user, params=None):
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = MagicMock(name="tester")
    request.method = "GET"
    request.GET = MultiDict(params or {})
    request.POST = MultiDict()
    request.params = MultiDict(params or {})
    request.locale_name = "en"
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/comment"
    request.session = MagicMock()
    request.response = MagicMock()
    request.context = MagicMock()
    request.matchdict = {}
    request.matched_route = MagicMock()
    request.matched_route.name = "comment_all"
    request.environ = {}
    request.environ["webob._parsed_get_vars"] = (MultiDict(params or {}), MultiDict())
    request.environ["webob._parsed_post_vars"] = (MultiDict(), MultiDict())
    request.environ["webob._parsed_params_vars"] = (
        MultiDict(params or {}),
        MultiDict(),
    )
    request.path_qs = "/comment"
    request.query_string = ""
    request.referrer = "/home"
    request.headers = {}
    return request


def _user(dbsession, name="cmtuser"):
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


def test_comment_all_filter_text(dbsession):
    user = _user(dbsession)
    co = Company(
        name="CmtCo",
        street="S",
        postcode="00",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    co.created_by = user
    dbsession.add(co)
    dbsession.flush()
    c = Comment(comment="findme_text")
    c.created_by = user
    c.company_id = co.id
    dbsession.add(c)
    transaction.commit()
    request = _req(dbsession, user, params={"comment": "findme"})
    view = CommentView(request)
    result = view.all()
    assert result["q"]["comment"] == "findme"


def test_comment_all_category_companies(dbsession):
    user = _user(dbsession, "cmtcatco")
    co = Company(
        name="CmtCatCo",
        street="S",
        postcode="00",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    co.created_by = user
    dbsession.add(co)
    dbsession.flush()
    c = Comment(comment="co comment")
    c.created_by = user
    c.company_id = co.id
    dbsession.add(c)
    transaction.commit()
    request = _req(dbsession, user, params={"category": "companies"})
    view = CommentView(request)
    result = view.all()
    assert result["q"]["category"] == "companies"


def test_comment_all_category_projects(dbsession):
    user = _user(dbsession, "cmtcatp")
    proj = Project(
        name="CmtCatP",
        street="S",
        postcode="00",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="",
        color="",
        deadline=None,
        stage="",
        delivery_method="",
    )
    proj.created_by = user
    dbsession.add(proj)
    dbsession.flush()
    c = Comment(comment="proj comment")
    c.created_by = user
    c.project_id = proj.id
    dbsession.add(c)
    transaction.commit()
    request = _req(dbsession, user, params={"category": "projects"})
    view = CommentView(request)
    result = view.all()
    assert result["q"]["category"] == "projects"


def test_comment_all_order_asc(dbsession):
    user = _user(dbsession, "cmtasc")
    transaction.commit()
    request = _req(dbsession, user, params={"order": "asc"})
    view = CommentView(request)
    result = view.all()
    assert result["q"]["order"] == "asc"


def test_delete_view_modifies_db_and_sets_header(dummy_request):
    view = CommentView(dummy_request)
    dummy_request.identity = DummyIdentity("user1")
    dummy_request.response.headers = {}
    result = view.delete()
    assert dummy_request.context.comment in dummy_request.dbsession.deleted
    assert dummy_request.response.headers["HX-Trigger"] == "commentEvent"
    assert result == ""


def test_search_view_get(dummy_request):
    dummy_request.method = "GET"
    view = CommentView(dummy_request)
    result = view.search()
    assert "form" in result
    assert result["heading"] == "Find a comment"


def test_search_view_post_valid(monkeypatch, dummy_request):
    dummy_request.method = "POST"
    form = CommentSearchForm()
    monkeypatch.setattr(CommentSearchForm, "validate", lambda self: True)
    monkeypatch.setattr(CommentSearchForm, "comment", type("F", (), {"data": "test"})())
    dummy_request.POST = MultiDict({"comment": "test"})
    view = CommentView(dummy_request)
    result = view.search()
    assert isinstance(result, HTTPSeeOther)


def test_search_view_post_invalid(monkeypatch, dummy_request):
    dummy_request.method = "POST"
    monkeypatch.setattr(CommentSearchForm, "validate", lambda self: False)
    dummy_request.POST = MultiDict({"comment": "test"})
    view = CommentView(dummy_request)
    result = view.search()
    assert "form" in result
    assert result["heading"] == "Find a comment"


# ===========================================================================
# Date range filtering tests
# ===========================================================================


def test_comment_all_date_from(dbsession):
    user = _user(dbsession, "cmtdtf1")
    co = Company(
        name="CmtDfCo",
        street="S",
        postcode="00",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    co.created_by = user
    dbsession.add(co)
    dbsession.flush()
    c = Comment(comment="datefrom_comment")
    c.created_by = user
    c.company_id = co.id
    dbsession.add(c)
    transaction.commit()
    request = _req(dbsession, user, params={"date_from": "2020-01-01T00:00"})
    view = CommentView(request)
    result = view.all()
    assert result["q"]["date_from"] == "2020-01-01T00:00"
    assert result["counter"] >= 1


def test_comment_all_date_to(dbsession):
    user = _user(dbsession, "cmtdtt1")
    co = Company(
        name="CmtDtCo",
        street="S",
        postcode="00",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    co.created_by = user
    dbsession.add(co)
    dbsession.flush()
    c = Comment(comment="dateto_comment")
    c.created_by = user
    c.company_id = co.id
    dbsession.add(c)
    transaction.commit()
    request = _req(dbsession, user, params={"date_to": "2030-01-01T00:00"})
    view = CommentView(request)
    result = view.all()
    assert result["q"]["date_to"] == "2030-01-01T00:00"
    assert result["counter"] >= 1


def test_comment_all_date_range(dbsession):
    user = _user(dbsession, "cmtdtr1")
    co = Company(
        name="CmtDrCo",
        street="S",
        postcode="00",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    co.created_by = user
    dbsession.add(co)
    dbsession.flush()
    c = Comment(comment="daterange_comment")
    c.created_by = user
    c.company_id = co.id
    dbsession.add(c)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={"date_from": "2020-01-01T00:00", "date_to": "2030-01-01T00:00"},
    )
    view = CommentView(request)
    result = view.all()
    assert result["q"]["date_from"] == "2020-01-01T00:00"
    assert result["q"]["date_to"] == "2030-01-01T00:00"
    assert result["counter"] >= 1
