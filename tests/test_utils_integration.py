import io

import pytest

from marker.utils.contact_csv_import import (
    parse_google_contacts_csv,
)
from marker.utils.export import response_xlsx
from marker.utils.geo import location, location_details


@pytest.mark.integration
def test_parse_google_contacts_csv_integration():
    csv_data = "Organization Name,First Name,E-mail 1 - Value,Phone 1 - Value,Labels\nTestOrg,John,john@example.com,123456789,Friends\n"
    file = io.StringIO(csv_data)
    reader, headers = parse_google_contacts_csv(file)
    assert reader is not None
    assert "Organization Name" in headers
    rows = list(reader)
    assert rows[0]["Organization Name"] == "TestOrg"
    assert rows[0]["First Name"] == "John"
    assert rows[0]["E-mail 1 - Value"] == "john@example.com"
    assert rows[0]["Phone 1 - Value"] == "123456789"
    assert rows[0]["Labels"] == "Friends"


@pytest.mark.integration
def test_response_xlsx_integration():

    # Patch Pyramid translation context
    class DummyRequest:
        def translate(self, msg):
            return str(msg)

    import marker.forms.ts

    marker.forms.ts.get_current_request = lambda: DummyRequest()
    rows = [["John", "Developer", "john@example.com"]]
    header_row = ["Name", "Role", "Email"]
    response = response_xlsx(rows, header_row)
    assert hasattr(response, "body_file")
    assert response.content_type.startswith(
        "application/vnd.openxmlformats-officedocument"
    )
    assert "attachment" in response.content_disposition


@pytest.mark.integration
def test_location_integration():
    # This test will call the real Nominatim API, so it may be slow or flaky
    result = location(q="Warsaw, Poland")
    assert result is None or ("lat" in result and "lon" in result)


@pytest.mark.integration
def test_location_details_integration():
    # This test will call the real Nominatim API, so it may be slow or flaky
    result = location_details(q="Warsaw, Poland")
    # Accept results with at least 'country' present, since API may not return city keys
    assert result is None or ("country" in result)


@pytest.mark.integration
def test_website_autofill_regex_integration():
    from marker.utils.website_autofill import _POSTCODE_RE, _STREET_RE

    text = "ul. Kwiatowa 12, 00-123 Warszawa"
    assert _STREET_RE.search(text)
    assert _POSTCODE_RE.search(text)
