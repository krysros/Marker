import json
import os
import re
import unicodedata

os.environ["USER_AGENT"] = "Marker/1.0"

import pycountry
from langchain_community.document_loaders import WebBaseLoader
from langchain_google_genai import ChatGoogleGenerativeAI

from ..forms.ts import TranslationString as _
from .geo import location_details


def _autofill_from_website(url, prompt, model="gemini-2.5-flash-lite", default_country=""):
    """
    Shared logic for autofilling company or project data from a website.
    """
    # Load the content of the page
    loader = WebBaseLoader(url)
    docs = loader.load()
    if not docs:
        raise ValueError(str(_("Could not load content from %(url)s")) % {"url": url})

    content = docs[0].page_content

    # Initialize Gemini model with forced JSON output
    llm = ChatGoogleGenerativeAI(
        model=model,
        response_mime_type="application/json",
    )

    # Make the request
    response = llm.invoke(f"{prompt}:\n\n{content}")

    result = json.loads(response.content)

    # Clean up street before geolocation (remove "ul." and "ulica" prefixes)
    street = result.get("street")
    if street:
        street = street.strip()
        street = re.sub(r"^(ulica|ul\.)\s*|^ul\s+", "", street, flags=re.IGNORECASE)
        result["street"] = street

    # Set country, subdivision, and postcode based on address using Nominatim
    # Pass only address-relevant fields to avoid confusing Nominatim with NIP, REGON, etc.
    address_fields = {
        k: v
        for k, v in result.items()
        if k in ("street", "postcode", "city", "subdivision", "country")
    }
    geo = location_details(**address_fields)
    if geo:
        # Autofill postcode if not provided by user
        if not result.get("postcode"):
            postcode = (
                geo.get("postcode")
                or geo.get("postalcode")
                or geo.get("postal")
                or geo.get("postal_code")
            )
            if postcode:
                result["postcode"] = postcode
        # Set country to country code (e.g. PL)
        if geo.get("country_code"):
            result["country"] = geo["country_code"].upper()
        # Set subdivision (voivodeship/state) to ISO code if possible
        if geo.get("state") and geo.get("country_code"):
            code = _subdivision_code_from_value(
                geo["state"], geo["country_code"].upper()
            )
            result["subdivision"] = code if code else ""

    # Normalize country value to alpha_2 code; LLM may return "Poland", "Polska", etc.
    # Fall back to default_country (derived from app locale) if value cannot be resolved.
    country_val = (result.get("country") or "").strip()
    if pycountry.countries.get(alpha_2=country_val.upper()):
        result["country"] = country_val.upper()
    else:
        country_obj = None
        if country_val:
            try:
                matches = pycountry.countries.search_fuzzy(country_val)
                if matches:
                    country_obj = matches[0]
            except LookupError:
                pass
        result["country"] = country_obj.alpha_2 if country_obj else default_country

    return result


def _country_from_locale(locale_str):
    """Derive ISO alpha_2 country code from a locale string (e.g. 'pl' → 'PL', 'pl_PL' → 'PL').
    First tries babel's territory (handles 'pl_PL', 'de_DE', etc.), then checks if the
    uppercase language code is itself a valid country alpha_2 (covers 'pl'→'PL', 'de'→'DE', etc.).
    Returns '' if the locale cannot be mapped to a country.
    """
    if not locale_str:
        return ""
    try:
        from babel import Locale
        locale = Locale.parse(locale_str, sep="_")
        if locale.territory:
            return locale.territory
    except Exception:
        pass
    # Fallback: check if the language code is also a valid country code (pl→PL, de→DE, fr→FR…)
    lang = locale_str.split("_")[0].split("-")[0].upper()
    if pycountry.countries.get(alpha_2=lang):
        return lang
    return ""


def company_autofill_from_website(website, model="gemini-2.5-flash-lite", default_country=""):
    prompt = "Extract the following form fields from the context: name, street, postcode, city, subdivision, country, NIP, REGON, KRS. Returns only one, best-matching result as a JSON object."
    return _autofill_from_website(website, prompt, model=model, default_country=default_country)


def project_autofill_from_website(website, model="gemini-2.5-flash-lite", default_country=""):
    prompt = "Extract the following form fields from the context: name, street, postcode, city, subdivision, country. Returns only one, best-matching result as a JSON object."
    return _autofill_from_website(website, prompt, model=model, default_country=default_country)


def contacts_autofill_from_website(website, model="gemini-2.5-flash-lite"):
    """
    Extract a list of contacts (people) from the given website URL.
    In addition to the main URL, tries common contact sub-pages
    (/kontakt, /contact, etc.) to improve extraction quality.
    Returns a list of dicts with keys: name, role, phone, email.
    """
    from urllib.parse import urljoin, urlparse

    parsed = urlparse(website)
    root = f"{parsed.scheme}://{parsed.netloc}"

    content_parts = []

    # Load the main page
    try:
        docs = WebBaseLoader(website).load()
        if docs and docs[0].page_content.strip():
            content_parts.append(docs[0].page_content)
    except Exception:
        pass

    # Also try a contact-like sub-page for better people extraction
    contact_paths = ["/kontakt", "/contact", "/zespol", "/team", "/o-nas", "/about"]
    for path in contact_paths:
        url = urljoin(root, path)
        if url.rstrip("/") == website.rstrip("/"):
            continue
        try:
            docs = WebBaseLoader(url).load()
            if docs and len(docs[0].page_content.strip()) > 200:
                content_parts.append(docs[0].page_content)
                break
        except Exception:
            continue

    if not content_parts:
        raise ValueError(str(_("Could not load content from %(url)s")) % {"url": website})

    content = "\n\n---\n\n".join(content_parts[:2])

    llm = ChatGoogleGenerativeAI(
        model=model,
        response_mime_type="application/json",
    )

    prompt = (
        "Extract a list of contacts (people) from the context. "
        "For each contact provide: name, role, phone, email. "
        'Return a JSON array of objects, e.g. [{"name": "...", "role": "...", "phone": "...", "email": "..."}]. '
        "If no contacts are found, return an empty array []."
    )

    response = llm.invoke(f"{prompt}:\n\n{content}")
    result = json.loads(response.content)

    if isinstance(result, list):
        return result
    # Gemini sometimes wraps the array in a dict
    if isinstance(result, dict):
        for key in ("contacts", "people", "results", "data"):
            if key in result and isinstance(result[key], list):
                return result[key]
    return []


def tags_autofill_from_website(website, existing_tags=None, model="gemini-2.5-flash-lite"):
    """
    Extract a list of tags (core business activities or project types) from the
    given website URL.  When *existing_tags* (a list of tag name strings already
    present in the database) is supplied, the LLM is instructed to prefer those
    exact names over inventing new ones.
    Returns a list of up to 20 tag name strings.
    """
    from urllib.parse import urljoin, urlparse

    parsed = urlparse(website)
    root = f"{parsed.scheme}://{parsed.netloc}"
    content_parts = []

    # Load the main page
    try:
        docs = WebBaseLoader(website).load()
        if docs and docs[0].page_content.strip():
            content_parts.append(docs[0].page_content)
    except Exception:
        pass

    # Also try an "about" or "offer" sub-page for richer activity descriptions
    extra_paths = ["/oferta", "/offer", "/uslugi", "/services", "/o-nas", "/about"]
    for path in extra_paths:
        url = urljoin(root, path)
        if url.rstrip("/") == website.rstrip("/"):
            continue
        try:
            docs = WebBaseLoader(url).load()
            if docs and len(docs[0].page_content.strip()) > 200:
                content_parts.append(docs[0].page_content)
                break
        except Exception:
            continue

    if not content_parts:
        raise ValueError(str(_("Could not load content from %(url)s")) % {"url": website})

    content = "\n\n---\n\n".join(content_parts[:2])

    llm = ChatGoogleGenerativeAI(
        model=model,
        response_mime_type="application/json",
    )

    existing_section = ""
    if existing_tags:
        # Pass at most 500 existing names to keep the prompt manageable
        sample = existing_tags[:500]
        existing_section = (
            f" The following tags already exist in the database: {json.dumps(sample, ensure_ascii=False)}."
            " Where possible, reuse an existing tag name exactly (same spelling) instead of creating a new one."
            " Only propose a new name when none of the existing tags adequately describes the activity or type."
        )

    prompt = (
        "Extract up to 20 tags that best describe the core business activities (for a company) "
        "or project types (for a project) based on the context."
        + existing_section
        + ' Return a JSON array of strings, e.g. ["Construction", "Real estate", "Project management"].'
        " Return at most 20 items. If nothing can be determined, return an empty array []."
    )

    response = llm.invoke(f"{prompt}:\n\n{content}")
    result = json.loads(response.content)

    if isinstance(result, list):
        return [str(t).strip() for t in result if str(t).strip()][:20]
    # Gemini sometimes wraps in a dict
    if isinstance(result, dict):
        for key in ("tags", "items", "results", "data"):
            if key in result and isinstance(result[key], list):
                return [str(t).strip() for t in result[key] if str(t).strip()][:20]
    return []


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
