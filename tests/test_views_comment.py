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
