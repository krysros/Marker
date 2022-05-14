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


def branch_factory(request):
    branch_id = int(request.matchdict["branch_id"])
    branch = request.dbsession.execute(
        select(models.Branch).filter_by(id=branch_id)
    ).scalar_one_or_none()
    if not branch:
        raise HTTPNotFound
    return resources.BranchResource(branch)


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


def investment_factory(request):
    investment_id = int(request.matchdict["investment_id"])
    investment = request.dbsession.execute(
        select(models.Investment).filter_by(id=investment_id)
    ).scalar_one_or_none()
    if not investment:
        raise HTTPNotFound
    return resources.InvestmentResource(investment)


def user_factory(request):
    username = request.matchdict["username"]
    user = request.dbsession.execute(
        select(models.User).filter_by(username=username)
    ).scalar_one_or_none()
    if not user:
        raise HTTPNotFound
    return resources.UserResource(user)


def document_factory(request):
    document_id = int(request.matchdict["document_id"])
    document = request.dbsession.execute(
        select(models.Document).filter_by(id=document_id)
    ).scalar_one_or_none()
    if not document:
        raise HTTPNotFound
    return resources.DocumentResource(document)
