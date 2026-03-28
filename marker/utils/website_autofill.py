import ssl

ssl._create_default_https_context = ssl._create_unverified_context

import os
import re
import unicodedata
import urllib.parse
import urllib.request

import pycountry

from .geo import location_details
from .llm_extract import extract_fields_llm


def shorten_url_to_hostname(url):
    """
    Given a URL, return its hostname (domain) only, without scheme or path.
    If the input is already a hostname, return as is.
    """
    if not url:
        return ""
    url = url.strip()
    # Add scheme if missing for urlparse
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+\-.]*://", url):
        url = f"https://{url}"
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.hostname or url
    except Exception:
        return url


def _autofill_from_website(website, fields):
    """
    Shared logic for autofilling company or project data from a website.
    """
    try:
        with urllib.request.urlopen(website, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        raise RuntimeError(f"Error fetching website: {e}")

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is missing")

    result = extract_fields_llm(html, api_key)

    # Clean up street before geolocation (remove "ul." and "ulica" prefixes)
    street = result.get("street")
    if street:
        street = street.strip()
        street = re.sub(r"^(ulica|ul\.)\s*|^ul\s+", "", street, flags=re.IGNORECASE)
        result["street"] = street

    # Set country and subdivision (voivodeship/state) based on address using Nominatim
    address_query = " ".join(
        str(result.get(f, "")) for f in ("street", "postcode", "city") if result.get(f)
    )
    geo = location_details(q=address_query)
    if geo:
        # Set country to country code (e.g. PL)
        if geo.get("country_code"):
            result["country"] = geo["country_code"].upper()
        # Set subdivision (voivodeship/state) to ISO code if possible, otherwise use state name
        if geo.get("state") and geo.get("country_code"):
            code = _subdivision_code_from_value(
                geo["state"], geo["country_code"].upper()
            )
            if code:
                result["subdivision"] = code
            else:
                result["subdivision"] = geo["state"]

    return {field: result.get(field) for field in fields if result.get(field)}


def company_autofill_from_website(website):

    fields = (
        "name",
        "street",
        "postcode",
        "city",
        "subdivision",
        "country",
        "NIP",
        "REGON",
        "KRS",
    )
    return _autofill_from_website(website, fields)


def project_autofill_from_website(website):
    fields = (
        "name",
        "street",
        "postcode",
        "city",
        "subdivision",
        "country",
    )
    return _autofill_from_website(website, fields)


def _subdivision_code_from_value(value, country_code):
    value = _normalize_whitespace(value)
    if not value or not country_code:
        return ""

    value = re.sub(r"^(woj(?:ew[oó]dztwo)?\.?\s+)", "", value, flags=re.IGNORECASE)
    subdivisions = pycountry.subdivisions.get(country_code=country_code) or []

    for subdivision in subdivisions:
        if value.upper() == subdivision.code.upper():
            return subdivision.code

    folded = _fold_text(value)
    for subdivision in subdivisions:
        if folded == _fold_text(subdivision.name):
            return subdivision.code

    for subdivision in subdivisions:
        subdivision_folded = _fold_text(subdivision.name)
        if subdivision_folded and subdivision_folded in folded:
            return subdivision.code

    return ""


def _normalize_whitespace(value):
    return re.sub(r"\s+", " ", value or "").strip()


def _fold_text(value):
    value = _normalize_whitespace(value).casefold()
    value = value.translate(str.maketrans({"ł": "l", "đ": "d", "ø": "o", "ß": "ss"}))
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))
