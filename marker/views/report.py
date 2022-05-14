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
import deform
from deform.schema import CSRFSchema
import colander

from ..models import (
    User,
    Branch,
    Company,
    Investment,
)

from ..models.company import companies_branches
from ..models.investment import companies_investments
from ..models.user import upvotes, following

from ..paginator import get_paginator
from .select import VOIVODESHIPS, REPORTS


class ReportView(object):
    def __init__(self, request):
        self.request = request

    @property
    def report_form(self):
        class Schema(CSRFSchema):
            rel = colander.SchemaNode(
                colander.String(),
                title="Relacja",
                widget=deform.widget.SelectWidget(values=REPORTS),
            )

        schema = Schema().bind(request=self.request)
        submit_btn = deform.form.Button(name="submit", title="Pokaż")
        form = deform.Form(schema, buttons=(submit_btn,))
        return form

    @view_config(route_name="report", renderer="form.mako", permission="view")
    def view(self):
        form = self.report_form
        appstruct = {}
        rendered_form = None

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                rendered_form = e.render()
            else:
                next_url = self.request.route_url(
                    "report_results", rel=appstruct["rel"]
                )
                return HTTPSeeOther(location=next_url)

        if rendered_form is None:
            rendered_form = form.render(appstruct=appstruct)

        return dict(
            heading="Wybór raportu",
            rendered_form=rendered_form,
        )

    @view_config(
        route_name="report_results", renderer="report.mako", permission="view"
    )
    @view_config(
        route_name="report_more",
        renderer="report_more.mako",
        permission="view",
    )
    def results(self):
        rel = self.request.matchdict.get("rel", "cb")
        page = int(self.request.params.get("page", 1))
        voivodeships = dict(VOIVODESHIPS)
        reports = dict(REPORTS)

        if rel == "cb":
            stmt = (
                select(
                    Branch.name,
                    func.count(companies_branches.c.company_id).label("cb"),
                )
                .join(companies_branches)
                .group_by(Branch)
                .order_by(desc("cb"))
            )
        elif rel == "cv":
            stmt = (
                select(
                    Company.voivodeship,
                    func.count(Company.voivodeship).label("cv"),
                )
                .group_by(Company.voivodeship)
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
                    Investment.voivodeship,
                    func.count(Investment.voivodeship).label("tv"),
                )
                .group_by(Investment.voivodeship)
                .order_by(desc("tv"))
            )
        elif rel == "tc":
            stmt = (
                select(
                    Investment.city, func.count(Investment.city).label("tc")
                )
                .group_by(Investment.city)
                .order_by(desc("tc"))
            )
        elif rel == "uc":
            stmt = (
                select(
                    User.username, func.count(Company.creator_id).label("uc")
                )
                .join(Company.created_by)
                .group_by(User.username)
                .order_by(desc("uc"))
            )
        elif rel == "ut":
            stmt = (
                select(
                    User.username,
                    func.count(Investment.creator_id).label("ut"),
                )
                .join(Investment.created_by)
                .group_by(User.username)
                .order_by(desc("ut"))
            )
        elif rel == "ct":
            stmt = (
                select(
                    Company.name,
                    func.count(companies_investments.c.company_id).label("ct"),
                )
                .join(companies_investments)
                .group_by(Company)
                .order_by(desc("ct"))
            )
        elif rel == "cu":
            stmt = (
                select(
                    Company.name, func.count(upvotes.c.company_id).label("cu")
                )
                .join(upvotes)
                .group_by(Company)
                .order_by(desc("cu"))
            )
        elif rel == "tf":
            stmt = (
                select(
                    Investment.name,
                    func.count(following.c.investment_id).label("tf"),
                )
                .join(following)
                .group_by(Investment)
                .order_by(desc("tf"))
            )
        else:
            raise HTTPNotFound

        paginator = self.request.dbsession.execute(
            get_paginator(stmt, page=page)
        ).all()
        next_page = self.request.route_url(
            "report_more",
            rel=rel,
            _query={"voivodeships": voivodeships, "page": page + 1},
        )

        return dict(
            rel=rel,
            lead=reports[rel],
            voivodeships=voivodeships,
            paginator=paginator,
            next_page=next_page,
        )
