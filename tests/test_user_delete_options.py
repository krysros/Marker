import datetime
from types import SimpleNamespace

from sqlalchemy import select

from marker import models
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


def _create_user(dbsession, name, role="admin"):
    user = models.user.User(
        name=name,
        password="admin",
        fullname=f"{name} Fullname",
        email=f"{name}@example.com",
        role=role,
    )
    dbsession.add(user)
    dbsession.flush()
    return user


def _create_user_dataset(dbsession, creator, suffix):
    company = models.company.Company(
        name=f"User Delete Company {suffix}",
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
        # court removed
    )
    company.created_by = creator

    project = models.project.Project(
        name=f"User Delete Project {suffix}",
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
    project.created_by = creator

    tag = models.tag.Tag(name=f"UserDeleteTag{suffix}")
    tag.created_by = creator
    tag.companies.append(company)
    tag.projects.append(project)

    company_contact = models.contact.Contact(
        name=f"User Delete Company Contact {suffix}",
        role="",
        phone="",
        email=f"company.contact.{suffix}@example.com",
        color="",
    )
    company_contact.created_by = creator
    company_contact.company = company

    standalone_contact = models.contact.Contact(
        name=f"User Delete Standalone Contact {suffix}",
        role="",
        phone="",
        email=f"standalone.contact.{suffix}@example.com",
        color="",
    )
    standalone_contact.created_by = creator

    company_comment = models.comment.Comment(f"User delete company comment {suffix}")
    company_comment.created_by = creator
    company_comment.company = company

    project_comment = models.comment.Comment(f"User delete project comment {suffix}")
    project_comment.created_by = creator
    project_comment.project = project

    dbsession.add_all(
        [
            company,
            project,
            tag,
            company_contact,
            standalone_contact,
            company_comment,
            project_comment,
        ]
    )
    dbsession.flush()

    return {
        "company": company,
        "project": project,
        "tag": tag,
        "company_contact": company_contact,
        "standalone_contact": standalone_contact,
        "company_comment": company_comment,
        "project_comment": project_comment,
    }


def _request_stub(dbsession, identity, target_user, delete_with_data=None):
    params = {}
    if delete_with_data is not None:
        params["delete_with_data"] = delete_with_data

    return SimpleNamespace(
        translate=lambda text: text,
        context=SimpleNamespace(user=target_user),
        identity=identity,
        dbsession=dbsession,
        params=params,
        session=_FlashSession(),
        response=_Response(),
        route_url=lambda route_name, **kwargs: f"/{route_name}",
        headers={},
        referrer=None,
    )


def test_delete_user_default_removes_account_only(dbsession):
    admin = _create_user(dbsession, "delete-user-default-admin", role="admin")
    target = _create_user(dbsession, "delete-user-default-target", role="editor")

    dataset = _create_user_dataset(dbsession, target, "default")

    company_id = dataset["company"].id
    project_id = dataset["project"].id
    tag_id = dataset["tag"].id
    contact_id = dataset["standalone_contact"].id
    company_comment_id = dataset["company_comment"].id

    request = _request_stub(dbsession, admin, target)
    response = UserView(request).delete()
    dbsession.flush()

    assert response.status_code == 303
    assert response.headers.get("HX-Redirect") == "/home"

    assert (
        dbsession.execute(
            select(models.User).where(models.User.id == target.id)
        ).scalar_one_or_none()
        is None
    )

    company = dbsession.execute(
        select(models.Company).where(models.Company.id == company_id)
    ).scalar_one_or_none()
    project = dbsession.execute(
        select(models.Project).where(models.Project.id == project_id)
    ).scalar_one_or_none()
    tag = dbsession.execute(
        select(models.Tag).where(models.Tag.id == tag_id)
    ).scalar_one_or_none()
    contact = dbsession.execute(
        select(models.Contact).where(models.Contact.id == contact_id)
    ).scalar_one_or_none()
    comment = dbsession.execute(
        select(models.Comment).where(models.Comment.id == company_comment_id)
    ).scalar_one_or_none()

    assert company is not None
    assert project is not None
    assert tag is not None
    assert contact is not None
    assert comment is not None


def test_delete_user_with_data_removes_created_records(dbsession):
    admin = _create_user(dbsession, "delete-user-with-data-admin", role="admin")
    target = _create_user(dbsession, "delete-user-with-data-target", role="editor")
    watcher = _create_user(dbsession, "delete-user-with-data-watcher", role="editor")

    dataset = _create_user_dataset(dbsession, target, "with-data")

    watcher.companies_stars.append(dataset["company"])
    watcher.projects_stars.append(dataset["project"])
    watcher.selected_companies.append(dataset["company"])
    watcher.selected_projects.append(dataset["project"])
    watcher.selected_tags.append(dataset["tag"])
    watcher.selected_contacts.append(dataset["company_contact"])
    watcher.selected_contacts.append(dataset["standalone_contact"])

    watcher_company = models.company.Company(
        name="Watcher Company Should Stay",
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
        # court removed
    )
    watcher_company.created_by = watcher
    dbsession.add(watcher_company)

    dbsession.flush()

    company_id = dataset["company"].id
    project_id = dataset["project"].id
    tag_id = dataset["tag"].id
    company_contact_id = dataset["company_contact"].id
    standalone_contact_id = dataset["standalone_contact"].id
    company_comment_id = dataset["company_comment"].id
    project_comment_id = dataset["project_comment"].id
    watcher_company_id = watcher_company.id

    request = _request_stub(dbsession, admin, target, delete_with_data="1")
    response = UserView(request).delete()
    dbsession.flush()

    assert response.status_code == 303
    assert response.headers.get("HX-Redirect") == "/home"

    assert (
        dbsession.execute(
            select(models.User).where(models.User.id == target.id)
        ).scalar_one_or_none()
        is None
    )

    assert (
        dbsession.execute(
            select(models.Company).where(models.Company.id == company_id)
        ).scalar_one_or_none()
        is None
    )
    assert (
        dbsession.execute(
            select(models.Project).where(models.Project.id == project_id)
        ).scalar_one_or_none()
        is None
    )
    assert (
        dbsession.execute(
            select(models.Tag).where(models.Tag.id == tag_id)
        ).scalar_one_or_none()
        is None
    )
    assert (
        dbsession.execute(
            select(models.Contact).where(
                models.Contact.id.in_([company_contact_id, standalone_contact_id])
            )
        )
        .scalars()
        .all()
        == []
    )
    assert (
        dbsession.execute(
            select(models.Comment).where(
                models.Comment.id.in_([company_comment_id, project_comment_id])
            )
        )
        .scalars()
        .all()
        == []
    )

    assert (
        dbsession.execute(
            select(models.Company).where(models.Company.id == watcher_company_id)
        ).scalar_one_or_none()
        is not None
    )

    assert (
        dbsession.execute(
            select(models.selected_companies.c.company_id).where(
                models.selected_companies.c.company_id == company_id
            )
        )
        .scalars()
        .all()
        == []
    )
    assert (
        dbsession.execute(
            select(models.selected_projects.c.project_id).where(
                models.selected_projects.c.project_id == project_id
            )
        )
        .scalars()
        .all()
        == []
    )
    assert (
        dbsession.execute(
            select(models.selected_tags.c.tag_id).where(
                models.selected_tags.c.tag_id == tag_id
            )
        )
        .scalars()
        .all()
        == []
    )
    assert (
        dbsession.execute(
            select(models.selected_contacts.c.contact_id).where(
                models.selected_contacts.c.contact_id.in_(
                    [company_contact_id, standalone_contact_id]
                )
            )
        )
        .scalars()
        .all()
        == []
    )
    assert (
        dbsession.execute(
            select(models.companies_stars.c.company_id).where(
                models.companies_stars.c.company_id == company_id
            )
        )
        .scalars()
        .all()
        == []
    )
    assert (
        dbsession.execute(
            select(models.projects_stars.c.project_id).where(
                models.projects_stars.c.project_id == project_id
            )
        )
        .scalars()
        .all()
        == []
    )


def test_user_view_has_delete_with_data_option(testapp, dbsession):
    admin = _create_user(dbsession, "delete-user-view-admin", role="admin")
    target = _create_user(dbsession, "delete-user-view-target", role="editor")

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = admin.name
    form["password"] = "admin"
    form.submit(status=303)

    response = testapp.get(f"/user/{target.name}", status=200)

    assert f"/user/{target.name}/delete" in response.text
    assert "hx-vals=" in response.text
    assert '"delete_with_data": "1"' in response.text
