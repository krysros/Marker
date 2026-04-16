from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from marker.subscribers import (
    _selected_ids_loader,
    add_localizer,
    add_renderer_globals,
    get_country_name,
    get_subdivision_name,
)


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
    assert event["get_subdivision_name"] is get_subdivision_name
    assert event["get_country_name"] is get_country_name
    assert isinstance(event["gemini_api_key_set"], bool)


def test_get_subdivision_name_valid():
    assert get_subdivision_name("AD-02") == "Canillo"


def test_get_subdivision_name_invalid():
    assert get_subdivision_name("INVALID-CODE") == ""


def test_get_subdivision_name_none():
    assert get_subdivision_name(None, "---") == "---"


def test_get_country_name_valid():
    assert get_country_name("PL") == "Poland"


def test_get_country_name_invalid():
    assert get_country_name("XX") == ""


def test_get_country_name_none():
    assert get_country_name(None, "---") == "---"


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
    result = mock_request.translate("hello")
    assert result == "translated"
