import pytest

from marker.utils.website_autofill import (
    _CITY_POSTCODE_LINE_RE,
    _KRS_RE,
    _NIP_RE,
    _POSTCODE_CITY_LINE_RE,
    _POSTCODE_RE,
    _REGON_RE,
    _STREET_RE,
)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("ul. Kwiatowa 12", True),
        ("ulica Długa 5", True),
        ("Kwiatowa", False),
    ],
)
def test_street_regex(text, expected):
    match = _STREET_RE.search(text)
    assert (match is not None) == expected


@pytest.mark.parametrize(
    "text,pattern,expected",
    [
        ("00-123 Warszawa", _POSTCODE_CITY_LINE_RE, True),
        ("Warszawa 00-123", _CITY_POSTCODE_LINE_RE, True),
        ("12345", _POSTCODE_CITY_LINE_RE, False),
        ("12345", _CITY_POSTCODE_LINE_RE, False),
    ],
)
def test_postcode_city_line_regex(text, pattern, expected):
    match = pattern.search(text)
    assert (match is not None) == expected


@pytest.mark.parametrize(
    "text,pattern,expected",
    [
        ("NIP: 123-456-32-18", _NIP_RE, True),
        ("REGON: 123456789", _REGON_RE, True),
        ("KRS: 0000123456", _KRS_RE, True),
        ("No match", _POSTCODE_RE, False),
    ],
)
def test_id_regex(text, pattern, expected):
    match = pattern.search(text)
    assert (match is not None) == expected
