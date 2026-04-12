import datetime

import pytest

import marker.forms.ts
from marker.utils import export


@pytest.fixture(autouse=True)
def patch_translationstring_str(monkeypatch):
    monkeypatch.setattr(
        marker.forms.ts.TranslationString, "__str__", lambda self: self.msg
    )
    yield


def test_response_xlsx_basic():
    rows = [["A", "B", "C"], [1, 2, 3]]
    header_row = ["Col1", "Col2", "Col3"]
    response = export.response_xlsx(rows, header_row)
    assert hasattr(response, "body_file")
    assert response.content_type.startswith(
        "application/vnd.openxmlformats-officedocument"
    )
    assert "attachment" in response.content_disposition
    # Check that the file is not empty
    content = response.body
    assert len(content) > 0


def test_response_xlsx_empty_rows():
    rows = []
    header_row = ["Col1", "Col2"]
    response = export.response_xlsx(rows, header_row)
    content = response.body
    assert len(content) > 0


def test_response_xlsx_special_characters():
    rows = [["ąęćłńóśżź", "A&B", "<script>"]]
    header_row = ["Polish", "Ampersand", "HTML"]
    response = export.response_xlsx(rows, header_row)
    content = response.body
    assert len(content) > 0


def test_response_xlsx_date_formats():
    today = datetime.date.today()
    rows = [[today, today, today]]
    header_row = ["D1", "D2", "D3"]
    response = export.response_xlsx(rows, header_row, default_date_format="dd-mm-yyyy")
    content = response.body
    assert len(content) > 0


def test_response_xlsx_row_colors():
    rows = [["A", "B", "C"], [1, 2, 3]]
    header_row = ["Col1", "Col2", "Col3"]
    row_colors = ["primary", "danger"]
    response = export.response_xlsx(rows, header_row, row_colors=row_colors)
    content = response.body
    assert len(content) > 0


def test_response_ods_basic():
    rows = [["A", "B", "C"], [1, 2, 3]]
    header_row = ["Col1", "Col2", "Col3"]
    response = export.response_ods(rows, header_row)
    assert response.content_type == "application/vnd.oasis.opendocument.spreadsheet"
    assert "attachment" in response.content_disposition
    assert "Marker.ods" in response.content_disposition
    assert len(response.body) > 0


def test_response_ods_empty_rows():
    rows = []
    header_row = ["Col1", "Col2"]
    response = export.response_ods(rows, header_row)
    assert len(response.body) > 0


def test_response_ods_special_characters():
    rows = [["ąęćłńóśżź", "A&B", "<script>"]]
    header_row = ["Polish", "Ampersand", "HTML"]
    response = export.response_ods(rows, header_row)
    assert len(response.body) > 0


def test_response_ods_date_values():
    today = datetime.date.today()
    rows = [[today, "text"]]
    header_row = ["Date", "Name"]
    response = export.response_ods(rows, header_row)
    assert len(response.body) > 0


def test_response_ods_row_colors():
    rows = [["A", "B", "C"], [1, 2, 3]]
    header_row = ["Col1", "Col2", "Col3"]
    row_colors = ["primary", "danger"]
    response = export.response_ods(rows, header_row, row_colors=row_colors)
    assert len(response.body) > 0


def test_response_ods_none_values():
    rows = [[None, "text", None]]
    header_row = ["Col1", "Col2", "Col3"]
    response = export.response_ods(rows, header_row)
    assert len(response.body) > 0


def test_response_ods_float_values():
    rows = [[1.5, 2.7, 3.14]]
    header_row = ["A", "B", "C"]
    response = export.response_ods(rows, header_row)
    assert len(response.body) > 0


def test_response_ods_column_transformers():
    """Cover lines 365-366: column_transformers branch in response_ods."""
    rows = [["PL-14", "PL", "text"]]
    header_row = ["Subdivision", "Country", "Name"]
    response = export.response_ods(rows, header_row)
    assert len(response.body) > 0
