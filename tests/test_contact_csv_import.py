from io import BytesIO

from sqlalchemy import select

from marker import models
from marker.utils.contact_csv_import import (
    GoogleContactsCsvImporter,
    missing_google_contacts_columns,
    parse_google_contacts_csv,
)


def _create_user(dbsession, name):
    user = models.user.User(
        name=name,
        password="admin",
        fullname="CSV Import Tester",
        email=f"{name}@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()
    return user


def test_google_contacts_header_aliases_are_accepted():
    headers = {
        "Organization 1 - Name",
        "Given Name",
        "E-mail 1 - Value",
        "Phone 1 - Value",
        "Group Membership",
    }

    assert missing_google_contacts_columns(headers) == []


def test_google_contacts_header_notes_is_optional():
    headers = {
        "Organization 1 - Name",
        "Given Name",
        "E-mail 1 - Value",
        "Phone 1 - Value",
        "Group Membership",
    }

    assert missing_google_contacts_columns(headers) == []


def test_parse_csv_supports_utf8_bom_and_comma_separator():
    payload = (
        "\ufeffOrganization 1 - Name,Given Name,E-mail 1 - Value,"
        "Phone 1 - Value,Group Membership,Notes\n"
        "Acme,Jan,jan@example.com,123456789,Klienci ::: * My Contacts,Wazny\n"
    ).encode("utf-8")

    reader, headers = parse_google_contacts_csv(BytesIO(payload))

    assert reader is not None
    assert missing_google_contacts_columns(headers) == []

    row = next(reader)
    assert row["Organization 1 - Name"] == "Acme"
    assert row["Given Name"] == "Jan"


def test_parse_csv_rejects_semicolon_separator():
    payload = (
        "Organization 1 - Name;Given Name;E-mail 1 - Value;"
        "Phone 1 - Value;Group Membership;Notes\n"
        "Acme;Jan;jan@example.com;123456789;Klienci ::: * My Contacts;Wazny\n"
    ).encode("utf-8")

    reader, headers = parse_google_contacts_csv(BytesIO(payload))

    assert reader is None
    assert headers == set()


def test_add_row_supports_google_alias_columns(dbsession):
    user = _create_user(dbsession, "google-csv-import-user")
    importer = GoogleContactsCsvImporter(
        dbsession=dbsession,
        identity=user,
        geocode=lambda **kwargs: None,
    )

    row = {
        "Organization 1 - Name": "Acme",
        "Address 1 - Street": "ul. Testowa 1",
        "Address 1 - Postal Code": "00-001",
        "Address 1 - City": "Warszawa",
        "Address 1 - Region": "Mazowieckie",
        "Address 1 - Country": "Poland",
        "Website 1 - Value": "https://acme.example.com",
        "Group Membership": "Klienci ::: * My Contacts",
        "Notes": "Wazny klient",
        "Given Name": "jan",
        "Name Prefix": "dr",
        "Additional Name": "adam",
        "Family Name": "kowalski",
        "Name Suffix": "PhD",
        "Organization 1 - Title": "CEO",
        "Organization 1 - Department": "Sales",
        "Phone 1 - Value": "123456789",
        "E-mail 1 - Value": "jan.kowalski@example.com",
    }

    added = importer.add_row(row)
    dbsession.flush()

    assert added is True

    company = dbsession.execute(
        select(models.Company).filter_by(name="Acme")
    ).scalar_one()

    assert company.street == "ul. Testowa 1"
    assert {tag.name for tag in company.tags} == {"Klienci"}
    assert [comment.comment for comment in company.comments] == ["Wazny klient"]

    assert len(company.contacts) == 1
    contact = company.contacts[0]
    assert contact.name == "dr Jan Adam Kowalski PhD"
    assert contact.role == "CEO"
    assert contact.phone == "123456789"
    assert contact.email == "jan.kowalski@example.com"


def test_add_row_skips_duplicate_contact_for_same_company(
    dbsession,
):
    user = _create_user(dbsession, "google-csv-import-dedup-user")
    importer = GoogleContactsCsvImporter(
        dbsession=dbsession,
        identity=user,
        geocode=lambda **kwargs: None,
    )

    row = {
        "Organization 1 - Name": "Acme",
        "Address 1 - Street": "ul. Testowa 1",
        "Address 1 - Postal Code": "00-001",
        "Address 1 - City": "Warszawa",
        "Address 1 - Region": "Mazowieckie",
        "Address 1 - Country": "Poland",
        "Website 1 - Value": "https://acme.example.com",
        "Group Membership": "Klienci ::: * My Contacts",
        "Notes": "Wazny klient",
        "Given Name": "jan",
        "Name Prefix": "dr",
        "Additional Name": "adam",
        "Family Name": "kowalski",
        "Name Suffix": "PhD",
        "Organization 1 - Title": "CEO",
        "Organization 1 - Department": "Sales",
        "Phone 1 - Value": "123456789",
        "E-mail 1 - Value": "jan.kowalski@example.com",
    }

    added_first = importer.add_row(row)
    added_second = importer.add_row(row)
    dbsession.flush()

    assert added_first is True
    assert added_second is False

    company = dbsession.execute(
        select(models.Company).filter_by(name="Acme")
    ).scalar_one()
    assert len(company.contacts) == 1
    assert len(company.comments) == 1
