import datetime
from types import SimpleNamespace

from sqlalchemy import delete, select

from marker import models
from marker.views.project import ProjectView
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


def _create_user(dbsession, name="delete-project-admin"):
    user = models.user.User(
        name=name,
        password="admin",
        fullname="Delete Project Admin",
        email=f"{name}@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()
    return user


def _create_project_with_contact(user, suffix):
    project = models.project.Project(
        name=f"Cascade Project {suffix}",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="",
        website="",
        color="",
        deadline=datetime.datetime.now(),
        stage="",
        delivery_method="",
    )
    project.created_by = user

    contact = models.contact.Contact(
        name=f"Project Contact {suffix}",
        role="",
        phone="",
        email=f"project.contact.{suffix}@example.com",
        color="",
    )
    contact.created_by = user
    project.contacts.append(contact)
    return project, contact


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


def test_delete_project_removes_assigned_contacts(dbsession):
    user = _create_user(dbsession, "single-project-delete-admin")
    project, contact = _create_project_with_contact(user, "single")
    dbsession.add(project)
    dbsession.flush()

    selector = _create_user(dbsession, "single-project-selected-contact-user")
    selector.selected_contacts.append(contact)
    dbsession.flush()

    project_id = project.id
    contact_id = contact.id

    request = _request_stub(dbsession, user, SimpleNamespace(project=project))
    response = ProjectView(request).delete()
    dbsession.flush()

    assert response.status_code == 303
    assert (
        dbsession.execute(
            select(models.Project).where(models.Project.id == project_id)
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


def test_delete_selected_projects_removes_assigned_contacts(dbsession):
    user = _create_user(dbsession, "bulk-project-delete-admin")

    project_1, contact_1 = _create_project_with_contact(user, "bulk-1")
    project_2, contact_2 = _create_project_with_contact(user, "bulk-2")
    dbsession.add(project_1)
    dbsession.add(project_2)
    dbsession.flush()

    project_1_id = project_1.id
    project_2_id = project_2.id
    contact_1_id = contact_1.id
    contact_2_id = contact_2.id

    user.selected_projects.append(project_1)
    user.selected_projects.append(project_2)

    selector = _create_user(dbsession, "bulk-project-selected-contact-user")
    selector.selected_contacts.append(contact_1)
    selector.selected_contacts.append(contact_2)
    dbsession.flush()

    request = _request_stub(dbsession, user, SimpleNamespace(user=user))
    response = UserView(request).delete_selected_projects()
    dbsession.flush()

    assert response.status_code == 303
    assert (
        dbsession.execute(
            select(models.Project).where(
                models.Project.id.in_([project_1_id, project_2_id])
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


def test_raw_project_delete_cascades_to_contacts(dbsession):
    user = _create_user(dbsession, "raw-project-delete-admin")
    project, contact = _create_project_with_contact(user, "raw")
    dbsession.add(project)
    dbsession.flush()

    selector = _create_user(dbsession, "raw-project-selected-contact-user")
    selector.selected_contacts.append(contact)
    dbsession.flush()

    project_id = project.id
    contact_id = contact.id

    dbsession.execute(delete(models.Project).where(models.Project.id == project_id))
    dbsession.flush()

    assert (
        dbsession.execute(
            select(models.Project).where(models.Project.id == project_id)
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
