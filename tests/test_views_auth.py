"""Tests for marker/views/auth.py"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import transaction
from pyramid.httpexceptions import HTTPForbidden, HTTPNotFound, HTTPSeeOther
from webob.multidict import MultiDict

from marker.models.user import User
from marker.views.auth import forbidden, httpexception_view, login, logout


def _make_request(
    dbsession, method="GET", post=None, params=None, is_authenticated=False
):
    request = SimpleNamespace()
    request.dbsession = dbsession
    request.method = method
    request.POST = MultiDict(post or {})
    request.GET = MultiDict()
    request.params = MultiDict(params or {})
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/home"
    request.session = MagicMock()
    request.response = MagicMock()
    request.response.status = 200
    request.host_url = "http://localhost"
    request.path_qs = "/"
    request.is_authenticated = is_authenticated
    return request


def test_login_get(dbsession):
    request = _make_request(dbsession)
    result = login(request)
    assert "form" in result
    assert "url" in result
    assert "next_url" in result
    assert "heading" in result


def test_login_post_invalid_form(dbsession):
    request = _make_request(dbsession, method="POST", post={})
    result = login(request)
    assert "form" in result


def test_login_post_wrong_credentials(dbsession):
    user = User(
        name="authuser",
        fullname="A U",
        email="a@u.com",
        role="admin",
        password="correct",
    )
    dbsession.add(user)
    transaction.commit()

    request = _make_request(
        dbsession,
        method="POST",
        post={"username": "authuser", "password": "wrong"},
    )
    result = login(request)
    assert "form" in result
    assert request.response.status == 400


def test_login_post_nonexistent_user(dbsession):
    request = _make_request(
        dbsession,
        method="POST",
        post={"username": "nobody", "password": "pass"},
    )
    result = login(request)
    assert "form" in result


@patch("marker.views.auth.remember")
@patch("marker.views.auth.new_csrf_token")
def test_login_post_success(mock_csrf, mock_remember, dbsession):
    user = User(
        name="authok",
        fullname="A OK",
        email="ok@u.com",
        role="admin",
        password="goodpass",
    )
    dbsession.add(user)
    transaction.commit()

    mock_remember.return_value = []
    request = _make_request(
        dbsession,
        method="POST",
        post={"username": "authok", "password": "goodpass"},
    )
    result = login(request)
    assert isinstance(result, HTTPSeeOther)


def test_logout_post(dbsession):
    request = _make_request(dbsession, method="POST")
    request.identity = MagicMock()
    request.identity.name = "testuser"

    with patch("marker.views.auth.forget", return_value=[]):
        with patch("marker.views.auth.new_csrf_token"):
            result = logout(request)
    assert isinstance(result, HTTPSeeOther)


def test_logout_get(dbsession):
    request = _make_request(dbsession, method="GET")
    result = logout(request)
    assert isinstance(result, HTTPSeeOther)


def test_forbidden_not_authenticated(dbsession):
    request = _make_request(dbsession, is_authenticated=False)
    exc = HTTPForbidden()
    result = forbidden(exc, request)
    assert isinstance(result, HTTPSeeOther)


@patch("marker.views.auth.render_to_response")
def test_forbidden_authenticated(mock_render, dbsession):
    from webob.headers import ResponseHeaders

    request = _make_request(dbsession, is_authenticated=True)
    exc = HTTPForbidden()
    mock_response = MagicMock()
    mock_response.headers = ResponseHeaders()
    mock_render.return_value = mock_response
    result = forbidden(exc, request)
    assert result == mock_response


@patch("marker.views.auth.render_to_response")
def test_httpexception_view_renders_template(mock_render, dbsession):
    from webob.headers import ResponseHeaders

    request = _make_request(dbsession)
    exc = HTTPNotFound()
    mock_response = MagicMock()
    mock_response.headers = ResponseHeaders()
    mock_render.return_value = mock_response
    result = httpexception_view(exc, request)
    assert mock_render.called


@patch("marker.views.auth.render_to_response", side_effect=LookupError)
def test_httpexception_view_lookup_error(mock_render, dbsession):
    request = _make_request(dbsession)
    exc = HTTPNotFound()
    result = httpexception_view(exc, request)
    assert result is exc
