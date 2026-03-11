import ipaddress
import json
import re
import socket
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from html import unescape

import pycountry
from bs4 import BeautifulSoup

from ..forms.select import COURTS
from .geo import location_details

_MAX_HTML_BYTES = 500_000
_TIMEOUT = 5
_MAX_COMPANY_NAME_LEN = 100
_MAX_PROJECT_NAME_LEN = 200
_MAX_STREET_LEN = 100
_MAX_POSTCODE_LEN = 10
_MAX_CITY_LEN = 100
_NAME_SEPARATORS = (" | ", " - ", " – ", " — ", " • ")
_ORG_TYPES = {
    "organization",
    "localbusiness",
    "corporation",
    "ngo",
    "educationalorganization",
    "governmentorganization",
    "project",
}
_COURTS = [(code, label) for code, label in COURTS if code]
_COUNTRY_ALIASES = {
    "polska": "PL",
    "poland": "PL",
    "deutschland": "DE",
    "niemcy": "DE",
    "czech republic": "CZ",
    "czechia": "CZ",
    "czechy": "CZ",
    "slovakia": "SK",
    "slowacja": "SK",
    "uk": "GB",
    "wielka brytania": "GB",
    "united kingdom": "GB",
}
_POSTCODE_RE = re.compile(r"\b\d{2}[\-–—]?\d{3}\b")
_POSTCODE_CITY_LINE_RE = re.compile(
    r"\b(?P<postcode>\d{2}[\-–—]?\d{3})\s+(?P<city>[A-Za-zÀ-ÖØ-öø-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻż][A-Za-zÀ-ÖØ-öø-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻż\-\s]{1,80})$"
)
_CITY_POSTCODE_LINE_RE = re.compile(
    r"^(?P<city>[A-Za-zÀ-ÖØ-öø-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻż][A-Za-zÀ-ÖØ-öø-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻż\-\s]{1,80})\s+(?P<postcode>\d{2}[\-–—]?\d{3})\b"
)
_ADDRESS_LINE_RE = re.compile(
    r"(?:adres(?:\s+siedziby)?|siedziba)\s*[:\-]\s*([^\n|]{6,160})",
    re.IGNORECASE,
)
_ADDRESS_ONLY_LABEL_RE = re.compile(
    r"^(?:adres(?:\s+siedziby)?|siedziba)\s*[:\-]?\s*$",
    re.IGNORECASE,
)
_ADDRESS_PART_SPLIT_RE = re.compile(r"\s*,\s*")
_STREET_RE = re.compile(
    r"\b(?:ulica|ul\.?)\s*([^\n,;|]{3,100})",
    re.IGNORECASE,
)
_NIP_RE = re.compile(
    r"\b(?:NIP|VAT(?:\s*UE)?)\s*[:#]?\s*(?:PL\s*)?([0-9][0-9\s\-]{8,20})",
    re.IGNORECASE,
)
_REGON_RE = re.compile(r"\bREGON\s*[:#]?\s*([0-9][0-9\s\-]{7,20})", re.IGNORECASE)
_KRS_RE = re.compile(r"\bKRS\s*[:#]?\s*([0-9][0-9\s\-]{8,20})", re.IGNORECASE)
_NAME_TAIL_RE = re.compile(
    r"(?:"
    r",?\s*\b(?:ul\.?|ulica|al\.?|aleja|plac|pl\.?|os\.?|adres|nip|regon|krs|tel\.?|telefon|e-?mail|kontakt|infolinia|z\s+siedzib[aą])\b"
    r"|,\s*\d{2}[\-–—]?\d{3}\b"
    r"|,\s*[A-Za-zÀ-ÖØ-öø-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻż][A-Za-zÀ-ÖØ-öø-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻż0-9\-\s]{1,80}\d+[A-Za-z0-9/\-]*\b"
    r"|https?://"
    r"|www\."
    r")",
    re.IGNORECASE,
)
_LEGAL_FORM_PATTERNS_BY_COUNTRY = {
    "PL": (
        r"\bsp\.?\s*z\.?\s*o\.?\s*o\.?\b",
        r"(?:\bp\.\s*s\.\s*a\.?\b|\bp\.s\.a\.?\b)",
        r"\bsp\.?\s*j\.?\b",
        r"\bsp\.?\s*p\.?\b",
        r"\bsp\.?\s*k\.?\b",
        r"(?:\bs\.\s*k\.\s*a\.?\b|\bs\.k\.a\.?\b)",
        r"(?:\bs\.\s*c\.?\b|\bs\.c\.?\b)",
        r"(?:\bs\.\s*a\.?\b|\bs\.a\.?\b)",
        r"\bspolka\s+z\s+ograniczona\s+odpowiedzialnoscia\b",
        r"\bprosta\s+spolka\s+akcyjna\b",
        r"\bspolka\s+komandytowo[-\s]*akcyjna\b",
        r"\bspolka\s+akcyjna\b",
        r"\bspolka\s+jawna\b",
        r"\bspolka\s+partnerska\b",
        r"\bspolka\s+komandytowa\b",
        r"\bspolka\s+cywilna\b",
    ),
    "GB": (
        r"\bltd\.?\b",
        r"\blimited\b",
        r"\bplc\b",
    ),
    "US": (
        r"\bl\.?\s*l\.?\s*c\.?\b",
        r"\bl\.?\s*l\.?\s*p\.?\b",
        r"(?:\binc\.?\b|\bincorporated\b)",
        r"(?:\bcorp\.?\b|\bcorporation\b)",
    ),
    "DE": (r"\bgmbh\b",),
    "FR": (
        r"\bs\.?\s*a\.?\s*s\.?\b",
        r"\bs\.?\s*a\.?\s*r\.?\s*l\.?\b",
    ),
    "IT": (
        r"(?:\bs\.\s*p\.\s*a\.?\b|\bs\.p\.a\.?\b)",
        r"\bs\.?\s*r\.?\s*l\.?\b",
    ),
    "DK": (r"\ba\s*/\s*s\b",),
    "HU": (r"\bkft\.?\b",),
    "EE": (r"\bo\.?\s*u\.?\b",),
    "NL": (
        r"\bb\.?\s*v\.?\b",
        r"\bn\.?\s*v\.?\b",
    ),
    "BE": (
        r"\bb\.?\s*v\.?\b",
        r"\bn\.?\s*v\.?\b",
    ),
    "SG": (r"\bpte\.?\s+ltd\.?\b",),
    "IN": (r"\bpvt\.?\s+ltd\.?\b",),
}
_LEGAL_FORM_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in dict.fromkeys(
        pattern
        for country_patterns in _LEGAL_FORM_PATTERNS_BY_COUNTRY.values()
        for pattern in country_patterns
    )
)
_COMPANY_DESCRIPTOR_PATTERNS = (
    re.compile(r"\bdeweloper\b"),
    re.compile(r"\bdeveloper\b"),
)
_COMPANY_PREFIX_PATTERNS = (
    re.compile(r"\bf\.?\s*h\.?\s*u\.?\b"),
    re.compile(r"\bp\.?\s*p\.?\s*h\.?\s*u\.?\b"),
    re.compile(r"\bp\.?\s*h\.?\s*u\.?\b"),
    re.compile(r"\bp\.?\s*u\.?\s*h\.?\b"),
    re.compile(r"\bfirma\s+handlowo(?:[-\s]+)uslugowa\b"),
    re.compile(r"\bfirma\s+uslugowo(?:[-\s]+)handlowa\b"),
    re.compile(r"\bprzedsiebiorstwo\s+handlowo(?:[-\s]+)uslugowe\b"),
    re.compile(r"\bprzedsiebiorstwo\s+uslugowo(?:[-\s]+)handlowe\b"),
    re.compile(
        r"\bprzedsiebiorstwo\s+produkcyjno(?:[-\s]+)handlowo(?:[-\s]+)uslugowe\b"
    ),
    re.compile(
        r"\bprzedsiebiorstwo\s+produkcyjno(?:[-\s]+)uslugowo(?:[-\s]+)handlowe\b"
    ),
)
_NON_NAME_LINE_KEYWORDS = (
    "kontakt",
    "contact",
    "adres",
    "address",
    "telefon",
    "phone",
    "email",
    "e-mail",
    "nip",
    "regon",
    "krs",
    "www",
    "http",
)
_NAME_CASE_TOKEN_RE = re.compile(
    r"[A-Za-zÀ-ÖØ-öø-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻż][A-Za-zÀ-ÖØ-öø-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻż0-9\-]*"
)
_NAME_CASE_STOPWORDS = {
    "i",
    "oraz",
    "and",
    "or",
    "of",
    "the",
    "for",
    "to",
    "z",
    "ze",
    "w",
    "we",
    "na",
    "do",
    "de",
    "da",
    "di",
    "del",
    "van",
    "von",
    "la",
    "le",
    "el",
}


def _parse_html_document(html):
    soup = BeautifulSoup(html or "", "html.parser")
    json_ld = _extract_json_ld(soup)

    title_tag = soup.find("title")
    title = _normalize_whitespace(
        title_tag.get_text(" ", strip=True) if title_tag else ""
    )

    meta = {}
    for meta_tag in soup.find_all("meta"):
        key = _normalize_whitespace(
            meta_tag.get("property") or meta_tag.get("name") or ""
        ).lower()
        content = _normalize_whitespace(meta_tag.get("content") or "")
        if key and content and key not in meta:
            meta[key] = content

    for tag in soup.find_all(["script", "style", "noscript"]):
        tag.decompose()

    raw_text = soup.get_text("\n")
    visible_lines = []
    for raw_line in raw_text.splitlines():
        line = _normalize_whitespace(raw_line)
        if line:
            visible_lines.append(line)

    visible_text = _normalize_whitespace(" ".join(visible_lines))
    return {
        "title": title,
        "meta": meta,
        "visible_lines": visible_lines,
        "visible_text": visible_text,
        "json_ld": json_ld,
    }


def company_autofill_from_website(website):
    data = _extract_autofill_data(
        website,
        max_name_length=_MAX_COMPANY_NAME_LEN,
        prefer_legal_name=True,
    )
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
        "court",
    )
    return {field: data[field] for field in fields if data.get(field)}


def project_autofill_from_website(website):
    data = _extract_autofill_data(
        website,
        max_name_length=_MAX_PROJECT_NAME_LEN,
        prefer_legal_name=False,
    )
    fields = (
        "name",
        "street",
        "postcode",
        "city",
        "subdivision",
        "country",
    )
    return {field: data[field] for field in fields if data.get(field)}


def _extract_autofill_data(website, max_name_length, prefer_legal_name=True):
    url = _normalize_url(website)
    if not url:
        return {}

    html = ""
    final_url = url
    downloaded = _download_html(url, timeout=_TIMEOUT)
    if downloaded:
        html, final_url = downloaded

    parsed = _parse_html_document(html)
    json_ld = parsed["json_ld"]
    folded_text = _fold_text(parsed["visible_text"])

    hostname = urllib.parse.urlparse(final_url).hostname or ""
    country_code = _country_code_from_value(
        _first_not_empty(
            _jsonld_value(json_ld, "addressCountry"),
            _jsonld_value(json_ld, "country"),
            _meta_country(parsed["meta"]),
        )
    )
    if not country_code:
        country_code = _country_code_from_hostname(hostname)
    address_block = _extract_name_address_block(parsed["visible_lines"])

    address = _extract_address(
        json_ld,
        parsed["visible_text"],
        parsed["visible_lines"],
        country_code,
        address_block=address_block,
    )

    if not country_code:
        country_code = _country_code_from_value(
            _first_not_empty(
                address.get("country_code"),
                address.get("country"),
            )
        )

    region_value = _first_not_empty(
        _jsonld_value(json_ld, "addressRegion"),
        _jsonld_value(json_ld, "region"),
        address.get("state"),
    )
    subdivision_code = _subdivision_code_from_value(region_value, country_code)
    if not subdivision_code and country_code:
        subdivision_code = _subdivision_code_from_text(
            country_code, _fold_text(address.get("state"))
        )
    if not subdivision_code and country_code:
        subdivision_code = _subdivision_code_from_text(country_code, folded_text)

    if prefer_legal_name:
        name_value = _select_preferred_name(
            candidates=[
                _organization_name(json_ld),
                address_block.get("name"),
                *_visible_legal_name_candidates(parsed["visible_lines"], hostname),
                parsed["meta"].get("og:site_name"),
                parsed["meta"].get("application-name"),
                parsed["title"],
                _hostname_name(hostname),
            ],
            hostname=hostname,
        )
    else:
        name_value = _first_not_empty(
            parsed["title"],
            parsed["meta"].get("og:site_name"),
            parsed["meta"].get("application-name"),
            _jsonld_value(json_ld, "name"),
            _hostname_name(hostname),
        )

    nip_value = _first_not_empty(
        _jsonld_value(json_ld, "taxID"),
        _jsonld_value(json_ld, "vatID"),
        _jsonld_value(json_ld, "vatNumber"),
        _extract_by_regex(_NIP_RE, parsed["visible_text"]),
    )
    regon_value = _first_not_empty(
        _jsonld_value(json_ld, "regon"),
        _extract_by_regex(_REGON_RE, parsed["visible_text"]),
    )
    krs_value = _first_not_empty(
        _jsonld_value(json_ld, "krs"),
        _extract_by_regex(_KRS_RE, parsed["visible_text"]),
    )
    court_value = _court_code_from_text(parsed["visible_text"])

    result = {
        "name": _sanitize_name(
            name_value,
            max_name_length,
            split_on_separators=prefer_legal_name,
        ),
        "street": _sanitize_street(address.get("street"), max_len=_MAX_STREET_LEN),
        "postcode": _sanitize_postcode(
            address.get("postcode"), max_len=_MAX_POSTCODE_LEN
        ),
        "city": _sanitize_city(address.get("city"), max_len=_MAX_CITY_LEN),
        "country": country_code,
        "subdivision": subdivision_code,
        "NIP": _sanitize_nip(nip_value),
        "REGON": _sanitize_regon(regon_value),
        "KRS": _sanitize_krs(krs_value),
        "court": court_value,
    }
    return {key: value for key, value in result.items() if value}


def _normalize_url(url):
    url = _normalize_whitespace(url)
    if not url:
        return ""
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+\-.]*://", url):
        url = f"https://{url}"
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return ""
    if not parsed.netloc:
        return ""
    return urllib.parse.urlunparse(parsed)


def _download_html(url, timeout):
    parsed = urllib.parse.urlparse(url)
    if not _hostname_is_public(parsed.hostname):
        return None

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "MarkerBot/1.0 (+https://github.com/krysros/marker)",
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            final_url = response.geturl() or url
            content_type = (response.headers.get("Content-Type") or "").lower()
            if (
                "text/html" not in content_type
                and "application/xhtml+xml" not in content_type
            ):
                return None

            payload = response.read(_MAX_HTML_BYTES + 1)
            if len(payload) > _MAX_HTML_BYTES:
                payload = payload[:_MAX_HTML_BYTES]

            charset = response.headers.get_content_charset() or "utf-8"
            html = payload.decode(charset, errors="ignore")
            return html, final_url
    except (urllib.error.URLError, UnicodeDecodeError, ValueError, TimeoutError):
        return None


def _hostname_is_public(hostname):
    hostname = (hostname or "").strip().lower()
    if not hostname or hostname == "localhost" or hostname.endswith(".local"):
        return False
    try:
        addresses = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False
    for address in addresses:
        try:
            ip = ipaddress.ip_address(address[4][0])
        except ValueError:
            return False
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            return False
    return True


def _extract_json_ld(soup):
    if not soup:
        return []

    objects = []
    for script in soup.find_all("script"):
        script_type = _normalize_whitespace(script.get("type") or "").lower()
        if "ld+json" not in script_type:
            continue

        raw = script.string or script.get_text("\n")
        payload = _normalize_whitespace(unescape(raw or ""))
        if not payload:
            continue
        if payload.startswith("<!--") and payload.endswith("-->"):
            payload = payload[4:-3].strip()
        try:
            item = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if isinstance(item, list):
            objects.extend(item)
        else:
            objects.append(item)
    return objects


def _iter_nodes(value):
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from _iter_nodes(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _iter_nodes(nested)


def _organization_name(json_ld):
    for node in _iter_nodes(json_ld):
        if not isinstance(node, dict):
            continue
        node_type = node.get("@type")
        types = []
        if isinstance(node_type, str):
            types = [node_type]
        elif isinstance(node_type, list):
            types = [str(item) for item in node_type]
        folded_types = {_fold_text(item) for item in types}
        if not folded_types.intersection(_ORG_TYPES):
            continue
        name = _first_not_empty(node.get("legalName"), node.get("name"))
        if name:
            return name
    return _jsonld_value(json_ld, "name")


def _visible_legal_name_candidates(visible_lines, hostname):
    candidates = []
    host_tokens = _hostname_tokens(hostname)

    for line in visible_lines or []:
        line = _normalize_whitespace(line)
        if not line or not (
            _contains_legal_form(line)
            or _contains_company_descriptor(line)
            or _contains_company_prefix(line)
        ):
            continue

        candidate = _trim_name_tail(line)
        candidate = _trim_name_prefix_to_hostname(candidate, host_tokens)
        candidate = _normalize_whitespace(candidate).strip(" ,;:-|")

        if len(candidate) >= 2 and (
            _contains_legal_form(candidate)
            or _contains_company_descriptor(candidate)
            or _contains_company_prefix(candidate)
        ):
            candidates.append(candidate)

    return candidates


def _trim_name_tail(value):
    match = _NAME_TAIL_RE.search(value or "")
    if not match:
        return value
    return value[: match.start()]


def _trim_name_prefix_to_hostname(value, host_tokens):
    if not value or not host_tokens:
        return value

    starts = []
    for token in host_tokens:
        match = re.search(rf"\b{re.escape(token)}\b", value, flags=re.IGNORECASE)
        if match:
            starts.append(match.start())

    if not starts:
        return value

    return value[min(starts) :]


def _select_preferred_name(candidates, hostname):
    variants = {}
    for source_index, candidate in enumerate(candidates):
        candidate = _normalize_whitespace(candidate)
        if not candidate:
            continue
        for variant in _name_variants(candidate):
            normalized = _normalize_whitespace(variant)
            if len(normalized) >= 2:
                folded = _fold_text(normalized)
                if not folded:
                    continue

                case_rank = _company_name_case_rank(normalized)
                existing = variants.get(folded)
                if not existing:
                    variants[folded] = {
                        "source_index": source_index,
                        "variant": normalized,
                        "case_rank": case_rank,
                    }
                    continue

                if case_rank > existing["case_rank"]:
                    variants[folded] = {
                        "source_index": min(source_index, existing["source_index"]),
                        "variant": normalized,
                        "case_rank": case_rank,
                    }
                elif (
                    case_rank == existing["case_rank"]
                    and source_index < existing["source_index"]
                ):
                    existing["source_index"] = source_index
                    existing["variant"] = normalized

    if not variants:
        return _hostname_name(hostname)

    best_name = ""
    best_rank = None
    for variant_data in variants.values():
        source_index = variant_data["source_index"]
        variant = variant_data["variant"]
        case_rank = variant_data["case_rank"]

        host_score = _hostname_match_score(variant, hostname)
        has_legal_form = _contains_legal_form(variant)
        has_descriptor = _contains_company_descriptor(variant)
        has_core_name = _has_core_name_outside_legal_form(variant)
        length = len(variant)

        rank = (
            int(has_legal_form and has_core_name and host_score > 0),
            int(host_score > 0),
            int(has_legal_form and has_core_name),
            int(has_descriptor and host_score > 0),
            int(has_descriptor and case_rank[0] > 0),
            case_rank,
            host_score,
            int(length <= 90),
            -abs(length - 40),
            -source_index,
        )
        if best_rank is None or rank > best_rank:
            best_rank = rank
            best_name = variant

    return best_name or _hostname_name(hostname)


def _name_variants(candidate):
    variants = [candidate]
    for separator in _NAME_SEPARATORS:
        for value in tuple(variants):
            if separator not in value:
                continue
            parts = [part.strip() for part in value.split(separator)]
            variants.extend(part for part in parts if part)

    unique_variants = []
    seen = set()
    for value in variants:
        folded = _fold_text(value)
        if folded and folded not in seen:
            seen.add(folded)
            unique_variants.append(value)
    return unique_variants


def _hostname_match_score(name, hostname):
    signature = _hostname_signature(hostname)
    if not signature:
        return 0

    folded_name = _fold_text(name)
    score = 0
    if signature in folded_name:
        score += 8

    host_tokens = _hostname_tokens(hostname)
    name_tokens = set(re.findall(r"[a-z0-9]+", folded_name))
    overlaps = sum(1 for token in host_tokens if token in name_tokens)
    score += min(overlaps * 2, 6)
    return score


def _hostname_signature(hostname):
    hostname = (hostname or "").strip().lower()
    if not hostname:
        return ""

    parts = [part for part in hostname.split(".") if part and part != "www"]
    if not parts:
        return ""

    core = parts[0].replace("-", " ").replace("_", " ")
    return _fold_text(core)


def _hostname_tokens(hostname):
    signature = _hostname_signature(hostname)
    if not signature:
        return []
    return [token for token in re.findall(r"[a-z0-9]+", signature) if len(token) >= 3]


def _contains_legal_form(name):
    folded_name = _fold_text(name)
    return any(pattern.search(folded_name) for pattern in _LEGAL_FORM_PATTERNS)


def _contains_company_descriptor(name):
    folded_name = _fold_text(name)
    return any(pattern.search(folded_name) for pattern in _COMPANY_DESCRIPTOR_PATTERNS)


def _contains_company_prefix(name):
    folded_name = _fold_text(name)
    return any(pattern.search(folded_name) for pattern in _COMPANY_PREFIX_PATTERNS)


def _company_name_case_rank(name):
    tokens = []
    for token in _NAME_CASE_TOKEN_RE.findall(name or ""):
        folded_token = _fold_text(token)
        if len(folded_token) < 2 or folded_token in _NAME_CASE_STOPWORDS:
            continue
        tokens.append(token)

    if not tokens:
        return (0, 0)

    good_tokens = sum(1 for token in tokens if _is_company_case_token(token))
    return (int(good_tokens == len(tokens)), good_tokens)


def _is_company_case_token(token):
    for part in token.split("-"):
        letters = [char for char in part if char.isalpha()]
        if not letters:
            continue

        if all(char.isupper() for char in letters):
            continue

        first_alpha_index = next(
            (index for index, char in enumerate(part) if char.isalpha()),
            -1,
        )
        if first_alpha_index < 0 or not part[first_alpha_index].isupper():
            return False

        tail = part[first_alpha_index + 1 :]
        if any(char.isalpha() and not char.islower() for char in tail):
            return False

    return True


def _has_core_name_outside_legal_form(name):
    stripped = _fold_text(name)
    for pattern in _LEGAL_FORM_PATTERNS:
        stripped = pattern.sub(" ", stripped)

    tokens = [token for token in re.findall(r"[a-z0-9]+", stripped) if len(token) >= 2]
    return bool(tokens)


def _jsonld_value(json_ld, key):
    folded_key = _fold_text(key)
    for node in _iter_nodes(json_ld):
        if not isinstance(node, dict):
            continue
        for k, v in node.items():
            if _fold_text(k) != folded_key:
                continue
            if isinstance(v, dict):
                continue
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, str) and _normalize_whitespace(item):
                        return item
                    if isinstance(item, dict):
                        nested = _first_not_empty(item.get("value"), item.get("name"))
                        if nested:
                            return nested
            elif isinstance(v, str):
                value = _normalize_whitespace(v)
                if value:
                    return value
    return ""


def _extract_address(
    json_ld,
    visible_text,
    visible_lines,
    country_code,
    address_block=None,
):
    address = {
        "street": "",
        "postcode": "",
        "city": "",
        "state": "",
        "country": "",
        "country_code": country_code or "",
    }
    text_with_lines = "\n".join(visible_lines)

    for node in _iter_nodes(json_ld):
        if not isinstance(node, dict):
            continue
        candidate = node.get("address")
        if isinstance(candidate, list):
            candidate = next(
                (item for item in candidate if isinstance(item, dict)), None
            )
        if not isinstance(candidate, dict):
            continue

        street = _first_not_empty(
            candidate.get("streetAddress"), candidate.get("street")
        )
        postcode = _first_not_empty(
            candidate.get("postalCode"), candidate.get("zipCode")
        )
        city = _first_not_empty(candidate.get("addressLocality"), candidate.get("city"))
        state = _first_not_empty(candidate.get("addressRegion"), candidate.get("state"))
        country = _first_not_empty(
            candidate.get("addressCountry"), candidate.get("country")
        )

        _set_if_missing(address, "street", street)
        _set_if_missing(
            address,
            "postcode",
            postcode,
            sanitizer=lambda value: _sanitize_postcode(
                value, max_len=_MAX_POSTCODE_LEN
            ),
        )
        _set_if_missing(address, "city", city)
        _set_if_missing(address, "state", state)
        _set_if_missing(address, "country", country)

    if not address["country_code"]:
        address["country_code"] = _country_code_from_value(address["country"])

    block = address_block or {}
    _set_if_missing(
        address,
        "street",
        block.get("street"),
        sanitizer=lambda value: _sanitize_street(value, max_len=_MAX_STREET_LEN),
    )
    _set_if_missing(
        address,
        "postcode",
        block.get("postcode"),
        sanitizer=lambda value: _sanitize_postcode(value, max_len=_MAX_POSTCODE_LEN),
    )
    _set_if_missing(
        address,
        "city",
        block.get("city"),
        sanitizer=lambda value: _sanitize_city(value, max_len=_MAX_CITY_LEN),
    )

    if not (address["street"] and address["postcode"] and address["city"]):
        line = _extract_address_line(visible_lines, visible_text)
        if line:
            if not address["street"]:
                street = _extract_by_regex(_STREET_RE, line)
                if street:
                    address["street"] = street
            if not (address["postcode"] and address["city"]):
                postcode, city = _extract_postcode_city_from_lines(line.splitlines())
                if postcode and not address["postcode"]:
                    address["postcode"] = postcode
                if city and not address["city"]:
                    address["city"] = city

    if not address["street"]:
        address["street"] = _extract_by_regex(
            _STREET_RE, text_with_lines or visible_text
        )

    if not (address["postcode"] and address["city"]):
        postcode, city = _extract_postcode_city_from_lines(visible_lines)
        if postcode and not address["postcode"]:
            address["postcode"] = postcode
        if city and not address["city"]:
            address["city"] = city

    if not address["postcode"]:
        address["postcode"] = _extract_first_postcode(text_with_lines or visible_text)

    geocoded = _geocode_address(address)
    if geocoded:
        _set_if_missing(
            address,
            "postcode",
            geocoded.get("postcode"),
            sanitizer=lambda value: _sanitize_postcode(
                value, max_len=_MAX_POSTCODE_LEN
            ),
        )
        _set_if_missing(
            address,
            "city",
            geocoded.get("city"),
            sanitizer=lambda value: _sanitize_city(value, max_len=_MAX_CITY_LEN),
        )
        _set_if_missing(address, "state", geocoded.get("state"))
        _set_if_missing(address, "country", geocoded.get("country"))
        _set_if_missing(
            address,
            "country_code",
            _first_not_empty(geocoded.get("country_code"), geocoded.get("country")),
            sanitizer=_country_code_from_value,
        )

    return address


def _extract_address_line(visible_lines, visible_text):
    for index, line in enumerate(visible_lines):
        extracted = _extract_by_regex(_ADDRESS_LINE_RE, line)
        if extracted:
            return extracted
        if _ADDRESS_ONLY_LABEL_RE.match(line):
            next_lines = visible_lines[index + 1 : index + 3]
            if next_lines:
                return "\n".join(next_lines)
    return _extract_by_regex(_ADDRESS_LINE_RE, visible_text)


def _extract_name_address_block(visible_lines):
    segments = _address_segments(visible_lines)
    if len(segments) < 2:
        return {}

    for index, segment in enumerate(segments):
        street = _extract_street_candidate(segment)
        if not street:
            continue

        postcode, city = _extract_postcode_city_from_lines([segment])
        if not (postcode and city):
            for offset in (1, 2):
                next_index = index + offset
                if next_index >= len(segments):
                    break
                postcode, city = _extract_postcode_city_from_lines(
                    [segments[next_index]]
                )
                if postcode and city:
                    break

        if not (postcode and city):
            continue

        name = ""
        for prev_index in range(index - 1, max(index - 4, -1), -1):
            candidate = _normalize_whitespace(segments[prev_index]).strip(" ,;:-|")
            if not _is_name_block_candidate(candidate):
                continue
            name = _compose_block_name(segments, prev_index, candidate)
            if name:
                break

        return {
            "name": name,
            "street": street,
            "postcode": postcode,
            "city": city,
        }

    return {}


def _compose_block_name(segments, name_index, name_candidate):
    base_name = _sanitize_name(
        name_candidate,
        _MAX_COMPANY_NAME_LEN,
        split_on_separators=False,
    )
    if not base_name:
        return ""

    if _contains_company_prefix(base_name):
        return base_name

    for prefix_index in range(name_index - 1, max(name_index - 3, -1), -1):
        prefix_candidate = _normalize_whitespace(segments[prefix_index]).strip(" ,;:-|")
        if not _is_name_block_candidate(prefix_candidate):
            continue
        if not _contains_company_prefix(prefix_candidate):
            continue

        combined = _sanitize_name(
            f"{prefix_candidate} {base_name}",
            _MAX_COMPANY_NAME_LEN,
            split_on_separators=False,
        )
        if combined and _fold_text(combined) != _fold_text(base_name):
            return combined

    return base_name


def _address_segments(visible_lines):
    segments = []
    for line in visible_lines or []:
        normalized_line = _normalize_whitespace(line)
        if not normalized_line:
            continue

        parts = [
            _normalize_whitespace(part).strip(" ,;:-|")
            for part in _ADDRESS_PART_SPLIT_RE.split(normalized_line)
            if _normalize_whitespace(part)
        ]
        if len(parts) > 1:
            segments.extend(part for part in parts if part)
        else:
            segments.append(normalized_line)

    return segments


def _extract_street_candidate(value):
    value = _normalize_whitespace(value).strip(" ,;:-|")
    if not value:
        return ""

    labeled_street = _extract_by_regex(_STREET_RE, value)
    if labeled_street:
        return _sanitize_street(labeled_street, max_len=_MAX_STREET_LEN)

    if _POSTCODE_RE.search(value):
        return ""
    if not re.search(r"\d", value):
        return ""
    if not re.search(
        r"[A-Za-zÀ-ÖØ-öø-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻż]",
        value,
    ):
        return ""

    folded_value = _fold_text(value)
    if any(keyword in folded_value for keyword in _NON_NAME_LINE_KEYWORDS):
        return ""

    return _sanitize_street(value, max_len=_MAX_STREET_LEN)


def _is_name_block_candidate(value):
    value = _normalize_whitespace(value)
    if len(value) < 2:
        return False
    if _POSTCODE_RE.search(value):
        return False
    if _extract_street_candidate(value):
        return False

    folded_value = _fold_text(value)
    if any(keyword in folded_value for keyword in _NON_NAME_LINE_KEYWORDS):
        return False

    return bool(re.search(r"[A-Za-zÀ-ÖØ-öø-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻż]{2,}", value))


def _extract_postcode_city_from_lines(lines):
    patterns = (_POSTCODE_CITY_LINE_RE, _CITY_POSTCODE_LINE_RE)
    normalized_lines = [
        _normalize_whitespace(line) for line in lines if _normalize_whitespace(line)
    ]

    for pattern in patterns:
        for line in normalized_lines:
            match = pattern.search(line)
            if not match:
                continue
            postcode = _sanitize_postcode(
                match.group("postcode"), max_len=_MAX_POSTCODE_LEN
            )
            city = _sanitize_city(match.group("city"), max_len=_MAX_CITY_LEN)
            if postcode and city:
                return postcode, city

    return "", ""


def _extract_first_postcode(text):
    match = _POSTCODE_RE.search(text or "")
    if not match:
        return ""
    return _sanitize_postcode(match.group(0), max_len=_MAX_POSTCODE_LEN)


def _country_name(country_code):
    code = (country_code or "").strip().upper()
    if not code:
        return ""
    country = pycountry.countries.get(alpha_2=code)
    return getattr(country, "name", "")


def _geocode_address(address):
    needs_enrichment = (
        bool(address.get("postcode"))
        and (
            not address.get("city")
            or not address.get("state")
            or not address.get("country_code")
        )
    ) or (bool(address.get("city")) and not address.get("state"))

    if not needs_enrichment:
        return None

    country_name = _country_name(address.get("country_code")) or _normalize_whitespace(
        address.get("country")
    )

    queries = []
    postcode = _sanitize_postcode(address.get("postcode"), max_len=_MAX_POSTCODE_LEN)
    if postcode:
        query = {"postalcode": postcode}
        if country_name:
            query["country"] = country_name
        queries.append(query)

    city = _sanitize_city(address.get("city"), max_len=_MAX_CITY_LEN)
    street = _sanitize_street(address.get("street"), max_len=_MAX_STREET_LEN)

    if street:
        query = {"street": street}
        if city:
            query["city"] = city
        if country_name:
            query["country"] = country_name
        if query not in queries:
            queries.append(query)

    if city:
        query = {"city": city}
        if country_name:
            query["country"] = country_name
        if query not in queries:
            queries.append(query)

    for query in queries:
        details = location_details(**query)
        if details:
            return details

    return None


def _set_if_missing(data, key, value, sanitizer=None):
    if data.get(key):
        return

    if sanitizer:
        normalized = sanitizer(value)
    else:
        normalized = _normalize_whitespace(value)

    if normalized:
        data[key] = normalized


def _extract_by_regex(pattern, text):
    match = pattern.search(text or "")
    if not match:
        return ""
    return _normalize_whitespace(match.group(1))


def _meta_country(meta):
    return _first_not_empty(
        meta.get("geo.country"),
        meta.get("country"),
        meta.get("og:locale"),
    )


def _country_code_from_value(value):
    value = _normalize_whitespace(value)
    if not value:
        return ""

    value = value.replace("_", "-")
    if re.fullmatch(r"[A-Za-z]{2}(?:-[A-Za-z]{2})?", value):
        code = value.split("-")[0].upper()
        if code == "UK":
            code = "GB"
        if pycountry.countries.get(alpha_2=code):
            return code

    alias = _COUNTRY_ALIASES.get(_fold_text(value))
    if alias:
        return alias

    try:
        return pycountry.countries.lookup(value).alpha_2
    except LookupError:
        return ""


def _country_code_from_hostname(hostname):
    hostname = (hostname or "").strip().lower()
    if not hostname or "." not in hostname:
        return ""
    tld = hostname.rsplit(".", 1)[-1].upper()
    if len(tld) != 2 or not tld.isalpha():
        return ""
    if tld == "UK":
        tld = "GB"
    country = pycountry.countries.get(alpha_2=tld)
    return country.alpha_2 if country else ""


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


def _subdivision_code_from_text(country_code, folded_text):
    if not country_code or not folded_text:
        return ""
    subdivisions = pycountry.subdivisions.get(country_code=country_code) or []
    for subdivision in subdivisions:
        subdivision_folded = _fold_text(subdivision.name)
        if subdivision_folded and subdivision_folded in folded_text:
            return subdivision.code
    return ""


def _court_code_from_text(text):
    folded_text = _fold_text(text)
    if not folded_text:
        return ""
    for code, label in _COURTS:
        if _fold_text(code) in folded_text or _fold_text(label) in folded_text:
            return code
    return ""


def _sanitize_name(value, max_len, split_on_separators=True):
    value = _normalize_whitespace(value)
    if not value:
        return ""

    if split_on_separators and not _contains_legal_form(value):
        for separator in _NAME_SEPARATORS:
            part = value.split(separator, 1)[0].strip()
            if 2 <= len(part) <= max_len:
                value = part
                break

    value = re.sub(
        r"(?:\s*[|–—-]\s*)?\b(strona\s+gł[oó]wna|home\s*page)\b",
        "",
        value,
        flags=re.IGNORECASE,
    )
    value = _normalize_whitespace(value).strip(" -–—|•")
    if len(value) > max_len:
        value = value[:max_len].rstrip()
    return value if len(value) >= 2 else ""


def _sanitize_street(value, max_len):
    value = _normalize_whitespace(value)
    if not value:
        return ""
    value = re.sub(r"^(?:ulica|ul\.)\s*|^ul\s+", "", value, flags=re.IGNORECASE)
    value = value.strip(" ,")
    if len(value) > max_len:
        value = value[:max_len].rstrip()
    return value


def _sanitize_postcode(value, max_len):
    value = _normalize_whitespace(value)
    if not value:
        return ""
    value = value.replace("–", "-").replace("—", "-")
    digits = re.sub(r"\D", "", value)
    if len(digits) == 5:
        value = f"{digits[:2]}-{digits[2:]}"
    if len(value) > max_len:
        return ""
    return value


def _sanitize_city(value, max_len):
    value = _normalize_whitespace(value)
    if not value:
        return ""
    value = value.strip(" ,")
    if len(value) > max_len:
        value = value[:max_len].rstrip()
    return value


def _sanitize_nip(value):
    digits = re.sub(r"\D", "", value or "")
    if len(digits) != 10:
        return ""
    numbers = [int(char) for char in digits]
    weights = (6, 5, 7, 2, 3, 4, 5, 6, 7)
    checksum = sum(a * b for a, b in zip(numbers[:9], weights, strict=False)) % 11
    if checksum != numbers[9]:
        return ""
    return digits


def _sanitize_regon(value):
    digits = re.sub(r"\D", "", value or "")
    if len(digits) not in {9, 14}:
        return ""
    if len(digits) == 9:
        if not _regon_checksum_9(digits):
            return ""
    else:
        if not _regon_checksum_9(digits[:9]) or not _regon_checksum_14(digits):
            return ""
    return digits


def _sanitize_krs(value):
    digits = re.sub(r"\D", "", value or "")
    if len(digits) != 10:
        return ""
    return digits


def _regon_checksum_9(digits):
    values = [int(char) for char in digits]
    weights = (8, 9, 2, 3, 4, 5, 6, 7)
    checksum = sum(a * b for a, b in zip(values[:8], weights, strict=False)) % 11
    if checksum == 10:
        checksum = 0
    return checksum == values[8]


def _regon_checksum_14(digits):
    values = [int(char) for char in digits]
    weights = (2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8)
    checksum = sum(a * b for a, b in zip(values[:13], weights, strict=False)) % 11
    if checksum == 10:
        checksum = 0
    return checksum == values[13]


def _hostname_name(hostname):
    hostname = (hostname or "").strip().lower()
    if not hostname:
        return ""
    parts = [part for part in hostname.split(".") if part]
    if not parts:
        return ""
    candidate = parts[0] if parts[0] != "www" else (parts[1] if len(parts) > 1 else "")
    candidate = candidate.replace("-", " ").replace("_", " ")
    candidate = _normalize_whitespace(candidate)
    return candidate.title() if len(candidate) >= 2 else ""


def _normalize_whitespace(value):
    return re.sub(r"\s+", " ", value or "").strip()


def _fold_text(value):
    value = _normalize_whitespace(value).casefold()
    value = value.translate(str.maketrans({"ł": "l", "đ": "d", "ø": "o", "ß": "ss"}))
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _first_not_empty(*values):
    for value in values:
        normalized = _normalize_whitespace(value)
        if normalized:
            return normalized
    return ""
