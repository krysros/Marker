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


def test_parse_google_contacts_csv_bytes():
    csv_bytes = b"Organization Name,First Name,E-mail 1 - Value\nTestOrg,John,john@example.com\n"
    file = io.BytesIO(csv_bytes)
    reader, headers = parse_google_contacts_csv(file)
    assert reader is not None
    assert "Organization Name" in headers


def test_parse_google_contacts_csv_bytes_bom():
    csv_bytes = b"\xef\xbb\xbfOrganization Name,First Name\nTestOrg,John\n"
    file = io.BytesIO(csv_bytes)
    reader, headers = parse_google_contacts_csv(file)
    assert reader is not None
    assert "Organization Name" in headers


def test_parse_google_contacts_csv_exception():
    """Exception during read returns (None, set())."""

    class BadFile:
        def seekable(self):
            return False

        def read(self):
            raise IOError("fail")

    reader, headers = parse_google_contacts_csv(BadFile())
    assert reader is None
    assert headers == set()


def test_importer_add_row_no_company_name(dbsession):
    from marker.models.user import User
    from marker.utils.contact_csv_import import GoogleContactsCsvImporter
    from tests.conftest import DummyRequestWithIdentity

    user = User(
        name="csvnoco", fullname="U", email="csvnoco@e.com", role="admin", password="pw"
    )
    dbsession.add(user)
    dbsession.flush()
    importer = GoogleContactsCsvImporter(
        dbsession=dbsession, identity=user, geocode=lambda **kw: None
    )
    row = {"Organization Name": "", "First Name": "John"}
    assert importer.add_row(row) is False


def test_importer_add_row_no_name(dbsession):
    from marker.models.user import User
    from marker.utils.contact_csv_import import GoogleContactsCsvImporter

    user = User(
        name="csvnoname",
        fullname="U",
        email="csvnoname@e.com",
        role="admin",
        password="pw",
    )
    dbsession.add(user)
    dbsession.flush()
    importer = GoogleContactsCsvImporter(
        dbsession=dbsession, identity=user, geocode=lambda **kw: None
    )
    row = {"Organization Name": "TestCo", "First Name": "", "Last Name": "", "Name": ""}
    assert importer.add_row(row) is False


def test_importer_add_row_success(dbsession):
    import transaction

    from marker.models.user import User
    from marker.utils.contact_csv_import import GoogleContactsCsvImporter

    user = User(
        name="csvsucc", fullname="U", email="csvsucc@e.com", role="admin", password="pw"
    )
    dbsession.add(user)
    dbsession.flush()
    importer = GoogleContactsCsvImporter(
        dbsession=dbsession, identity=user, geocode=lambda **kw: None
    )
    row = {
        "Organization Name": "SuccCo",
        "First Name": "John",
        "Last Name": "Doe",
        "Middle Name": "",
        "Name Prefix": "",
        "Name Suffix": "",
        "Organization Title": "Engineer",
        "Organization Department": "",
        "Phone 1 - Value": "123456",
        "E-mail 1 - Value": "john@example.com",
        "Address 1 - Street": "Main St",
        "Address 1 - Postal Code": "00-000",
        "Address 1 - City": "Warsaw",
        "Address 1 - Region": "PL-14",
        "Address 1 - Country": "PL",
        "Website 1 - Value": "",
        "Labels": "Friends:::Work",
        "Notes": "Test note",
    }
    assert importer.add_row(row) is True


def test_importer_add_row_duplicate(dbsession):
    from marker.models.user import User
    from marker.utils.contact_csv_import import GoogleContactsCsvImporter

    user = User(
        name="csvdup", fullname="U", email="csvdup@e.com", role="admin", password="pw"
    )
    dbsession.add(user)
    dbsession.flush()
    importer = GoogleContactsCsvImporter(
        dbsession=dbsession, identity=user, geocode=lambda **kw: None
    )
    row = {
        "Organization Name": "DupCo",
        "First Name": "Jane",
        "Last Name": "Doe",
        "Middle Name": "",
        "Name Prefix": "",
        "Name Suffix": "",
        "Organization Title": "",
        "Organization Department": "Sales",
        "Phone 1 - Value": "999",
        "E-mail 1 - Value": "noemail",
        "Address 1 - Street": "",
        "Address 1 - Postal Code": "",
        "Address 1 - City": "",
        "Address 1 - Region": "",
        "Address 1 - Country": "",
        "Website 1 - Value": "",
        "Labels": "",
        "Notes": "",
    }
    assert importer.add_row(row) is True
    # Second time same data → duplicate, should return False
    assert importer.add_row(row) is False


def test_parse_google_contacts_csv_unicode_decode_error():
    """Cover lines 27-28: UnicodeDecodeError fallback."""
    # bytes with invalid UTF-8 sequence
    file = io.BytesIO(b"Name\xff\xfe\nJohn\n")
    reader, headers = parse_google_contacts_csv(file)
    assert reader is not None


def test_parse_google_contacts_csv_sniff_error():
    """Cover lines 38-39: csv.Sniffer fails → fallback to csv.excel."""
    # Very short content that confuses sniffer
    file = io.StringIO("a\n1\n")
    reader, headers = parse_google_contacts_csv(file)
    assert reader is not None


def test_importer_add_row_with_geocode(dbsession):
    """Cover lines 167-168: geocode returns location for new company."""
    from marker.models.user import User
    from marker.utils.contact_csv_import import GoogleContactsCsvImporter

    user = User(
        name="csvgeo", fullname="U", email="csvgeo@e.com", role="admin", password="pw"
    )
    dbsession.add(user)
    dbsession.flush()
    importer = GoogleContactsCsvImporter(
        dbsession=dbsession,
        identity=user,
        geocode=lambda **kw: {"lat": 50.0, "lon": 20.0},
    )
    row = {
        "Organization Name": "GeoCo",
        "First Name": "Geo",
        "Last Name": "User",
        "Middle Name": "",
        "Name Prefix": "",
        "Name Suffix": "",
        "Organization Title": "",
        "Organization Department": "",
        "Phone 1 - Value": "123",
        "E-mail 1 - Value": "geo@e.com",
        "Address 1 - Street": "Main St",
        "Address 1 - Postal Code": "00-000",
        "Address 1 - City": "Warsaw",
        "Address 1 - Region": "",
        "Address 1 - Country": "PL",
        "Website 1 - Value": "",
        "Labels": "",
        "Notes": "",
    }
    assert importer.add_row(row) is True
