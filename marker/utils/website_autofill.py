import json
import os
import re
import unicodedata

os.environ["USER_AGENT"] = "MarkerBot/1.0"

import pycountry
from langchain_community.document_loaders import WebBaseLoader
from langchain_google_genai import ChatGoogleGenerativeAI

from .geo import location_details


def _clean_json_string(json_string):
    pattern = r"^```json\s*(.*?)\s*```$"
    cleaned_string = re.sub(pattern, r"\1", json_string, flags=re.DOTALL)
    return cleaned_string.strip()


def _autofill_from_website(url, prompt):
    """
    Shared logic for autofilling company or project data from a website.
    """
    # Load the content of the page
    loader = WebBaseLoader(url)
    docs = loader.load()

    # Extract just the text from the loaded document
    content = docs[0].page_content

    # Initialize Gemini model
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")

    # Make the request
    response = llm.invoke(f"{prompt}:\n\n{content}")

    # Convert the response to JSON
    result = json.loads(_clean_json_string(response.content))

    # Clean up street before geolocation (remove "ul." and "ulica" prefixes)
    street = result.get("street")
    if street:
        street = street.strip()
        street = re.sub(r"^(ulica|ul\.)\s*|^ul\s+", "", street, flags=re.IGNORECASE)
        result["street"] = street

    # Set country, subdivision, and postcode based on address using Nominatim
    geo = location_details(**result)
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
        # Set subdivision (voivodeship/state) to ISO code if possible, otherwise use state name
        if geo.get("state") and geo.get("country_code"):
            code = _subdivision_code_from_value(
                geo["state"], geo["country_code"].upper()
            )
            if code:
                result["subdivision"] = code
            else:
                result["subdivision"] = geo["state"]

    return result


def company_autofill_from_website(website):
    prompt = "Extract the following form fields from the context: name, street, postcode, city, subdivision, country, NIP, REGON, KRS. Returns only one, best-matching result as a JSON object."
    return _autofill_from_website(website, prompt)


def project_autofill_from_website(website):
    prompt = "Extract the following form fields from the context: name, street, postcode, city, subdivision, country. Returns only one, best-matching result as a JSON object."
    return _autofill_from_website(website, prompt)


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
