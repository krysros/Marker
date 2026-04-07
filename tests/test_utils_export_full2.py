
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


def test_response_xlsx_safe_cell_value_custom_type():
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
