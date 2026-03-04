import json
import urllib.error
import urllib.parse
import urllib.request

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
REQUEST_HEADERS = {
    "User-Agent": "MarkerBot/1.0",
    "Accept": "application/json",
}


def _first_not_empty(*values):
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _nominatim_search(**kwargs):
    """
    See: https://nominatim.org/release-docs/latest/api/Search/
    Geocoding Policy: https://operations.osmfoundation.org/policies/nominatim/
    """
    if "q" in kwargs:
        query = _first_not_empty(kwargs.get("q"))
        if not query:
            return []
        params = {"q": query}
    else:
        params = {
            key: value
            for key, value in kwargs.items()
            if _first_not_empty(value)
        }
        if not params:
            return []

    params.update(
        {
            "format": "json",
            "addressdetails": 1,
            "limit": 1,
        }
    )
    url = f"{NOMINATIM_URL}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers=REQUEST_HEADERS)
    try:
        with urllib.request.urlopen(request) as response:
            payload = json.load(response)
    except (urllib.error.URLError, json.JSONDecodeError, ValueError):
        return []

    if not isinstance(payload, list):
        return []
    return payload


def location(**kwargs):
    results = _nominatim_search(**kwargs)
    if not results:
        return None

    first = results[0]
    try:
        return {
            "lat": float(first["lat"]),
            "lon": float(first["lon"]),
        }
    except (KeyError, TypeError, ValueError):
        return None


def location_details(**kwargs):
    results = _nominatim_search(**kwargs)
    if not results:
        return None

    first = results[0]
    address = first.get("address") if isinstance(first, dict) else None
    if not isinstance(address, dict):
        return None

    city = _first_not_empty(
        address.get("city"),
        address.get("town"),
        address.get("village"),
        address.get("municipality"),
        address.get("county"),
    )
    state = _first_not_empty(
        address.get("state"),
        address.get("region"),
        address.get("state_district"),
        address.get("province"),
    )
    country = _first_not_empty(address.get("country"))
    country_code = _first_not_empty(address.get("country_code")).upper()
    postcode = _first_not_empty(address.get("postcode"))

    data = {
        "city": city,
        "state": state,
        "country": country,
        "country_code": country_code,
        "postcode": postcode,
    }

    if isinstance(first, dict):
        try:
            data["lat"] = float(first["lat"])
            data["lon"] = float(first["lon"])
        except (KeyError, TypeError, ValueError):
            pass

    return {key: value for key, value in data.items() if value}
