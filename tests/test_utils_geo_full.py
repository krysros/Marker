"""Tests for marker/utils/geo.py - covering error paths and edge cases using geopy."""

from unittest.mock import MagicMock, patch
from geopy.exc import GeopyError

from marker.utils.geo import (
    _first_not_empty,
    _nominatim_search,
    location,
    location_details,
)


def test_first_not_empty_returns_first():
    assert _first_not_empty("", None, "hello", "world") == "hello"


def test_first_not_empty_all_empty():
    assert _first_not_empty("", None, "  ") == ""


def test_first_not_empty_none():
    assert _first_not_empty(None, None) == ""


def test_nominatim_search_empty_query():
    assert _nominatim_search(q="") is None
    assert _nominatim_search(q="  ") is None
    assert _nominatim_search(q=None) is None


def test_nominatim_search_no_params():
    assert _nominatim_search() is None


def test_nominatim_search_empty_keyword_params():
    assert _nominatim_search(city="", street=None) is None


@patch("marker.utils.geo.Nominatim.geocode")
def test_nominatim_search_geopy_error(mock_geocode):
    mock_geocode.side_effect = GeopyError("network error")
    result = _nominatim_search(q="Warsaw")
    assert result is None


@patch("marker.utils.geo.Nominatim.geocode")
def test_nominatim_search_success(mock_geocode):
    mock_loc = MagicMock()
    mock_geocode.return_value = mock_loc
    result = _nominatim_search(q="Warsaw")
    assert result == mock_loc


@patch("marker.utils.geo._nominatim_search")
def test_location_no_results(mock_search):
    mock_search.return_value = None
    assert location(q="nowhere") is None


@patch("marker.utils.geo._nominatim_search")
def test_location_success(mock_search):
    mock_loc = MagicMock()
    mock_loc.latitude = 52.23
    mock_loc.longitude = 21.01
    mock_search.return_value = mock_loc
    result = location(q="Warsaw")
    assert result == {"lat": 52.23, "lon": 21.01}


@patch("marker.utils.geo._nominatim_search")
def test_location_bad_coords(mock_search):
    mock_loc = MagicMock()
    type(mock_loc).latitude = property(lambda self: float("invalid"))
    mock_search.return_value = mock_loc
    assert location(q="Warsaw") is None


@patch("marker.utils.geo._nominatim_search")
def test_location_details_no_results(mock_search):
    mock_search.return_value = None
    assert location_details(q="nowhere") is None


@patch("marker.utils.geo._nominatim_search")
def test_location_details_no_address(mock_search):
    mock_loc = MagicMock()
    mock_loc.raw = {}
    mock_search.return_value = mock_loc
    assert location_details(q="Warsaw") is None


@patch("marker.utils.geo._nominatim_search")
def test_location_details_success(mock_search):
    mock_loc = MagicMock()
    mock_loc.latitude = 52.23
    mock_loc.longitude = 21.01
    mock_loc.raw = {
        "address": {
            "city": "Warsaw",
            "state": "Mazowieckie",
            "country": "Poland",
            "country_code": "pl",
            "postcode": "00-001",
        },
    }
    mock_search.return_value = mock_loc
    result = location_details(q="Warsaw")
    assert result["city"] == "Warsaw"
    assert result["state"] == "Mazowieckie"
    assert result["country_code"] == "PL"
    assert result["lat"] == 52.23


@patch("marker.utils.geo._nominatim_search")
def test_location_details_bad_lat_lon(mock_search):
    mock_loc = MagicMock()
    type(mock_loc).latitude = property(lambda self: float("invalid"))
    mock_loc.raw = {
        "address": {
            "city": "Test",
            "country_code": "pl",
        },
    }
    mock_search.return_value = mock_loc
    result = location_details(q="test")
    assert "lat" not in result
    assert result["city"] == "Test"


@patch("marker.utils.geo._nominatim_search")
def test_location_details_town_fallback(mock_search):
    mock_loc = MagicMock()
    mock_loc.latitude = 51.0
    mock_loc.longitude = 20.0
    mock_loc.raw = {
        "address": {
            "town": "SmallTown",
            "country": "Poland",
            "country_code": "pl",
        },
    }
    mock_search.return_value = mock_loc
    result = location_details(q="SmallTown")
    assert result["city"] == "SmallTown"


@patch("marker.utils.geo._nominatim_search")
def test_location_with_keyword_params(mock_search):
    mock_loc = MagicMock()
    mock_loc.latitude = 52.0
    mock_loc.longitude = 21.0
    mock_search.return_value = mock_loc
    result = location(city="Warsaw", street="Marszalkowska")
    assert result == {"lat": 52.0, "lon": 21.0}


@patch("marker.utils.geo.Nominatim.geocode")
def test_nominatim_search_with_keyword_params(mock_geocode):
    mock_loc = MagicMock()
    mock_geocode.return_value = mock_loc
    result = _nominatim_search(city="Warsaw")
    assert result == mock_loc
