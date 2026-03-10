import datetime
from types import SimpleNamespace

from sqlalchemy import select

from marker import models
from marker.views.company import CompanyView
from marker.views.project import ProjectView


class _FlashSession:
    def __init__(self):
        self.messages = []

    def flash(self, message):
        self.messages.append(message)


class _Response:
    def __init__(self):
        self.headers = {}
        self.status_code = None


def _create_user(dbsession, name):
    user = models.user.User(
        name=name,
        password="admin",
        fullname="Star Delete Admin",
        email=f"{name}@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()
    return user


def _create_company(user, suffix):
    company = models.company.Company(
        name=f"Star Company {suffix}",
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
    return company


def _create_project(user, suffix):
    project = models.project.Project(
        name=f"Star Project {suffix}",
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
    return project


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


def test_delete_company_removes_stars_rows(dbsession):
    owner = _create_user(dbsession, "delete-company-star-owner")
    watcher = _create_user(dbsession, "delete-company-star-watcher")

    company = _create_company(owner, "delete")
    dbsession.add(company)
    dbsession.flush()

    watcher.companies_stars.append(company)
    dbsession.flush()

    company_id = company.id

    request = _request_stub(dbsession, owner, SimpleNamespace(company=company))
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
            select(models.companies_stars.c.company_id).where(
                models.companies_stars.c.company_id == company_id
            )
        )
        .scalars()
        .all()
        == []
    )


def test_del_row_company_removes_stars_rows(dbsession):
    owner = _create_user(dbsession, "del-row-company-star-owner")
    watcher = _create_user(dbsession, "del-row-company-star-watcher")

    company = _create_company(owner, "del-row")
    dbsession.add(company)
    dbsession.flush()

    watcher.companies_stars.append(company)
    dbsession.flush()

    company_id = company.id

    request = _request_stub(dbsession, owner, SimpleNamespace(company=company))
    response = CompanyView(request).del_row()
    dbsession.flush()

    assert response == ""
    assert (
        dbsession.execute(
            select(models.Company).where(models.Company.id == company_id)
        ).scalar_one_or_none()
        is None
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


def test_delete_project_removes_stars_rows(dbsession):
    owner = _create_user(dbsession, "delete-project-star-owner")
    watcher = _create_user(dbsession, "delete-project-star-watcher")

    project = _create_project(owner, "delete")
    dbsession.add(project)
    dbsession.flush()

    watcher.projects_stars.append(project)
    dbsession.flush()

    project_id = project.id

    request = _request_stub(dbsession, owner, SimpleNamespace(project=project))
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
            select(models.projects_stars.c.project_id).where(
                models.projects_stars.c.project_id == project_id
            )
        )
        .scalars()
        .all()
        == []
    )


def test_del_row_project_removes_stars_rows(dbsession):
    owner = _create_user(dbsession, "del-row-project-star-owner")
    watcher = _create_user(dbsession, "del-row-project-star-watcher")

    project = _create_project(owner, "del-row")
    dbsession.add(project)
    dbsession.flush()

    watcher.projects_stars.append(project)
    dbsession.flush()

    project_id = project.id

    request = _request_stub(dbsession, owner, SimpleNamespace(project=project))
    response = ProjectView(request).del_row()
    dbsession.flush()

    assert response == ""
    assert (
        dbsession.execute(
            select(models.Project).where(models.Project.id == project_id)
        ).scalar_one_or_none()
        is None
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
