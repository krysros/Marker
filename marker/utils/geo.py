from geopy.geocoders import Nominatim
from geopy.exc import GeopyError


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
            return None
    else:
        query = {key: value for key, value in kwargs.items() if _first_not_empty(value)}
        if not query:
            return None

    try:
        # Nominatim geocoder configuration
        geolocator = Nominatim(user_agent="Marker/1.0", timeout=5)
        # Call geocode with addressdetails=True to get full details for location_details
        return geolocator.geocode(query, addressdetails=True)
    except GeopyError:
        return None


def location(**kwargs):
    loc = _nominatim_search(**kwargs)
    if not loc:
        return None

    try:
        return {
            "lat": loc.latitude,
            "lon": loc.longitude,
        }
    except (AttributeError, KeyError, TypeError, ValueError):
        return None


def location_details(**kwargs):
    loc = _nominatim_search(**kwargs)
    if not loc or not isinstance(loc.raw, dict):
        return None

    first = loc.raw
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

    try:
        data["lat"] = loc.latitude
        data["lon"] = loc.longitude
    except (AttributeError, KeyError, TypeError, ValueError):
        pass

    return {key: value for key, value in data.items() if value}
