from pyramid.httpexceptions import HTTPNotFound, HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy.sql import func, select
from sqlalchemy.sql.expression import desc

from ..forms import ReportForm
from ..forms.select import REPORTS, SUBDIVISIONS
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
        _ = self.request.translate
        form = ReportForm(self.request.POST)

        if self.request.method == "POST" and form.validate():
            report = form.report.data
            next_url = self.request.route_url("report_all", rel=report)
            return HTTPSeeOther(location=next_url)

        return {
            "url": self.request.route_url("report"),
            "heading": _("Report"),
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
        subdivisions = dict(SUBDIVISIONS)
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
            case "companies-subdivisions":
                stmt = (
                    select(
                        Company.subdivision,
                        func.count(Company.subdivision).label("companies-subdivisions"),
                    )
                    .group_by(Company.subdivision)
                    .order_by(desc("companies-subdivisions"))
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
            case "projects-subdivisions":
                stmt = (
                    select(
                        Project.subdivision,
                        func.count(Project.subdivision).label("projects-subdivisions"),
                    )
                    .group_by(Project.subdivision)
                    .order_by(desc("projects-subdivisions"))
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
            case "companies-announcement":
                stmt = (
                    select(
                        Company.name,
                        func.count(CompaniesProjects.company).label(
                            "companies-announcement"
                        ),
                    )
                    .filter(CompaniesProjects.stage == "announcement")
                    .join(CompaniesProjects)
                    .group_by(Company)
                    .order_by(desc("companies-announcement"))
                )
            case "companies-tenders":
                stmt = (
                    select(
                        Company.name,
                        func.count(CompaniesProjects.company).label(
                            "companies-tenders"
                        ),
                    )
                    .filter(CompaniesProjects.stage == "tender")
                    .join(CompaniesProjects)
                    .group_by(Company)
                    .order_by(desc("companies-tenders"))
                )
            case "companies-constructions":
                stmt = (
                    select(
                        Company.name,
                        func.count(CompaniesProjects.company).label(
                            "companies-constructions"
                        ),
                    )
                    .filter(CompaniesProjects.stage == "construction")
                    .join(CompaniesProjects)
                    .group_by(Company)
                    .order_by(desc("companies-constructions"))
                )
            case "designers":
                stmt = (
                    select(
                        Company.name,
                        func.count(CompaniesProjects.company).label("designers"),
                    )
                    .filter(CompaniesProjects.role == "designer")
                    .join(CompaniesProjects)
                    .group_by(Company)
                    .order_by(desc("designers"))
                )
            case "purchasers":
                stmt = (
                    select(
                        Company.name,
                        func.count(CompaniesProjects.company).label("purchasers"),
                    )
                    .filter(CompaniesProjects.role == "purchaser")
                    .join(CompaniesProjects)
                    .group_by(Company)
                    .order_by(desc("purchasers"))
                )
            case "investors":
                stmt = (
                    select(
                        Company.name,
                        func.count(CompaniesProjects.company).label("investors"),
                    )
                    .filter(CompaniesProjects.role == "investor")
                    .join(CompaniesProjects)
                    .group_by(Company)
                    .order_by(desc("investors"))
                )
            case "general-contractors":
                stmt = (
                    select(
                        Company.name,
                        func.count(CompaniesProjects.company).label(
                            "general-contractors"
                        ),
                    )
                    .filter(CompaniesProjects.role == "general_contractor")
                    .join(CompaniesProjects)
                    .group_by(Company)
                    .order_by(desc("general-contractors"))
                )
            case "subcontractors":
                stmt = (
                    select(
                        Company.name,
                        func.count(CompaniesProjects.company).label("subcontractors"),
                    )
                    .filter(CompaniesProjects.role == "subcontractor")
                    .join(CompaniesProjects)
                    .group_by(Company)
                    .order_by(desc("subcontractors"))
                )
            case "suppliers":
                stmt = (
                    select(
                        Company.name,
                        func.count(CompaniesProjects.company).label("suppliers"),
                    )
                    .filter(CompaniesProjects.role == "supplier")
                    .join(CompaniesProjects)
                    .group_by(Company)
                    .order_by(desc("suppliers"))
                )
            case "projects-companies":
                stmt = (
                    select(
                        Project.name,
                        func.count(CompaniesProjects.project).label(
                            "projects-companies"
                        ),
                    )
                    .join(CompaniesProjects)
                    .group_by(Project)
                    .order_by(desc("projects-companies"))
                )
            case _:
                raise HTTPNotFound

        paginator = self.request.dbsession.execute(get_paginator(stmt, page=page)).all()
        next_page = self.request.route_url(
            "report_more",
            rel=rel,
            subdivisions=subdivisions,
            _query={"page": page + 1},
        )
        return {
            "rel": rel,
            "lead": reports[rel],
            "subdivisions": subdivisions,
            "paginator": paginator,
            "next_page": next_page,
        }
