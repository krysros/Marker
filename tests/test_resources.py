from types import SimpleNamespace

from pyramid.authorization import ALL_PERMISSIONS, Allow, Authenticated

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


def test_default_resource_acl():
    r = DefaultResource()
    acl = r.__acl__()
    assert (Allow, Authenticated, "view") in acl
    assert (Allow, "role:editor", ("add", "edit")) in acl
    assert (Allow, "role:admin", ALL_PERMISSIONS) in acl


def test_account_resource_acl():
    user = SimpleNamespace(id=7)
    r = AccountResource(user)
    assert r.user is user
    acl = r.__acl__()
    assert (Allow, "u:7", "view") in acl
    assert (Allow, "u:7", "edit") in acl
    assert (Allow, "role:admin", ALL_PERMISSIONS) in acl


def test_user_resource_acl():
    user = SimpleNamespace(id=99)
    r = UserResource(user)
    assert r.user is user
    acl = r.__acl__()
    assert (Allow, "u:99", "view") in acl
    assert (Allow, "u:99", "edit") in acl
    assert (Allow, "role:admin", ALL_PERMISSIONS) in acl


def test_tag_resource():
    tag = SimpleNamespace(id=1)
    r = TagResource(tag)
    assert r.tag is tag
    # inherits DefaultResource acl
    acl = r.__acl__()
    assert (Allow, Authenticated, "view") in acl


def test_company_resource():
    company = SimpleNamespace(id=2)
    r = CompanyResource(company)
    assert r.company is company


def test_contact_resource():
    contact = SimpleNamespace(id=3)
    r = ContactResource(contact)
    assert r.contact is contact


def test_comment_resource():
    comment = SimpleNamespace(id=4)
    r = CommentResource(comment)
    assert r.comment is comment


def test_project_resource():
    project = SimpleNamespace(id=5)
    r = ProjectResource(project)
    assert r.project is project
