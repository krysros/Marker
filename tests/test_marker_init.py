"""Tests for marker/__init__.py"""

from unittest.mock import MagicMock, patch

from pyramid import testing
from pyramid.testing import DummyRequest

from marker import locale_negotiator


def test_locale_negotiator_cookie():
    """Cover line 15: locale from _LOCALE_ cookie."""
    request = DummyRequest()
    request.cookies = {"_LOCALE_": "pl"}
    assert locale_negotiator(request) == "pl"


def test_models_includeme_creates_engine_when_not_provided():
    """Cover models/__init__.py line 132: get_engine fallback."""
    fake_engine = MagicMock()
    mock_session_factory = MagicMock()

    with (
        patch("marker.models.get_engine", return_value=fake_engine) as mock_ge,
        patch("marker.models.get_session_factory", return_value=mock_session_factory),
    ):
        from marker.models import includeme

        config = testing.setUp(
            settings={"tm.manager_hook": "pyramid_tm.explicit_manager"}
        )
        config.include("pyramid_tm")
        config.include("pyramid_retry")
        includeme(config)
        mock_ge.assert_called_once()
    testing.tearDown()


def test_models_dbsession_fallback_when_no_environ():
    """Cover models/__init__.py line 143: get_tm_session fallback."""
    fake_engine = MagicMock()
    mock_session_factory = MagicMock()
    fake_dbsession = MagicMock()
    captured = {}

    original_add_request_method = None

    with (
        patch("marker.models.get_engine", return_value=fake_engine),
        patch("marker.models.get_session_factory", return_value=mock_session_factory),
        patch("marker.models.get_tm_session", return_value=fake_dbsession) as mock_gtms,
    ):
        from marker.models import includeme

        config = testing.setUp(
            settings={"tm.manager_hook": "pyramid_tm.explicit_manager"}
        )
        config.include("pyramid_tm")
        config.include("pyramid_retry")

        # Capture the dbsession function passed to add_request_method
        orig = config.add_request_method

        def capture_add_request_method(fn, *args, **kwargs):
            captured["dbsession_fn"] = fn
            return orig(fn, *args, **kwargs)

        config.add_request_method = capture_add_request_method
        includeme(config)

        # Call the captured function with a request missing app.dbsession
        request = DummyRequest()
        request.environ = {}
        request.tm = MagicMock()
        result = captured["dbsession_fn"](request)
        assert result is fake_dbsession
        mock_gtms.assert_called_once()

    testing.tearDown()
