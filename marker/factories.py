from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import select

import marker.models as models
import marker.resources as resources


def default_factory(request):
    return resources.DefaultResource()


def account_factory(request):
    user = request.identity
    if not user:
        raise HTTPNotFound
    return resources.AccountResource(user)


def tag_factory(request):
    tag_id = int(request.matchdict["tag_id"])
    tag = request.dbsession.execute(
        select(models.Tag).filter_by(id=tag_id)
    ).scalar_one_or_none()
    if not tag:
        raise HTTPNotFound
    return resources.TagResource(tag)


def company_factory(request):
    company_id = int(request.matchdict["company_id"])
    company = request.dbsession.execute(
        select(models.Company).filter_by(id=company_id)
    ).scalar_one_or_none()
    if not company:
        raise HTTPNotFound
    return resources.CompanyResource(company)


def person_factory(request):
    person_id = int(request.matchdict["person_id"])
    person = request.dbsession.execute(
        select(models.Person).filter_by(id=person_id)
    ).scalar_one_or_none()
    if not person:
        raise HTTPNotFound
    return resources.PersonResource(person)


def comment_factory(request):
    comment_id = int(request.matchdict["comment_id"])
    comment = request.dbsession.execute(
        select(models.Comment).filter_by(id=comment_id)
    ).scalar_one_or_none()
    if not comment:
        raise HTTPNotFound
    return resources.CommentResource(comment)


def project_factory(request):
    project_id = int(request.matchdict["project_id"])
    project = request.dbsession.execute(
        select(models.Project).filter_by(id=project_id)
    ).scalar_one_or_none()
    if not project:
        raise HTTPNotFound
    return resources.ProjectResource(project)


def user_factory(request):
    username = request.matchdict["username"]
    user = request.dbsession.execute(
        select(models.User).filter_by(name=username)
    ).scalar_one_or_none()
    if not user:
        raise HTTPNotFound
    return resources.UserResource(user)
