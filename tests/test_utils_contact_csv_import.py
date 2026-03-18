import io

import pytest

from marker.utils.contact_csv_import import (
    csv_row_value,
    missing_google_contacts_columns,
    normalize_csv_header,
    parse_google_contacts_csv,
)


@pytest.mark.parametrize(
    "header,expected",
    [
        ("\ufeffOrganization Name", "Organization Name"),
        ("  First Name  ", "First Name"),
        (None, ""),
    ],
)
def test_normalize_csv_header(header, expected):
    assert normalize_csv_header(header) == expected


@pytest.mark.parametrize(
    "row,columns,expected",
    [
        ({"A": "foo", "B": "bar"}, ["A", "B"], "foo"),
        ({"A": "", "B": "bar"}, ["A", "B"], "bar"),
        ({"A": "", "B": ""}, ["A", "B"], ""),
    ],
)
def test_csv_row_value(row, columns, expected):
    assert csv_row_value(row, *columns) == expected


def test_parse_google_contacts_csv_valid():
    csv_data = (
        "Organization Name,First Name,E-mail 1 - Value\nTestOrg,John,john@example.com\n"
    )
    file = io.StringIO(csv_data)
    reader, headers = parse_google_contacts_csv(file)
    assert reader is not None
    assert "Organization Name" in headers
    assert "First Name" in headers
    rows = list(reader)
    assert rows[0]["Organization Name"] == "TestOrg"
    assert rows[0]["First Name"] == "John"
    assert rows[0]["E-mail 1 - Value"] == "john@example.com"


def test_parse_google_contacts_csv_invalid_delimiter():
    csv_data = (
        "Organization Name;First Name;E-mail 1 - Value\nTestOrg;John;john@example.com\n"
    )
    file = io.StringIO(csv_data)
    reader, headers = parse_google_contacts_csv(file)
    assert reader is None
    assert headers == set()


def test_missing_google_contacts_columns():
    headers = [
        "Organization Name",
        "First Name",
        "E-mail 1 - Value",
        "Phone 1 - Value",
        "Labels",
    ]
    missing = missing_google_contacts_columns(headers)
    assert missing == []
    headers = ["First Name", "E-mail 1 - Value"]
    missing = missing_google_contacts_columns(headers)
    assert "Organization Name" in missing
    assert "Phone 1 - Value" in missing
    assert "Labels" in missing
