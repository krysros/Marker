"""Tests for marker/utils/vcard_import.py and the contact_import_vcard view."""

import io
from unittest.mock import MagicMock

import pytest
import transaction
from webob.multidict import MultiDict

import marker.forms.ts
from marker.models.company import Company
from marker.models.contact import Contact
from marker.models.user import User
from marker.utils.vcard_import import ParsedVCard, parse_vcard, upsert_vcard
from marker.views.contact import ContactView
from tests.conftest import DummyRequestWithIdentity


@pytest.fixture(autouse=True)
def patch_translationstring_str(monkeypatch):
    monkeypatch.setattr(
        marker.forms.ts.TranslationString, "__str__", lambda self: self.msg
    )
    yield


# ---------------------------------------------------------------------------
# parse_vcard unit tests
# ---------------------------------------------------------------------------

FULL_VCARD = """\
BEGIN:VCARD
VERSION:4.0
FN:Jan Kowalski
N:Kowalski;Jan;;;
TITLE:Developer
ROLE:Developer
TEL;TYPE=WORK;VALUE=uri:tel:+48 600 100 200
EMAIL;TYPE=WORK:jan@example.com
ORG:ACME Corp
ADR;TYPE=WORK:;;Main St 1;Warsaw;PL-MZ;00-001;PL
URL;TYPE=WORK:https://acme.example.com
X-NIP:1234567890
X-REGON:987654321
X-KRS:0000123456
END:VCARD
"""


def test_parse_vcard_all_fields():
    card = parse_vcard(FULL_VCARD)
    assert card is not None
    assert card.name == "Jan Kowalski"
    assert card.role == "Developer"
    assert card.phone == "+48 600 100 200"
    assert card.email == "jan@example.com"
    assert card.org == "ACME Corp"
    assert card.street == "Main St 1"
    assert card.city == "Warsaw"
    assert card.subdivision == "PL-MZ"
    assert card.postcode == "00-001"
    assert card.country == "PL"
    assert card.website == "https://acme.example.com"
    assert card.nip == "1234567890"
    assert card.regon == "987654321"
    assert card.krs == "0000123456"


def test_parse_vcard_tel_uri_prefix_stripped():
    vcf = "BEGIN:VCARD\nVERSION:4.0\nFN:Test\nTEL:tel:+1-555-0100\nEND:VCARD\n"
    card = parse_vcard(vcf)
    assert card.phone == "+1-555-0100"


def test_parse_vcard_n_fallback_when_no_fn():
    vcf = "BEGIN:VCARD\nVERSION:4.0\nN:Smith;John;;;\nEND:VCARD\n"
    card = parse_vcard(vcf)
    assert card.name == "John Smith"


def test_parse_vcard_no_begin_returns_none():
    assert parse_vcard("NOT A VCARD") is None


def test_parse_vcard_empty_fn_returns_none():
    vcf = "BEGIN:VCARD\nVERSION:4.0\nFN:\nEND:VCARD\n"
    assert parse_vcard(vcf) is None


def test_parse_vcard_minimal():
    vcf = "BEGIN:VCARD\nVERSION:4.0\nFN:Minimal Contact\nEND:VCARD\n"
    card = parse_vcard(vcf)
    assert card.name == "Minimal Contact"
    assert card.role is None
    assert card.phone is None
    assert card.email is None
    assert card.org is None


def test_parse_vcard_line_folding():
    # RFC 6350 §3.2: CRLF + single whitespace is removed (not replaced with space)
    vcf = (
        "BEGIN:VCARD\r\n"
        "VERSION:4.0\r\n"
        "FN:Long\r\n"
        " Name\r\n"
        "END:VCARD\r\n"
    )
    card = parse_vcard(vcf)
    # The fold marker (space) is stripped, so "Long" + "Name" = "LongName"
    assert card.name == "LongName"


def test_parse_vcard_unescape_special_chars():
    vcf = (
        "BEGIN:VCARD\nVERSION:4.0\n"
        r"FN:O\'Brien\, Jr." + "\n"
        "END:VCARD\n"
    )
    card = parse_vcard(vcf)
    assert "Brien" in card.name


def test_parse_vcard_org_with_department():
    vcf = "BEGIN:VCARD\nVERSION:4.0\nFN:X\nORG:Corp;Dept\nEND:VCARD\n"
    card = parse_vcard(vcf)
    assert card.org == "Corp"


def test_parse_vcard_line_without_colon():
    # A line without ':' should be silently skipped
    vcf = "BEGIN:VCARD\nVERSION:4.0\nFN:Test\nINVALIDLINE\nEND:VCARD\n"
    card = parse_vcard(vcf)
    assert card.name == "Test"


def test_parse_vcard_param_without_equals():
    # A param segment without '=' should be treated as TYPE=segment
    vcf = "BEGIN:VCARD\nVERSION:4.0\nFN:Test\nTEL;WORK:+1-555-0100\nEND:VCARD\n"
    card = parse_vcard(vcf)
    assert card.phone == "+1-555-0100"


    vcf = FULL_VCARD.replace("\n", "\r\n")
    card = parse_vcard(vcf)
    assert card.name == "Jan Kowalski"


# ---------------------------------------------------------------------------
# upsert_vcard unit tests (with real DB)
# ---------------------------------------------------------------------------

def _make_user(dbsession, name="vcarduser"):
    user = User(
        name=name, fullname="VU", email=f"{name}@e.com", role="admin", password="pw"
    )
    dbsession.add(user)
    dbsession.flush()
    return user


def _card(**kw):
    defaults = dict(
        name="Test Person",
        role="Dev",
        phone="123",
        email="t@t.com",
        org="Test Org",
        street="St 1",
        city="City",
        postcode="00-001",
        subdivision="PL-MZ",
        country="PL",
        website="https://test.example.com",
        nip="111",
        regon="222",
        krs="333",
    )
    defaults.update(kw)
    c = ParsedVCard()
    for k, v in defaults.items():
        setattr(c, k, v)
    return c


def test_upsert_vcard_creates_company_and_contact(dbsession):
    user = _make_user(dbsession, "uvc1")
    card = _card(org="NewCo", name="Alice")
    contact = upsert_vcard(dbsession, user, card)
    assert contact.name == "Alice"
    assert contact.company is not None
    assert contact.company.name == "NewCo"
    assert contact.company.street == "St 1"
    assert contact.company.NIP == "111"


def test_upsert_vcard_existing_company_adds_contact(dbsession):
    user = _make_user(dbsession, "uvc2")
    company = Company(
        name="ExistCo", street="", postcode="", city="", subdivision="",
        country="", website="", color="", NIP="", REGON="", KRS="",
    )
    company.created_by = user
    dbsession.add(company)
    dbsession.flush()

    card = _card(org="ExistCo", name="Bob")
    contact = upsert_vcard(dbsession, user, card)
    assert contact.name == "Bob"
    assert contact.company_id == company.id


def test_upsert_vcard_returns_existing_contact(dbsession):
    user = _make_user(dbsession, "uvc3")
    company = Company(
        name="SameCo", street="", postcode="", city="", subdivision="",
        country="", website="", color="", NIP="", REGON="", KRS="",
    )
    company.created_by = user
    dbsession.add(company)
    dbsession.flush()

    existing = Contact(name="Carol", role="Dev", phone="123", email="t@t.com", color="")
    existing.created_by = user
    company.contacts.append(existing)
    dbsession.flush()

    card = _card(org="SameCo", name="Carol", role="Dev", phone="123", email="t@t.com")
    contact = upsert_vcard(dbsession, user, card)
    assert contact.id == existing.id


def test_upsert_vcard_no_org_uses_contact_name_as_company(dbsession):
    user = _make_user(dbsession, "uvc4")
    card = _card(org=None, name="Dave Solo")
    contact = upsert_vcard(dbsession, user, card)
    assert contact.name == "Dave Solo"
    assert contact.company.name == "Dave Solo"


# ---------------------------------------------------------------------------
# View tests for contact_import_vcard
# ---------------------------------------------------------------------------

def _make_view_request(dbsession, user, method="GET", vcf_content=None):
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = method
    request.GET = MultiDict()
    request.params = MultiDict()
    request.translate = lambda x: x
    request.route_url = lambda name, **kw: f"/{name}"
    request.current_route_path = lambda: "/contacts/import_vcard"
    request.session = MagicMock()
    request.response = MagicMock()
    request.referrer = "/home"
    request.matchdict = {}
    request.context = MagicMock()

    if method == "POST":
        post = MultiDict()
        if vcf_content is not None:
            file_mock = MagicMock()
            file_mock.file = io.BytesIO(
                vcf_content.encode("utf-8") if isinstance(vcf_content, str) else vcf_content
            )
            post["vcf_file"] = file_mock
        request.POST = post
    else:
        request.POST = MultiDict()

    return request


def test_view_import_vcard_get(dbsession):
    user = _make_user(dbsession, "vvu1")
    request = _make_view_request(dbsession, user)
    view = ContactView(request)
    result = view.contact_import_vcard()
    assert result["heading"] == "Import vCard"
    assert "form" in result


def test_view_import_vcard_post_no_file(dbsession):
    user = _make_user(dbsession, "vvu2")
    request = _make_view_request(dbsession, user, method="POST")
    # POST with no vcf_file key → redirect to referrer
    request.POST = MultiDict()
    view = ContactView(request)
    from pyramid.httpexceptions import HTTPFound
    result = view.contact_import_vcard()
    assert isinstance(result, HTTPFound)


def test_view_import_vcard_post_invalid_file(dbsession):
    user = _make_user(dbsession, "vvu3")
    request = _make_view_request(dbsession, user, method="POST", vcf_content="NOT A VCARD")
    view = ContactView(request)
    from pyramid.httpexceptions import HTTPFound
    result = view.contact_import_vcard()
    assert isinstance(result, HTTPFound)
    request.session.flash.assert_called_once()
    assert "warning:" in request.session.flash.call_args[0][0]


def test_view_import_vcard_post_valid_new_company(dbsession):
    user = _make_user(dbsession, "vvu4")
    transaction.commit()
    request = _make_view_request(
        dbsession, user, method="POST", vcf_content=FULL_VCARD
    )
    view = ContactView(request)
    from pyramid.httpexceptions import HTTPFound
    result = view.contact_import_vcard()
    assert isinstance(result, HTTPFound)
    assert "/contact_view" in result.location


def test_view_import_vcard_post_existing_company_new_contact(dbsession):
    user = _make_user(dbsession, "vvu5")
    company = Company(
        name="ACME Corp", street="", postcode="", city="", subdivision="",
        country="", website="", color="", NIP="", REGON="", KRS="",
    )
    company.created_by = user
    dbsession.add(company)
    transaction.commit()

    request = _make_view_request(
        dbsession, user, method="POST", vcf_content=FULL_VCARD
    )
    view = ContactView(request)
    from pyramid.httpexceptions import HTTPFound
    result = view.contact_import_vcard()
    assert isinstance(result, HTTPFound)


def test_view_import_vcard_post_latin1_encoded(dbsession):
    """File with latin-1 bytes (fails utf-8-sig, falls back to utf-8 replace)."""
    user = _make_user(dbsession, "vvu7")
    # Create bytes that are valid latin-1 but invalid utf-8
    raw_bytes = FULL_VCARD.encode("latin-1") + b"\xff\xfe"
    request = _make_view_request(dbsession, user, method="POST")
    file_mock = MagicMock()
    file_mock.file = io.BytesIO(raw_bytes)
    request.POST["vcf_file"] = file_mock
    view = ContactView(request)
    from pyramid.httpexceptions import HTTPFound
    # The replaced text may or may not parse as valid vCard — either way, no exception
    result = view.contact_import_vcard()
    assert isinstance(result, HTTPFound)


def test_view_import_vcard_post_string_data(dbsession):
    """If file.read() returns a string (non-bytes), it should be handled via str()."""
    user = _make_user(dbsession, "vvu8")
    request = _make_view_request(dbsession, user, method="POST")
    file_mock = MagicMock()
    file_mock.file.read.return_value = FULL_VCARD  # string, not bytes
    request.POST["vcf_file"] = file_mock
    view = ContactView(request)
    from pyramid.httpexceptions import HTTPFound
    result = view.contact_import_vcard()
    assert isinstance(result, HTTPFound)


def test_view_import_vcard_post_existing_contact(dbsession):
    user = _make_user(dbsession, "vvu6")
    company = Company(
        name="ACME Corp", street="", postcode="", city="", subdivision="",
        country="", website="", color="", NIP="", REGON="", KRS="",
    )
    company.created_by = user
    dbsession.add(company)
    dbsession.flush()
    existing = Contact(
        name="Jan Kowalski", role="Developer", phone="+48 600 100 200",
        email="jan@example.com", color=""
    )
    existing.created_by = user
    company.contacts.append(existing)
    transaction.commit()

    request = _make_view_request(
        dbsession, user, method="POST", vcf_content=FULL_VCARD
    )
    view = ContactView(request)
    from pyramid.httpexceptions import HTTPFound
    result = view.contact_import_vcard()
    assert isinstance(result, HTTPFound)

