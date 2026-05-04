"""Parse a vCard 4.0/3.0 file and upsert Company + Contact.

Supported fields (matching the built-in vCard export):
  FN / N        → contact.name
  TITLE / ROLE  → contact.role
  TEL           → contact.phone
  EMAIL         → contact.email
  ORG           → company.name
  ADR           → company.street / city / postcode / subdivision / country
  URL           → company.website
  X-NIP         → company.NIP
  X-REGON       → company.REGON
  X-KRS         → company.KRS
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import func, select

from ..models import Company, Contact


# ---------------------------------------------------------------------------
# Low-level vCard line unfolding and property parser
# ---------------------------------------------------------------------------

def _unfold(text: str) -> str:
    """Unfold vCard lines (RFC 6350 §3.2)."""
    return re.sub(r"\r?\n[ \t]", "", text)


def _unescape(value: str) -> str:
    """Reverse RFC 6350 TEXT escaping."""
    return (
        value
        .replace("\\n", "\n")
        .replace("\\N", "\n")
        .replace("\\;", ";")
        .replace("\\,", ",")
        .replace("\\\\", "\\")
    )


def _parse_lines(text: str) -> list[tuple[str, dict, str]]:
    """Return list of (name, params, value) for each unfolded content line."""
    lines = _unfold(text).splitlines()
    result = []
    for raw in lines:
        raw = raw.rstrip("\r")
        if not raw or raw.upper() in ("BEGIN:VCARD", "END:VCARD"):
            continue
        # Split name;params from value at first ':'
        if ":" not in raw:
            continue
        left, value = raw.split(":", 1)
        parts = left.split(";")
        name = parts[0].upper()
        params: dict[str, list[str]] = {}
        for p in parts[1:]:
            if "=" in p:
                k, v = p.split("=", 1)
                params.setdefault(k.upper(), []).append(v)
            else:
                params.setdefault("TYPE", []).append(p.upper())
        result.append((name, params, value))
    return result


# ---------------------------------------------------------------------------
# High-level parsed card dataclass
# ---------------------------------------------------------------------------

@dataclass
class ParsedVCard:
    name: str = ""
    role: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    org: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    subdivision: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    nip: Optional[str] = None
    regon: Optional[str] = None
    krs: Optional[str] = None


def parse_vcard(text: str) -> Optional[ParsedVCard]:
    """Parse the first VCARD block found in *text*.

    Returns a :class:`ParsedVCard` or ``None`` if no valid card was found.
    """
    # Extract first VCARD block (case-insensitive)
    m = re.search(
        r"BEGIN:VCARD\r?\n(.*?)END:VCARD",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if not m:
        return None

    block = "BEGIN:VCARD\n" + m.group(1) + "END:VCARD"
    lines = _parse_lines(block)

    card = ParsedVCard()
    fn_seen = False

    for name, params, value in lines:
        value = value.strip()
        if name == "FN" and not fn_seen:
            card.name = _unescape(value)
            fn_seen = True
        elif name == "N" and not card.name:
            # N:surname;given;additional;prefix;suffix
            parts = [_unescape(p) for p in value.split(";")]
            surname = parts[0] if len(parts) > 0 else ""
            given = parts[1] if len(parts) > 1 else ""
            card.name = " ".join(p for p in (given, surname) if p).strip()
        elif name in ("TITLE", "ROLE") and not card.role:
            card.role = _unescape(value) or None
        elif name == "TEL" and not card.phone:
            # Strip "tel:" URI prefix if present
            phone = re.sub(r"^tel:", "", value, flags=re.IGNORECASE)
            card.phone = _unescape(phone) or None
        elif name == "EMAIL" and not card.email:
            card.email = _unescape(value) or None
        elif name == "ORG" and not card.org:
            # ORG:Company;Department → take only the first component
            org_parts = value.split(";")
            card.org = _unescape(org_parts[0]) or None
        elif name == "ADR":
            # ADR:pobox;ext;street;city;region;postal;country
            adr_parts = [_unescape(p) for p in value.split(";")]
            def _adr(i):
                return adr_parts[i] if i < len(adr_parts) else ""
            if not card.street:
                card.street = _adr(2) or None
            if not card.city:
                card.city = _adr(3) or None
            if not card.subdivision:
                card.subdivision = _adr(4) or None
            if not card.postcode:
                card.postcode = _adr(5) or None
            if not card.country:
                card.country = _adr(6) or None
        elif name == "URL" and not card.website:
            card.website = _unescape(value) or None
        elif name == "X-NIP" and not card.nip:
            card.nip = _unescape(value) or None
        elif name == "X-REGON" and not card.regon:
            card.regon = _unescape(value) or None
        elif name == "X-KRS" and not card.krs:
            card.krs = _unescape(value) or None

    if not card.name:
        return None
    return card


# ---------------------------------------------------------------------------
# DB upsert logic
# ---------------------------------------------------------------------------

def _contacts_equal(contact: Contact, card: ParsedVCard) -> bool:
    """Return True when the DB contact matches all vCard contact fields."""
    return (
        (contact.name or "") == (card.name or "")
        and (contact.role or "") == (card.role or "")
        and (contact.phone or "") == (card.phone or "")
        and (contact.email or "") == (card.email or "")
    )


def upsert_vcard(dbsession, identity, card: ParsedVCard) -> Contact:
    """Apply vCard upsert rules and return the resulting Contact.

    Rules:
    1. Company + contact match → return existing contact unchanged.
    2. Company exists, no matching contact → create contact, attach to company.
    3. Company doesn't exist → create company + contact.
    """
    company: Optional[Company] = None

    if card.org:
        company = dbsession.execute(
            select(Company).filter(
                func.lower(Company.name) == func.lower(card.org)
            )
        ).scalar_one_or_none()

    if company is not None:
        # Check for an existing identical contact
        for c in company.contacts:
            if _contacts_equal(c, card):
                return c
        # Attach new contact to existing company
        contact = Contact(
            name=card.name,
            role=card.role,
            phone=card.phone,
            email=card.email,
            color="",
        )
        contact.created_by = identity
        company.contacts.append(contact)
        dbsession.flush()
        return contact

    # Create company + contact from scratch
    company = Company(
        name=card.org or card.name,
        street=card.street or "",
        postcode=card.postcode or "",
        city=card.city or "",
        subdivision=card.subdivision or "",
        country=card.country or "",
        website=card.website or "",
        color="",
        NIP=card.nip or "",
        REGON=card.regon or "",
        KRS=card.krs or "",
    )
    company.created_by = identity
    dbsession.add(company)
    dbsession.flush()

    contact = Contact(
        name=card.name,
        role=card.role,
        phone=card.phone,
        email=card.email,
        color="",
    )
    contact.created_by = identity
    company.contacts.append(contact)
    dbsession.flush()
    return contact
