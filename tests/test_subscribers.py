from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from marker.subscribers import _selected_ids_loader, add_localizer, add_renderer_globals


def test_selected_ids_loader_anonymous():
    request = SimpleNamespace()  # no identity attribute
    loader = _selected_ids_loader(request)
    result = loader("selected_companies")
    assert result == set()


def test_selected_ids_loader_invalid_name(dbsession):
    user = SimpleNamespace(id=1)
    request = SimpleNamespace(identity=user, dbsession=dbsession)
    loader = _selected_ids_loader(request)
    result = loader("nonexistent_table")
    assert result == set()


def test_selected_ids_loader_caches_result(dbsession):
    user = SimpleNamespace(id=1)
    request = SimpleNamespace(identity=user, dbsession=dbsession)
    loader = _selected_ids_loader(request)
    result1 = loader("selected_companies")
    result2 = loader("selected_companies")
    assert result1 is result2


def test_add_renderer_globals():
    translate_fn = lambda x: x
    localizer_obj = object()
    request = SimpleNamespace(
        translate=translate_fn,
        localizer=localizer_obj,
        identity=None,
    )
    event = {"request": request}
    add_renderer_globals(event)
    assert event["_"] is translate_fn
    assert event["localizer"] is localizer_obj
    assert callable(event["selected_ids"])


def test_add_localizer():
    mock_request = MagicMock()
    event = SimpleNamespace(request=mock_request)
    with patch("marker.subscribers.get_localizer") as mock_get:
        mock_localizer = MagicMock()
        mock_localizer.translate.return_value = "translated"
        mock_get.return_value = mock_localizer
        add_localizer(event)
    assert mock_request.localizer is mock_localizer
    assert callable(mock_request.translate)
