"""Tests for marker/utils/geo.py - covering error paths and edge cases."""

import json
from unittest.mock import MagicMock, patch

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
    assert _nominatim_search(q="") == []
    assert _nominatim_search(q="  ") == []
    assert _nominatim_search(q=None) == []


def test_nominatim_search_no_params():
    assert _nominatim_search() == []


def test_nominatim_search_empty_keyword_params():
    assert _nominatim_search(city="", street=None) == []


@patch("marker.utils.geo.urllib.request.urlopen")
def test_nominatim_search_url_error(mock_urlopen):
    import urllib.error

    mock_urlopen.side_effect = urllib.error.URLError("network error")
    result = _nominatim_search(q="Warsaw")
    assert result == []


@patch("marker.utils.geo.urllib.request.urlopen")
def test_nominatim_search_invalid_json(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.read.return_value = b"not json"
    mock_urlopen.return_value = mock_resp
    result = _nominatim_search(q="Warsaw")
    assert result == []


@patch("marker.utils.geo.urllib.request.urlopen")
def test_nominatim_search_not_list(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.read.return_value = json.dumps({"error": "bad"}).encode()
    mock_urlopen.return_value = mock_resp
    result = _nominatim_search(q="Warsaw")
    assert result == []


@patch("marker.utils.geo._nominatim_search")
def test_location_no_results(mock_search):
    mock_search.return_value = []
    assert location(q="nowhere") is None


@patch("marker.utils.geo._nominatim_search")
def test_location_success(mock_search):
    mock_search.return_value = [{"lat": "52.23", "lon": "21.01"}]
    result = location(q="Warsaw")
    assert result == {"lat": 52.23, "lon": 21.01}


@patch("marker.utils.geo._nominatim_search")
def test_location_bad_coords(mock_search):
    mock_search.return_value = [{"lat": "invalid"}]
    assert location(q="Warsaw") is None


@patch("marker.utils.geo._nominatim_search")
def test_location_details_no_results(mock_search):
    mock_search.return_value = []
    assert location_details(q="nowhere") is None


@patch("marker.utils.geo._nominatim_search")
def test_location_details_no_address(mock_search):
    mock_search.return_value = [{"lat": "52", "lon": "21"}]
    assert location_details(q="Warsaw") is None


@patch("marker.utils.geo._nominatim_search")
def test_location_details_success(mock_search):
    mock_search.return_value = [
        {
            "lat": "52.23",
            "lon": "21.01",
            "address": {
                "city": "Warsaw",
                "state": "Mazowieckie",
                "country": "Poland",
                "country_code": "pl",
                "postcode": "00-001",
            },
        }
    ]
    result = location_details(q="Warsaw")
    assert result["city"] == "Warsaw"
    assert result["state"] == "Mazowieckie"
    assert result["country_code"] == "PL"
    assert result["lat"] == 52.23


@patch("marker.utils.geo._nominatim_search")
def test_location_details_bad_lat_lon(mock_search):
    mock_search.return_value = [
        {
            "lat": "invalid",
            "lon": "bad",
            "address": {
                "city": "Test",
                "country_code": "pl",
            },
        }
    ]
    result = location_details(q="test")
    assert "lat" not in result
    assert result["city"] == "Test"


@patch("marker.utils.geo._nominatim_search")
def test_location_details_town_fallback(mock_search):
    mock_search.return_value = [
        {
            "lat": "51.0",
            "lon": "20.0",
            "address": {
                "town": "SmallTown",
                "country": "Poland",
                "country_code": "pl",
            },
        }
    ]
    result = location_details(q="SmallTown")
    assert result["city"] == "SmallTown"


@patch("marker.utils.geo._nominatim_search")
def test_location_with_keyword_params(mock_search):
    mock_search.return_value = [{"lat": "52.0", "lon": "21.0"}]
    result = location(city="Warsaw", street="Marszalkowska")
    assert result == {"lat": 52.0, "lon": 21.0}


@patch("marker.utils.geo.urllib.request.urlopen")
def test_nominatim_search_with_keyword_params(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.read.return_value = json.dumps(
        [{"lat": "52", "lon": "21", "address": {}}]
    ).encode()
    mock_urlopen.return_value = mock_resp
    result = _nominatim_search(city="Warsaw")
    assert len(result) == 1
