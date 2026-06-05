import json
import os
import re
import unicodedata
from urllib.parse import urljoin, urlparse

os.environ["USER_AGENT"] = "Marker/1.0"

import pycountry
from .langchain_ai import invoke_text

from ..forms.ts import TranslationString as _
from .geo import location_details
from .llm_report import get_configured_model, _get_locale


class WebBaseLoader:
    """
    A lightweight, robust, custom replacement for langchain_community's WebBaseLoader.
    Uses Python's standard urllib.request to fetch the page and BeautifulSoup to extract text.
    Respects charset encodings and handles Unicode seamlessly.
    """

    def __init__(self, url):
        self.url = url

    def load(self):
        import urllib.request
        from bs4 import BeautifulSoup

        user_agent = os.environ.get("USER_AGENT", "Marker/1.0")
        req = urllib.request.Request(self.url, headers={"User-Agent": user_agent})

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                raw_data = response.read()
                try:
                    html = raw_data.decode(charset, errors="replace")
                except Exception:
                    html = raw_data.decode("utf-8", errors="replace")
        except Exception as e:
            raise ValueError(f"Could not load content from {self.url}: {e}")

        soup = BeautifulSoup(html, "html.parser")
        for element in soup(["script", "style"]):
            element.decompose()

        text = soup.get_text(separator="\n", strip=True)

        class Document:
            def __init__(self, page_content):
                self.page_content = page_content

        return [Document(text)]


def _autofill_from_website(url, prompt, default_country=""):
    """
    Shared logic for autofilling company or project data from a website.
    """
    model = get_configured_model()
    # Load the content of the page
    loader = WebBaseLoader(url)
    docs = loader.load()
    if not docs:
        raise ValueError(str(_("Could not load content from %(url)s")) % {"url": url})

    content = docs[0].page_content

    # Make the request with full retry and backoff support
    response_text = invoke_text(
        prompt=f"{prompt}:\n\n{content}",
        model=model,
        response_mime_type="application/json",
        source="website_autofill_main",
    )

    result = json.loads(response_text)

    # Handle case where LLM returns an array instead of an object
    if isinstance(result, list):
        if result and isinstance(result[0], dict):
            result = result[0]
        else:
            raise ValueError(
                str(_("Invalid response format from AI: expected a JSON object"))
            )

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


def company_autofill_from_website(website, default_country="", locale=None):
    loc = _get_locale(locale)
    if loc.startswith("pl"):
        prompt = (
            "Wyodrębnij z kontekstu następujące pola formularza: name (nazwa firmy), "
            "street (ulica bez przedrostków ul./ulica), postcode (kod pocztowy), "
            "city (nazwa miasta przetłumaczona na język polski, np. 'Berlin', 'Londyn', 'Warszawa'), "
            "subdivision (województwo/region), country (kraj), NIP, REGON, KRS. "
            "Zwróć tylko jeden, najlepiej pasujący wynik jako obiekt JSON."
        )
    else:
        prompt = (
            "Extract the following form fields from the context: name (company name), "
            "street (street address), postcode (postcode), "
            "city (city name translated to English, e.g., 'Warsaw', 'London', 'Berlin'), "
            "subdivision (subdivision/state/region), country (country), NIP, REGON, KRS. "
            "Returns only one, best-matching result as a JSON object."
        )
    return _autofill_from_website(website, prompt, default_country=default_country)


def project_autofill_from_website(website, default_country="", locale=None):
    loc = _get_locale(locale)
    if loc.startswith("pl"):
        prompt = (
            "Wyodrębnij z kontekstu następujące pola formularza: name (nazwa projektu), "
            "street (ulica bez przedrostków ul./ulica), postcode (kod pocztowy), "
            "city (nazwa miasta przetłumaczona na język polski, np. 'Berlin', 'Londyn', 'Warszawa'), "
            "subdivision (województwo/region), country (kraj). "
            "Zwróć tylko jeden, najlepiej pasujący wynik jako obiekt JSON."
        )
    else:
        prompt = (
            "Extract the following form fields from the context: name (project name), "
            "street (street address), postcode (postcode), "
            "city (city name translated to English, e.g., 'Warsaw', 'London', 'Berlin'), "
            "subdivision (subdivision/state/region), country (country). "
            "Returns only one, best-matching result as a JSON object."
        )
    return _autofill_from_website(website, prompt, default_country=default_country)


def contacts_autofill_from_website(website, locale=None):
    """
    Extract a list of contacts (people) from the given website URL.
    In addition to the main URL, tries common contact sub-pages
    (/kontakt, /contact, etc.) to improve extraction quality.
    Returns a list of dicts with keys: name, role, phone, email.
    """
    model = get_configured_model()
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
        raise ValueError(
            str(_("Could not load content from %(url)s")) % {"url": website}
        )

    content = "\n\n---\n\n".join(content_parts[:2])

    # Model will be invoked later with exponential backoff support

    # Identify a backup company name from the website domain
    fallback_company_name = ""
    try:
        domain = parsed.netloc or parsed.path
        if domain.startswith("www."):
            domain = domain[4:]
        parts = domain.split(".")
        if len(parts) > 1:
            fallback_company_name = parts[0].capitalize()
        else:
            fallback_company_name = domain.capitalize()
    except Exception:
        fallback_company_name = ""

    loc = _get_locale(locale)
    if loc.startswith("pl"):
        role_guideline = (
            "Zachowaj stanowiska/role ('role') w DOKŁADNEJ formie i języku, w jakim występują na stronie internetowej. "
            "NIE tłumacz ich na angielski ani inny język, chyba że są tak zapisane na stronie. "
            "Popraw tylko oczywiste literówki. NIE wymyślaj ani nie twórz własnych określeń (np. zachowaj 'Dyrektor' jako 'Dyrektor', "
            "nie tłumacz na 'Director' ani nie wymyślaj innych ról)."
        )
        name_fallback_guideline = (
            f"Jeśli konkretna osoba kontaktowa (imię i nazwisko) NIE zostanie wyodrębniona lub znaleziona, "
            f"ale dostępne są informacje kontaktowe (takie jak telefon lub e-mail), użyj nazwy firmy jako 'name' kontaktu. "
            f"Zidentyfikuj nazwę firmy z kontekstu strony. Jeśli nie możesz znaleźć nazwy firmy, użyj '{fallback_company_name or 'nazwa firmy'}' "
            f"jako rezerwowej wartości 'name'. Nie pozostawiaj pola 'name' pustego ani nie pomijaj kontaktu, jeśli dane kontaktowe są obecne."
        )
        prompt = (
            "Wyodrębnij listę kontaktów z kontekstu.\n"
            "Dla każdego kontaktu podaj: name, role, phone, email.\n\n"
            "Zasady:\n"
            f"1. {name_fallback_guideline}\n"
            f"2. {role_guideline}\n"
            "3. Zwróć tablicę obiektów JSON, np. "
            '[{"name": "...", "role": "...", "phone": "...", "email": "..."}]. '
            "Jeśli nie znaleziono kontaktów, zwróć pustą tablicę []."
        )
    else:
        role_guideline = (
            "Provide job titles/roles ('role') in the EXACT form and language in which they appear on the website. "
            "Do NOT translate them to English or any other language unless they are originally written that way on the website. "
            "Correct only obvious typos/spelling mistakes. Do NOT invent, fabricate, or use your own terms or titles (e.g. keep 'Dyrektor' as 'Dyrektor', "
            "do not translate to 'Director' or make up other roles)."
        )
        name_fallback_guideline = (
            f"If a specific contact person (first and last name) is NOT extracted or found, but contact information (such as phone or email) "
            f"is available, use the company name as the contact's 'name'. Identify the company name from the page context. "
            f"If you cannot find the company name, use '{fallback_company_name or 'the company name'}' as the fallback 'name'. "
            f"Do not leave the 'name' field blank or skip the contact entry if contact details are present."
        )
        prompt = (
            "Extract a list of contacts from the context.\n"
            "For each contact provide: name, role, phone, email.\n\n"
            "Strict Guidelines:\n"
            f"1. {name_fallback_guideline}\n"
            f"2. {role_guideline}\n"
            "3. Returns a JSON array of objects, e.g. "
            '[{"name": "...", "role": "...", "phone": "...", "email": "..."}]. '
            "If no contacts are found, return an empty array []."
        )

    response_text = invoke_text(
        prompt=f"{prompt}:\n\n{content}",
        model=model,
        response_mime_type="application/json",
        source="website_autofill_contacts",
    )
    result = json.loads(response_text)

    contacts_list = []
    if isinstance(result, list):
        contacts_list = result
    elif isinstance(result, dict):
        for key in ("contacts", "people", "results", "data"):
            if key in result and isinstance(result[key], list):
                contacts_list = result[key]
                break
        else:
            if any(k in result for k in ("name", "role", "phone", "email")):
                contacts_list = [result]

    final_contacts = []
    for c in contacts_list:
        if not isinstance(c, dict):
            continue
        name = (c.get("name") or "").strip()
        role = c.get("role")
        if isinstance(role, str):
            role = role.strip()
        else:
            role = None

        phone = c.get("phone")
        if isinstance(phone, str):
            phone = phone.strip()
        else:
            phone = None

        email = c.get("email")
        if isinstance(email, str):
            email = email.strip()
        else:
            email = None

        # Apply fallback company name if name is empty but contact has other details
        if not name and (role or phone or email):
            name = fallback_company_name or "Company"

        if name:
            final_contacts.append(
                {"name": name, "role": role, "phone": phone, "email": email}
            )

    return final_contacts


_AVOID_TAGS_BY_LOCALE = {
    "pl": {
        "budowa",
        "jakość",
        "kierowanie projektem",
        "budownictwo",
        "budownictwo ogólne",
        "technologia",
        "certyfikaty",
        "energooszczędność",
    },
    "en": {
        "construction",
        "quality",
        "project management",
        "general construction",
        "technology",
        "certificates",
        "energy efficiency",
        "about",
        "contact",
        "services",
        "home",
    },
}


def _is_meaningless_tag(tag: str, locale: str | None = None) -> bool:
    loc = _get_locale(locale)
    # Check if the resolved locale starts with "pl"
    target_key = "pl" if loc.startswith("pl") else "en"
    avoid_set = _AVOID_TAGS_BY_LOCALE.get(target_key, _AVOID_TAGS_BY_LOCALE["en"])
    return tag.strip().lower() in avoid_set


def tags_autofill_from_website(website, existing_tags=None, locale=None):
    """
    Extract a list of tags (core business activities or project types) from the
    given website URL.  When *existing_tags* (a list of tag name strings already
    present in the database) is supplied, the LLM is instructed to prefer those
    exact names over inventing new ones.
    Returns a list of up to 10 tag name strings.
    """
    model = get_configured_model()
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
        raise ValueError(
            str(_("Could not load content from %(url)s")) % {"url": website}
        )

    content = "\n\n---\n\n".join(content_parts[:2])

    # Model will be invoked later with exponential backoff support

    loc = _get_locale(locale)
    existing_section = ""
    if existing_tags:
        # Pass at most 500 existing names to keep the prompt manageable
        sample = existing_tags[:500]
        if loc.startswith("pl"):
            existing_section = (
                f" Następujące tagi już istnieją w bazie danych: {json.dumps(sample, ensure_ascii=False)}."
                " Jeśli to możliwe, użyj dokładnie istniejącej nazwy tagu (identyczna pisownia) zamiast tworzyć nowy."
                " Zaproponuj nową nazwę tylko wtedy, gdy żaden z istniejących tagów nie opisuje odpowiednio działalności lub typu."
            )
        else:
            existing_section = (
                f" The following tags already exist in the database: {json.dumps(sample, ensure_ascii=False)}."
                " Where possible, reuse an existing tag name exactly (same spelling) instead of creating a new one."
                " Only propose a new name when none of the existing tags adequately describes the activity or type."
            )

    if loc.startswith("pl"):
        avoid_tags_str = "'budowa', 'jakość', 'kierowanie projektem', 'budownictwo', 'budownictwo ogólne', 'technologia', 'certyfikaty', 'energooszczędność' i tym podobne mało wartościowe lub zbyt ogólne określenia"
        example_str = '["Klimatyzacja", "Usługi instalacyjne", "Projektowanie dróg"]'
        prompt = (
            "Wyodrębnij do 20 tagów, które najlepiej opisują główną działalność biznesową (dla firmy) "
            "lub typy projektów (dla projektu) na podstawie kontekstu.\n"
            "Wskazówki:\n"
            f"1. Kategorycznie unikaj bezużytecznych lub ogólnych tagów (zazwyczaj jednowyrazowych), takich jak: {avoid_tags_str}.\n"
            "2. Wybierz konkretne tagi opisujące główny/podstawowy zakres działalności lub specyficzny typ projektu (np. 'instalacje elektryczne', 'konstrukcje stalowe', 'generalne wykonawstwo').\n"
            f"{existing_section}\n"
            f"Zwróć tablicę JSON zawierającą ciągi znaków, np. {example_str}.\n"
            "Zwróć maksymalnie 20 elementów. Jeśli nie można nic ustalić, zwróć pustą tablicę []."
        )
    else:
        avoid_tags_str = "'construction', 'quality', 'project management', 'general construction', 'technology', 'certificates', 'energy efficiency' and similar low-value or overly broad terms"
        example_str = '["Air conditioning", "Installation services", "Road design"]'
        prompt = (
            "Extract up to 20 tags that best describe the core business activities (for a company) "
            "or project types (for a project) based on the context.\n"
            "Strict Guidelines:\n"
            f"1. Strictly avoid meaningless or generic tags (usually single words), such as: {avoid_tags_str}.\n"
            "2. Select specific tags describing the core/primary scope of business activity or specific project type (e.g. 'electrical installations', 'steel structures', 'general contracting').\n"
            f"{existing_section}\n"
            f"Return a JSON array of strings, e.g. {example_str}.\n"
            "Return at most 20 items. If nothing can be determined, return an empty array []."
        )

    response_text = invoke_text(
        prompt=f"{prompt}:\n\n{content}",
        model=model,
        response_mime_type="application/json",
        source="website_autofill_tags",
    )
    result = json.loads(response_text)

    tags = []
    if isinstance(result, list):
        tags = [str(t).strip() for t in result if str(t).strip()]
    elif isinstance(result, dict):
        for key in ("tags", "items", "results", "data"):
            if key in result and isinstance(result[key], list):
                tags = [str(t).strip() for t in result[key] if str(t).strip()]
                break

    filtered_tags = [t for t in tags if t and not _is_meaningless_tag(t, locale=locale)]
    return filtered_tags[:10]


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
