import pytest
from pyramid.httpexceptions import HTTPFound
from webob.multidict import MultiDict

from marker.forms.account import Account, ChangePassword
from marker.views.account import AccountView


class DummyUser:
    def __init__(self, name="TestUser"):
        self._name = name
        self._fullname = "Test User"
        self._email = "test@example.com"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def fullname(self):
        return self._fullname

    @fullname.setter
    def fullname(self, value):
        self._fullname = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value


class DummyRequestWithIdentity:
    def __init__(self, *args, **kwargs):
        from pyramid.testing import DummyRequest

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


class DummySession(dict):
    def flash(self, msg):
        self["flash"] = msg


@pytest.fixture
def dummy_request(tm, dbsession):
    request = DummyRequestWithIdentity()
    request.method = "GET"
    request.POST = MultiDict()
    request.identity = DummyUser()
    request.session = DummySession()
    request.locale_name = "en"
    request.translate = lambda x: x
    request.current_route_url = lambda: "/account"
    request.tm = tm
    request.dbsession = dbsession
    return request


def test_account_edit_get(dummy_request):
    view = AccountView(dummy_request)
    result = view.account_edit()
    assert "form" in result
    assert isinstance(result["form"], Account)


def test_account_edit_post_valid(monkeypatch, dummy_request):
    dummy_request.method = "POST"
    dummy_request.POST = MultiDict(
        {"fullname": "Test User", "email": "test@example.com"}
    )
    monkeypatch.setattr(Account, "validate", lambda self: True)
    user = DummyUser()
    dummy_request.session.flash = lambda msg: None  # zapobiegaj flash
    dummy_request.identity = user
    result = AccountView(dummy_request).account_edit()
    assert isinstance(result, HTTPFound)


def test_account_edit_post_invalid(monkeypatch, dummy_request):
    dummy_request.method = "POST"
    dummy_request.POST = MultiDict({"fullname": "", "email": ""})
    monkeypatch.setattr(Account, "validate", lambda self: False)
    view = AccountView(dummy_request)
    result = view.account_edit()
    assert "form" in result
    assert isinstance(result["form"], Account)


def test_password_edit_get(dummy_request):
    view = AccountView(dummy_request)
    result = view.password_edit()
    assert "form" in result
    assert isinstance(result["form"], ChangePassword)


def test_password_edit_post_valid(monkeypatch, dummy_request):
    dummy_request.method = "POST"
    dummy_request.POST = MultiDict(
        {"password": "StrongPass123", "confirm": "StrongPass123"}
    )
    monkeypatch.setattr(ChangePassword, "validate", lambda self: True)
    user = DummyUser()
    dummy_request.session.flash = lambda msg: None  # zapobiegaj flash
    dummy_request.identity = user
    result = AccountView(dummy_request).password_edit()
    assert isinstance(result, HTTPFound)


def test_password_edit_post_invalid(monkeypatch, dummy_request):
    dummy_request.method = "POST"
    dummy_request.POST = MultiDict({"password": "", "confirm": ""})
    monkeypatch.setattr(ChangePassword, "validate", lambda self: False)
    view = AccountView(dummy_request)
    result = view.password_edit()
    assert "form" in result
    assert isinstance(result["form"], ChangePassword)
