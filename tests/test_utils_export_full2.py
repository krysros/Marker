import datetime

import pytest

import marker.forms.ts
from marker.utils import export


class DummyCompany:
    def __init__(self, name, city, subdivision, country):
        self.name = name
        self.city = city
        self.subdivision = subdivision
        self.country = country


class DummyContact:
    def __init__(self, name, role, phone, email, company):
        self.name = name
        self.role = role
        self.phone = phone
        self.email = email
        self.company = company


class DummyProject:
    def __init__(self, name, city, subdivision, country):
        self.name = name
        self.city = city
        self.subdivision = subdivision
        self.country = country


class DummyContactProject:
    def __init__(self, name, role, phone, email, project):
        self.name = name
        self.role = role
        self.phone = phone
        self.email = email
        self.project = project


@pytest.fixture(autouse=True)
def patch_translationstring_str(monkeypatch):
    monkeypatch.setattr(
        marker.forms.ts.TranslationString, "__str__", lambda self: self.msg
    )
    yield


def test_response_xlsx_contacts_company():
    company = DummyCompany("TestCo", "Warsaw", "PL-MZ", "PL")
    contact = DummyContact("Jan", "CEO", "123", "jan@example.com", company)
    response = export.response_xlsx_contacts_company([contact])
    assert hasattr(response, "body_file")
    content = response.body
    assert len(content) > 0


def test_response_xlsx_contacts_project():
    project = DummyProject("TestProj", "Warsaw", "PL-MZ", "PL")
    contact = DummyContactProject("Anna", "Manager", "456", "anna@example.com", project)
    response = export.response_xlsx_contacts_project([contact])
    assert hasattr(response, "body_file")
    content = response.body
    assert len(content) > 0


def test_response_vcard(monkeypatch):
    class DummyContact:
        name = "Jan Kowalski"

    class DummyTemplate:
        def render(self, contact):
            return "VCARD DATA"

    monkeypatch.setattr(export, "vcard_template", lambda: DummyTemplate())
    response = export.response_vcard(DummyContact())
    assert response.text == "VCARD DATA"
    assert response.content_type == "text/vcard"
    assert response.charset.lower() == "utf-8"
    assert "attachment; filename=" in response.content_disposition


def test_response_xlsx_with_row_color_and_datetime():
    """Test row_color formatting with datetime value (covers line 127)."""
    import datetime

    headers = ["Name", "Date"]
    rows = [["TestCo", datetime.datetime(2024, 1, 15, 10, 30)]]
    row_colors = ["red"]
    response = export.response_xlsx(rows, headers, row_colors=row_colors)
    assert hasattr(response, "body_file")
    assert len(response.body) > 0


def test_response_ods_contacts_company():
    company = DummyCompany("TestCo", "Warsaw", "PL-MZ", "PL")
    contact = DummyContact("Jan", "CEO", "123", "jan@example.com", company)
    response = export.response_ods_contacts_company([contact])
    assert response.content_type == "application/vnd.oasis.opendocument.spreadsheet"
    assert "Marker.ods" in response.content_disposition
    assert len(response.body) > 0


def test_response_ods_contacts_project():
    project = DummyProject("TestProj", "Warsaw", "PL-MZ", "PL")
    contact = DummyContactProject("Anna", "Manager", "456", "anna@example.com", project)
    response = export.response_ods_contacts_project([contact])
    assert response.content_type == "application/vnd.oasis.opendocument.spreadsheet"
    assert "Marker.ods" in response.content_disposition
    assert len(response.body) > 0
    """Test _safe_cell_value with a custom type (covers line 64)."""

    class CustomObj:
        def __str__(self):
            return "custom_value"

    headers = ["Name"]
    rows = [[CustomObj()]]
    row_colors = [""]
    response = export.response_xlsx(rows, headers, row_colors=row_colors)
    assert hasattr(response, "body_file")
    assert len(response.body) > 0


# ===========================================================================
# vCard template integration tests
# ===========================================================================


class _VcardCompany:
    def __init__(self, **kw):
        self.name = kw.get("name", "ACME Corp")
        self.street = kw.get("street", "Main St 1")
        self.postcode = kw.get("postcode", "00-001")
        self.city = kw.get("city", "Warsaw")
        self.subdivision = kw.get("subdivision", "PL-MZ")
        self.country = kw.get("country", "PL")
        self.website = kw.get("website", "https://acme.example.com")
        self.NIP = kw.get("NIP", "1234567890")
        self.REGON = kw.get("REGON", "987654321")
        self.KRS = kw.get("KRS", "0000123456")


class _VcardProject:
    def __init__(self, **kw):
        self.name = kw.get("name", "Big Project")
        self.street = kw.get("street", "Project Rd 5")
        self.postcode = kw.get("postcode", "01-001")
        self.city = kw.get("city", "Krakow")
        self.subdivision = kw.get("subdivision", "PL-MA")
        self.country = kw.get("country", "PL")
        self.website = kw.get("website", "https://proj.example.com")


class _VcardContact:
    def __init__(self, **kw):
        self.id = kw.get("id", 42)
        self.name = kw.get("name", "Jan Kowalski")
        self.role = kw.get("role", "Developer")
        self.phone = kw.get("phone", "+48 600 100 200")
        self.email = kw.get("email", "jan@example.com")
        self.company = kw.get("company", None)
        self.project = kw.get("project", None)
        self.updated_at = kw.get("updated_at", datetime.datetime(2025, 6, 1, 12, 0, 0))
        self.created_at = kw.get("created_at", datetime.datetime(2025, 1, 1, 8, 0, 0))


def _render_vcard(contact):
    return export.vcard_template().render(contact=contact)


def test_vcard_basic_fields():
    contact = _VcardContact(company=None, project=None)
    text = _render_vcard(contact)
    assert "BEGIN:VCARD" in text
    assert "VERSION:4.0" in text
    assert "FN:Jan Kowalski" in text
    assert "N:Jan Kowalski;;;;" in text
    assert "TITLE:Developer" in text
    assert "ROLE:Developer" in text
    assert "TEL;TYPE=WORK;VALUE=uri:tel:+48 600 100 200" in text
    assert "EMAIL;TYPE=WORK:jan@example.com" in text
    assert "END:VCARD" in text


def test_vcard_company_fields():
    co = _VcardCompany()
    contact = _VcardContact(company=co, project=None)
    text = _render_vcard(contact)
    assert "ORG:ACME Corp" in text
    assert "ADR;TYPE=WORK:;;Main St 1;Warsaw;PL-MZ;00-001;PL" in text
    assert "URL;TYPE=WORK:https://acme.example.com" in text
    assert "X-NIP:1234567890" in text
    assert "X-REGON:987654321" in text
    assert "X-KRS:0000123456" in text


def test_vcard_project_fields():
    proj = _VcardProject()
    contact = _VcardContact(company=None, project=proj)
    text = _render_vcard(contact)
    assert "ORG:Big Project" in text
    assert "ADR;TYPE=WORK:;;Project Rd 5;Krakow;PL-MA;01-001;PL" in text
    assert "URL;TYPE=WORK:https://proj.example.com" in text
    assert "X-NIP" not in text


def test_vcard_rev_updated_at():
    contact = _VcardContact(
        company=None,
        project=None,
        updated_at=datetime.datetime(2025, 6, 15, 9, 30, 0),
        created_at=datetime.datetime(2025, 1, 1, 0, 0, 0),
    )
    text = _render_vcard(contact)
    assert "REV:20250615T093000Z" in text


def test_vcard_rev_fallback_created_at():
    contact = _VcardContact(
        company=None,
        project=None,
        updated_at=None,
        created_at=datetime.datetime(2025, 3, 10, 7, 0, 0),
    )
    text = _render_vcard(contact)
    assert "REV:20250310T070000Z" in text


def test_vcard_uid():
    contact = _VcardContact(id=99, company=None, project=None)
    text = _render_vcard(contact)
    assert "UID:urn:uuid:contact-99" in text


def test_vcard_vescape_special_chars():
    co = _VcardCompany(
        name="Firm; & Co,",
        street=None,
        postcode=None,
        city=None,
        subdivision=None,
        country=None,
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    contact = _VcardContact(
        name="O'Brien, James; Jr.",
        role=None,
        phone=None,
        email=None,
        company=co,
        project=None,
        updated_at=None,
        created_at=None,
    )
    text = _render_vcard(contact)
    assert r"FN:O'Brien\, James\; Jr." in text
    assert r"ORG:Firm\; & Co\," in text


def test_vcard_empty_optional_fields():
    contact = _VcardContact(
        role=None,
        phone=None,
        email=None,
        company=None,
        project=None,
        updated_at=None,
        created_at=None,
    )
    text = _render_vcard(contact)
    assert "TITLE" not in text
    assert "ROLE" not in text
    assert "TEL" not in text
    assert "EMAIL" not in text
    assert "ORG" not in text
    assert "ADR" not in text
    assert "URL" not in text
    assert "REV" not in text


def test_vcard_company_no_address():
    co = _VcardCompany(
        street=None,
        postcode=None,
        city=None,
        subdivision=None,
        country=None,
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    contact = _VcardContact(company=co, project=None)
    text = _render_vcard(contact)
    assert "ORG:ACME Corp" in text
    assert "ADR" not in text
    assert "URL" not in text
    assert "X-NIP" not in text
