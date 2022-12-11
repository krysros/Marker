from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPSeeOther,
)

from sqlalchemy.sql.expression import desc
from sqlalchemy.sql import (
    func,
    select,
)

from ..models import (
    User,
    Tag,
    Company,
    Project,
)

from ..models.company import companies_tags
from ..models.project import companies_projects
from ..models.user import recommended, watched

from ..paginator import get_paginator
from ..forms.select import STATES, REPORTS
from ..forms import ReportForm


class ReportView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="report", renderer="report_form.mako", permission="view")
    def view(self):
        form = ReportForm(self.request.POST)

        if self.request.method == "POST" and form.validate():
            report = form.report.data
            next_url = self.request.route_url("report_results", rel=report)
            return HTTPSeeOther(location=next_url)

        return {
            "url": self.request.route_url("report"),
            "heading": "Raport",
            "form": form,
            "counter": len(REPORTS),
        }

    @view_config(route_name="report_results", renderer="report.mako", permission="view")
    @view_config(
        route_name="report_more",
        renderer="report_more.mako",
        permission="view",
    )
    def results(self):
        rel = self.request.matchdict.get("rel", "companies-tags")
        page = int(self.request.params.get("page", 1))
        states = dict(STATES)
        reports = dict(REPORTS)

        if rel == "companies-tags":
            stmt = (
                select(
                    Tag.name,
                    func.count(companies_tags.c.company_id).label("companies-tags"),
                )
                .join(companies_tags)
                .group_by(Tag)
                .order_by(desc("companies-tags"))
            )
        elif rel == "companies-states":
            stmt = (
                select(
                    Company.state,
                    func.count(Company.state).label("companies-states"),
                )
                .group_by(Company.state)
                .order_by(desc("companies-states"))
            )
        elif rel == "companies-cities":
            stmt = (
                select(Company.city, func.count(Company.city).label("companies-cities"))
                .group_by(Company.city)
                .order_by(desc("companies-cities"))
            )
        elif rel == "projects-states":
            stmt = (
                select(
                    Project.state,
                    func.count(Project.state).label("projects-states"),
                )
                .group_by(Project.state)
                .order_by(desc("projects-states"))
            )
        elif rel == "projects-cities":
            stmt = (
                select(Project.city, func.count(Project.city).label("projects-cities"))
                .group_by(Project.city)
                .order_by(desc("projects-cities"))
            )
        elif rel == "users-companies":
            stmt = (
                select(
                    User.name, func.count(Company.creator_id).label("users-companies")
                )
                .join(Company.created_by)
                .group_by(User.name)
                .order_by(desc("users-companies"))
            )
        elif rel == "users-projects":
            stmt = (
                select(
                    User.name,
                    func.count(Project.creator_id).label("users-projects"),
                )
                .join(Project.created_by)
                .group_by(User.name)
                .order_by(desc("users-projects"))
            )
        elif rel == "companies-projects":
            stmt = (
                select(
                    Company.name,
                    func.count(companies_projects.c.company_id).label(
                        "companies-projects"
                    ),
                )
                .join(companies_projects)
                .group_by(Company)
                .order_by(desc("companies-projects"))
            )
        elif rel == "recommended-companies":
            stmt = (
                select(
                    Company.name,
                    func.count(recommended.c.company_id).label("recommended-companies"),
                )
                .join(recommended)
                .group_by(Company)
                .order_by(desc("recommended-companies"))
            )
        elif rel == "watched-projects":
            stmt = (
                select(
                    Project.name,
                    func.count(watched.c.project_id).label("watched-projects"),
                )
                .join(watched)
                .group_by(Project)
                .order_by(desc("watched-projects"))
            )
        else:
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
