from marker.security import MySecurityPolicy


def test_authenticated_userid_returns_none_when_no_identity():
    policy = MySecurityPolicy("test-seekrit")
    # Patch the identity method to return None
    policy.identity = lambda request: None
    result = policy.authenticated_userid(object())
    assert result is None


def test_authenticated_userid_returns_id():
    from types import SimpleNamespace

    policy = MySecurityPolicy("test-seekrit")
    user = SimpleNamespace(id=42, role="admin")
    policy.identity = lambda request: user
    result = policy.authenticated_userid(object())
    assert result == 42


def test_effective_principals_anonymous():
    from pyramid.authorization import Everyone

    policy = MySecurityPolicy("test-seekrit")
    policy.identity = lambda request: None
    principals = policy.effective_principals(object())
    assert principals == [Everyone]


def test_effective_principals_authenticated():
    from types import SimpleNamespace

    from pyramid.authorization import Authenticated, Everyone

    policy = MySecurityPolicy("test-seekrit")
    user = SimpleNamespace(id=5, role="editor")
    policy.identity = lambda request: user
    principals = policy.effective_principals(object())
    assert Everyone in principals
    assert Authenticated in principals
    assert "u:5" in principals
    assert "role:editor" in principals


def test_forget():
    from unittest.mock import MagicMock

    policy = MySecurityPolicy("test-seekrit")
    policy.authtkt = MagicMock()
    policy.authtkt.forget.return_value = [("Set-Cookie", "")]
    request = MagicMock()
    result = policy.forget(request)
    policy.authtkt.forget.assert_called_once_with(request)
    assert result == [("Set-Cookie", "")]
