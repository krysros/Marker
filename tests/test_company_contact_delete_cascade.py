from types import SimpleNamespace

from sqlalchemy import delete, select

from marker import models
from marker.views.company import CompanyView
from marker.views.user import UserView


class _FlashSession:
    def __init__(self):
        self.messages = []

    def flash(self, message):
        self.messages.append(message)


class _Response:
    def __init__(self):
        self.headers = {}
        self.status_code = None


def _create_user(dbsession, name="delete-admin"):
    user = models.user.User(
        name=name,
        password="admin",
        fullname="Delete Admin",
        email=f"{name}@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()
    return user


def _create_company_with_contact(user, suffix):
    company = models.company.Company(
        name=f"Cascade Company {suffix}",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
        court="",
    )
    company.created_by = user

    contact = models.contact.Contact(
        name=f"Cascade Contact {suffix}",
        role="",
        phone="",
        email=f"cascade.{suffix}@example.com",
        color="",
    )
    contact.created_by = user
    company.contacts.append(contact)
    return company, contact


def _request_stub(dbsession, user, context):
    return SimpleNamespace(
        translate=lambda text: text,
        context=context,
        identity=user,
        dbsession=dbsession,
        session=_FlashSession(),
        response=_Response(),
        route_url=lambda route_name, **kwargs: f"/{route_name}",
        headers={},
        referrer=None,
    )


def test_delete_company_removes_assigned_contacts(dbsession):
    user = _create_user(dbsession, "single-company-delete-admin")
    company, contact = _create_company_with_contact(user, "single")
    dbsession.add(company)
    dbsession.flush()

    selector = _create_user(dbsession, "single-company-selected-contact-user")
    selector.selected_contacts.append(contact)
    dbsession.flush()

    company_id = company.id
    contact_id = contact.id

    request = _request_stub(dbsession, user, SimpleNamespace(company=company))
    response = CompanyView(request).delete()
    dbsession.flush()

    assert response.status_code == 303
    assert (
        dbsession.execute(
            select(models.Company).where(models.Company.id == company_id)
        ).scalar_one_or_none()
        is None
    )
    assert (
        dbsession.execute(
            select(models.Contact).where(models.Contact.id == contact_id)
        ).scalar_one_or_none()
        is None
    )
    assert (
        dbsession.execute(
            select(models.selected_contacts.c.contact_id).where(
                models.selected_contacts.c.contact_id == contact_id
            )
        )
        .scalars()
        .all()
        == []
    )


def test_delete_selected_companies_removes_assigned_contacts(dbsession):
    user = _create_user(dbsession, "bulk-company-delete-admin")

    company_1, contact_1 = _create_company_with_contact(user, "bulk-1")
    company_2, contact_2 = _create_company_with_contact(user, "bulk-2")
    dbsession.add(company_1)
    dbsession.add(company_2)
    dbsession.flush()

    company_1_id = company_1.id
    company_2_id = company_2.id
    contact_1_id = contact_1.id
    contact_2_id = contact_2.id

    user.selected_companies.append(company_1)
    user.selected_companies.append(company_2)

    selector = _create_user(dbsession, "bulk-company-selected-contact-user")
    selector.selected_contacts.append(contact_1)
    selector.selected_contacts.append(contact_2)
    dbsession.flush()

    request = _request_stub(dbsession, user, SimpleNamespace(user=user))
    response = UserView(request).delete_selected_companies()
    dbsession.flush()

    assert response.status_code == 303
    assert (
        dbsession.execute(
            select(models.Company).where(
                models.Company.id.in_([company_1_id, company_2_id])
            )
        )
        .scalars()
        .all()
        == []
    )
    assert (
        dbsession.execute(
            select(models.Contact).where(
                models.Contact.id.in_([contact_1_id, contact_2_id])
            )
        )
        .scalars()
        .all()
        == []
    )
    assert (
        dbsession.execute(
            select(models.selected_contacts.c.contact_id).where(
                models.selected_contacts.c.contact_id.in_([contact_1_id, contact_2_id])
            )
        )
        .scalars()
        .all()
        == []
    )


def test_raw_company_delete_cascades_to_contacts(dbsession):
    user = _create_user(dbsession, "raw-company-delete-admin")
    company, contact = _create_company_with_contact(user, "raw")
    dbsession.add(company)
    dbsession.flush()

    selector = _create_user(dbsession, "raw-company-selected-contact-user")
    selector.selected_contacts.append(contact)
    dbsession.flush()

    company_id = company.id
    contact_id = contact.id

    dbsession.execute(delete(models.Company).where(models.Company.id == company_id))
    dbsession.flush()

    assert (
        dbsession.execute(
            select(models.Company).where(models.Company.id == company_id)
        ).scalar_one_or_none()
        is None
    )
    assert (
        dbsession.execute(
            select(models.Contact).where(models.Contact.id == contact_id)
        ).scalar_one_or_none()
        is None
    )
    assert (
        dbsession.execute(
            select(models.selected_contacts.c.contact_id).where(
                models.selected_contacts.c.contact_id == contact_id
            )
        )
        .scalars()
        .all()
        == []
    )
