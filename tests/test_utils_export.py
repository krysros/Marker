from unittest.mock import patch

import pytest
from webob.multidict import MultiDict

from marker.utils import export


class DummyTranslationString:
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


def dummy_(msg):
    return DummyTranslationString(msg)


@pytest.mark.parametrize(
    "rows,header_row",
    [
        ([["A", "B", "C"]], ["Col1", "Col2", "Col3"]),
        ([["X", "Y", "Z"]], ["Name", "Role", "Email"]),
    ],
)
def test_response_xlsx_basic(rows, header_row):
    with patch.object(export, "_", dummy_):
        response = export.response_xlsx(rows, header_row)
        assert hasattr(response, "body_file")
        assert hasattr(response, "content_type")
        assert hasattr(response, "content_disposition")
        assert response.content_type.startswith(
            "application/vnd.openxmlformats-officedocument"
        )
        assert "attachment" in response.content_disposition


def test_response_xlsx_datetime_with_row_color():
    """Cover line 127: datetime cell with a colored row format."""
    import datetime

    rows = [[datetime.datetime(2024, 1, 15, 12, 0), "text"]]
    header_row = ["Date", "Name"]
    row_colors = ["primary"]
    with patch.object(export, "_", dummy_):
        response = export.response_xlsx(rows, header_row, row_colors=row_colors)
        assert response.body


def test_response_xlsx_row_color_formats_not_applied():
    """When row_colors is passed, no bg_color formats should be applied (coloring was removed)."""
    captured_formats = []

    class DummyWorksheet:
        def write(self, *args, **kwargs):
            return None

    class DummyWorkbook:
        def __init__(self, output, options):
            self.output = output
            self.options = options

        def add_worksheet(self):
            return DummyWorksheet()

        def add_format(self, options=None):
            captured_formats.append(options or {})
            return options or {}

        def close(self):
            return None

    with (
        patch.object(export, "_", dummy_),
        patch.object(export.xlsxwriter, "Workbook", DummyWorkbook),
    ):
        export.response_xlsx([["A"]], ["Name"], row_colors=["primary"])

    color_formats = [fmt for fmt in captured_formats if fmt.get("bg_color")]

    assert not color_formats


def test_apply_column_selection_unknown_keys_returns_original():
    rows = [["a", "b"]]
    header = ["Col1", "Col2"]
    filtered_rows, filtered_header, _ = export._apply_column_selection(
        rows, header, ["missing"]
    )
    assert filtered_rows == rows
    assert filtered_header == header


def test_apply_column_selection_subset_and_short_row_padding():
    rows = [["a"], ["x", "y"]]
    header = ["Col1", "Col2"]
    filtered_rows, filtered_header, _ = export._apply_column_selection(
        rows, header, ["Col2"]
    )
    assert filtered_header == ["Col2"]
    assert filtered_rows == [[None], ["y"]]


def test_make_export_response_csv_columns_to_ods():
    class DummyRequest:
        params = MultiDict({"format": "ods", "columns": "Col2,Col1"})

    rows = [["a", "b"]]
    header = ["Col1", "Col2"]

    with patch.object(export, "response_ods") as mock_ods:
        mock_ods.return_value = "ODS"
        result = export.make_export_response(DummyRequest(), rows, header)

    assert result == "ODS"
    called_rows, called_header = mock_ods.call_args[0]
    assert called_header == ["Col2", "Col1"]
    assert called_rows == [["b", "a"]]


def test_make_export_response_without_getall_uses_xlsx():
    class ParamsNoGetall(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    class DummyRequest:
        params = ParamsNoGetall({"format": "xlsx"})

    with patch.object(export, "response_xlsx") as mock_xlsx:
        mock_xlsx.return_value = "XLSX"
        result = export.make_export_response(DummyRequest(), [[1]], ["A"])

    assert result == "XLSX"
