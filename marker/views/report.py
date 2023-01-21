from pyramid.httpexceptions import HTTPNotFound, HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy.sql import func, select
from sqlalchemy.sql.expression import desc

from ..forms import ReportForm
from ..forms.select import REPORTS, STATES
from ..models import (
    Comment,
    CompaniesProjects,
    Company,
    Project,
    Tag,
    User,
    companies_tags,
    projects_tags,
    recommended,
    watched,
)
from ..paginator import get_paginator


class ReportView:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="report", renderer="report_form.mako", permission="view")
    def view(self):
        form = ReportForm(self.request.POST)

        if self.request.method == "POST" and form.validate():
            report = form.report.data
            next_url = self.request.route_url("report_all", rel=report)
            return HTTPSeeOther(location=next_url)

        return {
            "url": self.request.route_url("report"),
            "heading": "Raport",
            "form": form,
            "counter": len(REPORTS),
        }

    @view_config(route_name="report_all", renderer="report.mako", permission="view")
    @view_config(
        route_name="report_more",
        renderer="report_more.mako",
        permission="view",
    )
    def all(self):
        rel = self.request.matchdict.get("rel", "companies-tags")
        page = int(self.request.params.get("page", 1))
        states = dict(STATES)
        reports = dict(REPORTS)

        match rel:
            case "companies-tags":
                stmt = (
                    select(
                        Tag.name,
                        func.count(companies_tags.c.company_id).label("companies-tags"),
                    )
                    .join(companies_tags)
                    .group_by(Tag)
                    .order_by(desc("companies-tags"))
                )
            case "projects-tags":
                stmt = (
                    select(
                        Tag.name,
                        func.count(projects_tags.c.project_id).label("projects-tags"),
                    )
                    .join(projects_tags)
                    .group_by(Tag)
                    .order_by(desc("projects-tags"))
                )
            case "companies-states":
                stmt = (
                    select(
                        Company.state,
                        func.count(Company.state).label("companies-states"),
                    )
                    .group_by(Company.state)
                    .order_by(desc("companies-states"))
                )
            case "companies-cities":
                stmt = (
                    select(
                        Company.city, func.count(Company.city).label("companies-cities")
                    )
                    .group_by(Company.city)
                    .order_by(desc("companies-cities"))
                )
            case "companies-comments":
                stmt = (
                    select(
                        Company.name,
                        func.count(Comment.company_id).label("companies-comments"),
                    )
                    .join(Comment)
                    .group_by(Company)
                    .order_by(desc("companies-comments"))
                )
            case "projects-states":
                stmt = (
                    select(
                        Project.state,
                        func.count(Project.state).label("projects-states"),
                    )
                    .group_by(Project.state)
                    .order_by(desc("projects-states"))
                )
            case "projects-cities":
                stmt = (
                    select(
                        Project.city, func.count(Project.city).label("projects-cities")
                    )
                    .group_by(Project.city)
                    .order_by(desc("projects-cities"))
                )
            case "projects-comments":
                stmt = (
                    select(
                        Project.name,
                        func.count(Comment.project_id).label("projects-comments"),
                    )
                    .join(Comment)
                    .group_by(Project)
                    .order_by(desc("projects-comments"))
                )
            case "users-companies":
                stmt = (
                    select(
                        User.name,
                        func.count(Company.creator_id).label("users-companies"),
                    )
                    .join(Company.created_by)
                    .group_by(User.name)
                    .order_by(desc("users-companies"))
                )
            case "users-projects":
                stmt = (
                    select(
                        User.name,
                        func.count(Project.creator_id).label("users-projects"),
                    )
                    .join(Project.created_by)
                    .group_by(User.name)
                    .order_by(desc("users-projects"))
                )
            case "companies-projects":
                stmt = (
                    select(
                        Company.name,
                        func.count(CompaniesProjects.company_id).label(
                            "companies-projects"
                        ),
                    )
                    .join(CompaniesProjects)
                    .group_by(Company)
                    .order_by(desc("companies-projects"))
                )
            case "recommended-companies":
                stmt = (
                    select(
                        Company.name,
                        func.count(recommended.c.company_id).label(
                            "recommended-companies"
                        ),
                    )
                    .join(recommended)
                    .group_by(Company)
                    .order_by(desc("recommended-companies"))
                )
            case "watched-projects":
                stmt = (
                    select(
                        Project.name,
                        func.count(watched.c.project_id).label("watched-projects"),
                    )
                    .join(watched)
                    .group_by(Project)
                    .order_by(desc("watched-projects"))
                )
            case _:
                raise HTTPNotFound

        paginator = self.request.dbsession.execute(get_paginator(stmt, page=page)).all()
        next_page = self.request.route_url(
            "report_more",
            rel=rel,
            states=states,
            _query={"page": page + 1},
        )
        return {
            "rel": rel,
            "lead": reports[rel],
            "states": states,
            "paginator": paginator,
            "next_page": next_page,
        }
