import datetime
from types import SimpleNamespace

from sqlalchemy import delete, select

from marker import models
from marker.views.tag import TagView
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


def _create_user(dbsession, name):
    user = models.user.User(
        name=name,
        password="admin",
        fullname="Tag Delete Admin",
        email=f"{name}@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()
    return user


def _create_company(user, suffix):
    company = models.company.Company(
        name=f"Tag Company {suffix}",
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
        name=f"Tag Project {suffix}",
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


def _assert_tag_association_rows_removed(dbsession, tag_ids):
    assert (
        dbsession.execute(
            select(models.selected_tags.c.tag_id).where(
                models.selected_tags.c.tag_id.in_(tag_ids)
            )
        )
        .scalars()
        .all()
        == []
    )
    assert (
        dbsession.execute(
            select(models.companies_tags.c.tag_id).where(
                models.companies_tags.c.tag_id.in_(tag_ids)
            )
        )
        .scalars()
        .all()
        == []
    )
    assert (
        dbsession.execute(
            select(models.projects_tags.c.tag_id).where(
                models.projects_tags.c.tag_id.in_(tag_ids)
            )
        )
        .scalars()
        .all()
        == []
    )


def test_delete_tag_removes_association_rows(dbsession):
    owner = _create_user(dbsession, "single-tag-owner")
    selector = _create_user(dbsession, "single-tag-selector")

    company = _create_company(owner, "single")
    project = _create_project(owner, "single")
    tag = models.tag.Tag("Single Tag")
    tag.created_by = owner
    tag.companies.append(company)
    tag.projects.append(project)
    selector.selected_tags.append(tag)

    dbsession.add(company)
    dbsession.add(project)
    dbsession.add(tag)
    dbsession.flush()

    tag_id = tag.id
    request = _request_stub(dbsession, owner, SimpleNamespace(tag=tag))
    response = TagView(request).delete()
    dbsession.flush()

    assert response.status_code == 303
    assert (
        dbsession.execute(
            select(models.Tag).where(models.Tag.id == tag_id)
        ).scalar_one_or_none()
        is None
    )
    _assert_tag_association_rows_removed(dbsession, [tag_id])


def test_delete_selected_tags_removes_association_rows(dbsession):
    owner = _create_user(dbsession, "bulk-tag-owner")

    company = _create_company(owner, "bulk")
    project = _create_project(owner, "bulk")

    tag_1 = models.tag.Tag("Bulk Tag 1")
    tag_1.created_by = owner
    tag_1.companies.append(company)

    tag_2 = models.tag.Tag("Bulk Tag 2")
    tag_2.created_by = owner
    tag_2.projects.append(project)

    owner.selected_tags.append(tag_1)
    owner.selected_tags.append(tag_2)

    dbsession.add(company)
    dbsession.add(project)
    dbsession.add(tag_1)
    dbsession.add(tag_2)
    dbsession.flush()

    tag_ids = [tag_1.id, tag_2.id]

    request = _request_stub(dbsession, owner, SimpleNamespace(user=owner))
    response = UserView(request).delete_selected_tags()
    dbsession.flush()

    assert response.status_code == 303
    assert (
        dbsession.execute(select(models.Tag).where(models.Tag.id.in_(tag_ids)))
        .scalars()
        .all()
        == []
    )
    _assert_tag_association_rows_removed(dbsession, tag_ids)


def test_raw_tag_delete_cascades_association_rows(dbsession):
    owner = _create_user(dbsession, "raw-tag-owner")
    selector = _create_user(dbsession, "raw-tag-selector")

    company = _create_company(owner, "raw")
    project = _create_project(owner, "raw")
    tag = models.tag.Tag("Raw Tag")
    tag.created_by = owner
    tag.companies.append(company)
    tag.projects.append(project)
    selector.selected_tags.append(tag)

    dbsession.add(company)
    dbsession.add(project)
    dbsession.add(tag)
    dbsession.flush()

    tag_id = tag.id

    dbsession.execute(delete(models.Tag).where(models.Tag.id == tag_id))
    dbsession.flush()

    assert (
        dbsession.execute(
            select(models.Tag).where(models.Tag.id == tag_id)
        ).scalar_one_or_none()
        is None
    )
    _assert_tag_association_rows_removed(dbsession, [tag_id])
