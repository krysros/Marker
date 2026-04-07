"""Tests for marker/__init__.py"""

from pyramid.testing import DummyRequest

from marker import locale_negotiator


def test_locale_negotiator_cookie():
    """Cover line 15: locale from _LOCALE_ cookie."""
    request = DummyRequest()
    request.cookies = {"_LOCALE_": "pl"}
    assert locale_negotiator(request) == "pl"
