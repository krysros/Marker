from unittest.mock import patch

import pytest

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


def test_response_xlsx_row_color_formats_use_fill_without_borders():
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

    with patch.object(export, "_", dummy_), patch.object(
        export.xlsxwriter, "Workbook", DummyWorkbook
    ):
        export.response_xlsx([["A"]], ["Name"], row_colors=["primary"])

    color_formats = [
        fmt
        for fmt in captured_formats
        if fmt.get("bg_color") == "#DCEBFF"
    ]

    assert color_formats
    for fmt in color_formats:
        assert fmt.get("border") == 0
        assert "font_color" not in fmt
        assert "border_color" not in fmt
        assert "top_color" not in fmt
        assert "right_color" not in fmt
        assert "bottom_color" not in fmt
        assert "left_color" not in fmt
