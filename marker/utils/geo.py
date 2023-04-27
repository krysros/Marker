import json
import urllib.error
import urllib.parse
import urllib.request


def location(**kwargs):
    """
    See: https://nominatim.org/release-docs/latest/api/Search/#parameters
    Geocoding Policy: https://operations.osmfoundation.org/policies/nominatim/
    """
    if "q" in kwargs:
        query = urllib.parse.quote(kwargs["q"])
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
    else:
        params = urllib.parse.urlencode(kwargs)
        url = f"https://nominatim.openstreetmap.org/search?{params}&format=json"
    try:
        with urllib.request.urlopen(url) as f:
            res = json.load(f)
    except urllib.error.URLError:
        loc = None
    try:
        fst = res[0]
        lat = fst["lat"]
        lon = fst["lon"]
        loc = {"lat": float(lat), "lon": float(lon)}
    except (IndexError, UnboundLocalError):
        loc = None
    return loc
