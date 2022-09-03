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
from ..models.user import recomended, watched

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

        return dict(
            url=self.request.route_url("report"),
            heading="Raport",
            form=form,
        )

    @view_config(route_name="report_results", renderer="report.mako", permission="view")
    @view_config(
        route_name="report_more",
        renderer="report_more.mako",
        permission="view",
    )
    def results(self):
        rel = self.request.matchdict.get("rel", "cb")
        page = int(self.request.params.get("page", 1))
        states = dict(STATES)
        reports = dict(REPORTS)

        if rel == "cb":
            stmt = (
                select(
                    Tag.name,
                    func.count(companies_tags.c.company_id).label("cb"),
                )
                .join(companies_tags)
                .group_by(Tag)
                .order_by(desc("cb"))
            )
        elif rel == "cv":
            stmt = (
                select(
                    Company.state,
                    func.count(Company.state).label("cv"),
                )
                .group_by(Company.state)
                .order_by(desc("cv"))
            )
        elif rel == "cc":
            stmt = (
                select(Company.city, func.count(Company.city).label("cc"))
                .group_by(Company.city)
                .order_by(desc("cc"))
            )
        elif rel == "tv":
            stmt = (
                select(
                    Project.state,
                    func.count(Project.state).label("tv"),
                )
                .group_by(Project.state)
                .order_by(desc("tv"))
            )
        elif rel == "tc":
            stmt = (
                select(Project.city, func.count(Project.city).label("tc"))
                .group_by(Project.city)
                .order_by(desc("tc"))
            )
        elif rel == "uc":
            stmt = (
                select(User.name, func.count(Company.creator_id).label("uc"))
                .join(Company.created_by)
                .group_by(User.name)
                .order_by(desc("uc"))
            )
        elif rel == "ut":
            stmt = (
                select(
                    User.name,
                    func.count(Project.creator_id).label("ut"),
                )
                .join(Project.created_by)
                .group_by(User.name)
                .order_by(desc("ut"))
            )
        elif rel == "ct":
            stmt = (
                select(
                    Company.name,
                    func.count(companies_projects.c.company_id).label("ct"),
                )
                .join(companies_projects)
                .group_by(Company)
                .order_by(desc("ct"))
            )
        elif rel == "cu":
            stmt = (
                select(Company.name, func.count(recomended.c.company_id).label("cu"))
                .join(recomended)
                .group_by(Company)
                .order_by(desc("cu"))
            )
        elif rel == "tf":
            stmt = (
                select(
                    Project.name,
                    func.count(watched.c.project_id).label("tf"),
                )
                .join(watched)
                .group_by(Project)
                .order_by(desc("tf"))
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

        return dict(
            rel=rel,
            lead=reports[rel],
            states=states,
            paginator=paginator,
            next_page=next_page,
        )
