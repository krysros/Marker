import csv
from io import StringIO

from sqlalchemy import func, select

from ..models import Comment, Company, Contact, Tag

GOOGLE_CONTACTS_REQUIRED_COLUMNS = {
    "Organization Name": ("Organization Name", "Organization 1 - Name"),
    "First Name": ("First Name", "Given Name"),
    "E-mail 1 - Value": ("E-mail 1 - Value",),
    "Phone 1 - Value": ("Phone 1 - Value",),
    "Labels": ("Labels", "Group Membership"),
}


def parse_google_contacts_csv(file):
    try:
        if hasattr(file, "seek"):
            file.seek(0)

        data = file.read()
        if isinstance(data, bytes):
            try:
                # utf-8-sig strips BOM when present.
                text = data.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = data.decode("utf-8", errors="replace")
        else:
            text = str(data)
    except Exception:
        return None, set()

    f = StringIO(text)
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel

    if getattr(dialect, "delimiter", ",") != ",":
        return None, set()

    reader = csv.DictReader(f, dialect=dialect)
    if reader.fieldnames:
        reader.fieldnames = [
            normalize_csv_header(header) for header in reader.fieldnames
        ]
    headers = set(reader.fieldnames or [])
    return reader, headers


def missing_google_contacts_columns(headers):
    available_headers = {normalize_csv_header(header) for header in (headers or [])}
    missing_columns = []

    for display_name, aliases in GOOGLE_CONTACTS_REQUIRED_COLUMNS.items():
        if not any(alias in available_headers for alias in aliases):
            missing_columns.append(display_name)

    return missing_columns


def normalize_csv_header(header):
    if header is None:
        return ""
    return str(header).lstrip("\ufeff").strip()


def csv_row_value(row, *columns):
    for column in columns:
        value = row.get(column)
        if value is None:
            continue

        value = value.strip()
        if value:
            return value

    for column in columns:
        value = row.get(column)
        if value is not None:
            return value.strip()

    return ""


class GoogleContactsCsvImporter:
    def __init__(self, dbsession, identity, geocode):
        self.dbsession = dbsession
        self.identity = identity
        self.geocode = geocode

    @staticmethod
    def _same_contact_data(contact, name, role, phone, email):
        return (
            (contact.name or "") == name
            and (contact.role or "") == role
            and (contact.phone or "") == phone
            and (contact.email or "") == email
        )

    def _company_has_same_contact(self, company, name, role, phone, email):
        for existing_contact in company.contacts:
            if self._same_contact_data(
                existing_contact,
                name=name,
                role=role,
                phone=phone,
                email=email,
            ):
                return True

        existing_contact_id = self.dbsession.execute(
            select(Contact.id)
            .where(Contact.company_id == company.id)
            .where(Contact.name == name)
            .where(func.coalesce(Contact.role, "") == role)
            .where(func.coalesce(Contact.phone, "") == phone)
            .where(func.coalesce(Contact.email, "") == email)
            .limit(1)
        ).scalar_one_or_none()

        return existing_contact_id is not None

    def add_row(self, row):
        company_name = csv_row_value(
            row,
            "Organization Name",
            "Organization 1 - Name",
        )

        if not company_name:
            return False

        street = csv_row_value(row, "Address 1 - Street")
        postcode = csv_row_value(row, "Address 1 - Postal Code")
        city = csv_row_value(row, "Address 1 - City")
        subdivision = csv_row_value(row, "Address 1 - Region")
        country = csv_row_value(row, "Address 1 - Country")
        website = csv_row_value(row, "Website 1 - Value")

        company = self.dbsession.execute(
            select(Company).filter_by(name=company_name)
        ).scalar_one_or_none()
        if not company:
            company = Company(
                name=company_name,
                street=street,
                postcode=postcode,
                city=city,
                subdivision=subdivision,
                country=country,
                website=website,
                color="",
                NIP="",
                REGON="",
                KRS="",
            )
            loc = self.geocode(
                street=street,
                city=city,
                country=country,
                postalcode=postcode,
            )
            if loc is not None:
                company.latitude = loc["lat"]
                company.longitude = loc["lon"]

            company.created_by = self.identity
            self.dbsession.add(company)
            self.dbsession.flush()

        first_name = csv_row_value(row, "First Name", "Given Name", "Name")
        prefix = csv_row_value(row, "Name Prefix")
        middle_name = csv_row_value(row, "Middle Name", "Additional Name")
        last_name = csv_row_value(row, "Last Name", "Family Name")
        suffix = csv_row_value(row, "Name Suffix")

        name_parts = []
        if prefix:
            name_parts.append(prefix)
        if first_name:
            name_parts.append(first_name.title())
        if middle_name:
            name_parts.append(middle_name.title())
        if last_name:
            name_parts.append(last_name.title())
        if suffix:
            name_parts.append(suffix)

        name = " ".join(name_parts).strip()

        if not name:
            return False

        role = csv_row_value(
            row,
            "Organization Title",
            "Organization 1 - Title",
        )
        if not role:
            role = csv_row_value(
                row,
                "Organization Department",
                "Organization 1 - Department",
            )

        phone = csv_row_value(row, "Phone 1 - Value")
        email = csv_row_value(row, "E-mail 1 - Value")

        if "@" not in email:
            email = ""

        if self._company_has_same_contact(company, name, role, phone, email):
            return False

        labels = csv_row_value(row, "Labels", "Group Membership")
        tags = [
            label.strip()
            for label in labels.split(":::")
            if label.strip() and not label.strip().startswith("*")
        ]

        for tag_name in tags:
            tag = self.dbsession.execute(
                select(Tag).filter_by(name=tag_name)
            ).scalar_one_or_none()
            if not tag:
                tag = Tag(tag_name)
                tag.created_by = self.identity
            if tag not in company.tags:
                company.tags.append(tag)

        note = csv_row_value(row, "Notes")
        if note:
            comment = Comment(comment=note)
            comment.created_by = self.identity
            company.comments.append(comment)

        contact = Contact(
            name=name,
            role=role,
            phone=phone,
            email=email,
            color="",
        )
        contact.created_by = self.identity

        if contact not in company.contacts:
            company.contacts.append(contact)
            return True

        return False
