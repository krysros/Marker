from types import SimpleNamespace

import pytest
from pyramid.httpexceptions import HTTPNotFound

from marker.factories import (
    account_factory,
    comment_factory,
    company_factory,
    contact_factory,
    default_factory,
    project_factory,
    tag_factory,
    user_factory,
)
from marker.models import Comment, Company, Contact, Project, Tag, User
from marker.resources import (
    AccountResource,
    CommentResource,
    CompanyResource,
    ContactResource,
    DefaultResource,
    ProjectResource,
    TagResource,
    UserResource,
)


def test_default_factory():
    result = default_factory(None)
    assert isinstance(result, DefaultResource)


def test_account_factory_with_identity(dbsession):
    user = User(
        name="acct_user", fullname="A U", email="a@b.com", role="user", password="x"
    )
    dbsession.add(user)
    dbsession.flush()

    request = SimpleNamespace(identity=user)
    result = account_factory(request)
    assert isinstance(result, AccountResource)
    assert result.user is user


def test_account_factory_no_identity():
    request = SimpleNamespace(identity=None)
    with pytest.raises(HTTPNotFound):
        account_factory(request)


def test_tag_factory_found(dbsession):
    tag = Tag(name="TestTag")
    dbsession.add(tag)
    dbsession.flush()

    request = SimpleNamespace(matchdict={"tag_id": str(tag.id)}, dbsession=dbsession)
    result = tag_factory(request)
    assert isinstance(result, TagResource)
    assert result.tag is tag


def test_tag_factory_not_found(dbsession):
    request = SimpleNamespace(matchdict={"tag_id": "999999"}, dbsession=dbsession)
    with pytest.raises(HTTPNotFound):
        tag_factory(request)


def test_company_factory_found(dbsession):
    company = Company(
        name="FactCo",
        street=None,
        postcode=None,
        city=None,
        subdivision=None,
        country=None,
        website=None,
        color=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    dbsession.flush()

    request = SimpleNamespace(
        matchdict={"company_id": str(company.id)}, dbsession=dbsession
    )
    result = company_factory(request)
    assert isinstance(result, CompanyResource)
    assert result.company is company


def test_company_factory_not_found(dbsession):
    request = SimpleNamespace(matchdict={"company_id": "999999"}, dbsession=dbsession)
    with pytest.raises(HTTPNotFound):
        company_factory(request)


def test_contact_factory_found(dbsession):
    contact = Contact(name="John", role="dev", phone="123", email="j@j.com", color="")
    dbsession.add(contact)
    dbsession.flush()

    request = SimpleNamespace(
        matchdict={"contact_id": str(contact.id)}, dbsession=dbsession
    )
    result = contact_factory(request)
    assert isinstance(result, ContactResource)
    assert result.contact is contact


def test_contact_factory_not_found(dbsession):
    request = SimpleNamespace(matchdict={"contact_id": "999999"}, dbsession=dbsession)
    with pytest.raises(HTTPNotFound):
        contact_factory(request)


def test_comment_factory_found(dbsession):
    comment = Comment(comment="Hello")
    dbsession.add(comment)
    dbsession.flush()

    request = SimpleNamespace(
        matchdict={"comment_id": str(comment.id)}, dbsession=dbsession
    )
    result = comment_factory(request)
    assert isinstance(result, CommentResource)
    assert result.comment is comment


def test_comment_factory_not_found(dbsession):
    request = SimpleNamespace(matchdict={"comment_id": "999999"}, dbsession=dbsession)
    with pytest.raises(HTTPNotFound):
        comment_factory(request)


def test_project_factory_found(dbsession):
    project = Project(
        name="FactProj",
        street=None,
        postcode=None,
        city=None,
        subdivision=None,
        country=None,
        website=None,
        color=None,
        deadline=None,
        stage=None,
        delivery_method=None,
    )
    dbsession.add(project)
    dbsession.flush()

    request = SimpleNamespace(
        matchdict={"project_id": str(project.id)}, dbsession=dbsession
    )
    result = project_factory(request)
    assert isinstance(result, ProjectResource)
    assert result.project is project


def test_project_factory_not_found(dbsession):
    request = SimpleNamespace(matchdict={"project_id": "999999"}, dbsession=dbsession)
    with pytest.raises(HTTPNotFound):
        project_factory(request)


def test_user_factory_found(dbsession):
    user = User(
        name="fact_user", fullname="F U", email="f@u.com", role="user", password="x"
    )
    dbsession.add(user)
    dbsession.flush()

    request = SimpleNamespace(matchdict={"username": "fact_user"}, dbsession=dbsession)
    result = user_factory(request)
    assert isinstance(result, UserResource)
    assert result.user is user


def test_user_factory_not_found(dbsession):
    request = SimpleNamespace(
        matchdict={"username": "nonexistent"}, dbsession=dbsession
    )
    with pytest.raises(HTTPNotFound):
        user_factory(request)
