from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from sqlalchemy.sql import func, select
from sqlalchemy.sql.expression import desc

from ..forms.select import REPORTS
from ..models import (
    Activity,
    Comment,
    Company,
    Project,
    Tag,
    User,
    companies_stars,
    companies_tags,
    projects_stars,
    projects_tags,
)
from ..utils.paginator import get_paginator


class ReportView:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="report_all", renderer="report_all.mako", permission="view")
    def all(self):
        _ = self.request.translate
        return {
            "heading": _("Report"),
            "reports": REPORTS,
            "counter": len(REPORTS),
        }

    @view_config(route_name="report_view", renderer="report_view.mako", permission="view")
    @view_config(
        route_name="report_more",
        renderer="report_more.mako",
        permission="view",
    )
    def view(self):
        rel = self.request.matchdict.get("rel", "companies-tags")
        page = int(self.request.params.get("page", 1))
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
                        func.count(Activity.company_id).label("companies-projects"),
                    )
                    .join(Activity)
                    .group_by(Company)
                    .order_by(desc("companies-projects"))
                )
            case "companies-stars":
                stmt = (
                    select(
                        Company.name,
                        func.count(companies_stars.c.company_id).label(
                            "companies-stars"
                        ),
                    )
                    .join(companies_stars)
                    .group_by(Company)
                    .order_by(desc("companies-stars"))
                )
            case "projects-stars":
                stmt = (
                    select(
                        Project.name,
                        func.count(projects_stars.c.project_id).label("projects-stars"),
                    )
                    .join(projects_stars)
                    .group_by(Project)
                    .order_by(desc("projects-stars"))
                )
            case "companies-announcement":
                stmt = (
                    select(
                        Company.name,
                        func.count(Activity.company).label("companies-announcement"),
                    )
                    .filter(Activity.stage == "announcement")
                    .join(Activity)
                    .group_by(Company)
                    .order_by(desc("companies-announcement"))
                )
            case "companies-tenders":
                stmt = (
                    select(
                        Company.name,
                        func.count(Activity.company).label("companies-tenders"),
                    )
                    .filter(Activity.stage == "tender")
                    .join(Activity)
                    .group_by(Company)
                    .order_by(desc("companies-tenders"))
                )
            case "companies-constructions":
                stmt = (
                    select(
                        Company.name,
                        func.count(Activity.company).label("companies-constructions"),
                    )
                    .filter(Activity.stage == "construction")
                    .join(Activity)
                    .group_by(Company)
                    .order_by(desc("companies-constructions"))
                )
            case "designers":
                stmt = (
                    select(
                        Company.name,
                        func.count(Activity.company).label("designers"),
                    )
                    .filter(Activity.role == "designer")
                    .join(Activity)
                    .group_by(Company)
                    .order_by(desc("designers"))
                )
            case "purchasers":
                stmt = (
                    select(
                        Company.name,
                        func.count(Activity.company).label("purchasers"),
                    )
                    .filter(Activity.role == "purchaser")
                    .join(Activity)
                    .group_by(Company)
                    .order_by(desc("purchasers"))
                )
            case "investors":
                stmt = (
                    select(
                        Company.name,
                        func.count(Activity.company).label("investors"),
                    )
                    .filter(Activity.role == "investor")
                    .join(Activity)
                    .group_by(Company)
                    .order_by(desc("investors"))
                )
            case "general-contractors":
                stmt = (
                    select(
                        Company.name,
                        func.count(Activity.company).label("general-contractors"),
                    )
                    .filter(Activity.role == "general_contractor")
                    .join(Activity)
                    .group_by(Company)
                    .order_by(desc("general-contractors"))
                )
            case "subcontractors":
                stmt = (
                    select(
                        Company.name,
                        func.count(Activity.company).label("subcontractors"),
                    )
                    .filter(Activity.role == "subcontractor")
                    .join(Activity)
                    .group_by(Company)
                    .order_by(desc("subcontractors"))
                )
            case "suppliers":
                stmt = (
                    select(
                        Company.name,
                        func.count(Activity.company).label("suppliers"),
                    )
                    .filter(Activity.role == "supplier")
                    .join(Activity)
                    .group_by(Company)
                    .order_by(desc("suppliers"))
                )
            case "projects-companies":
                stmt = (
                    select(
                        Project.name,
                        func.count(Activity.project).label("projects-companies"),
                    )
                    .join(Activity)
                    .group_by(Project)
                    .order_by(desc("projects-companies"))
                )
            case _:
                raise HTTPNotFound

        paginator = self.request.dbsession.execute(get_paginator(stmt, page=page)).all()
        next_page = self.request.route_url(
            "report_more",
            rel=rel,
            _query={"page": page + 1},
        )
        return {
            "rel": rel,
            "lead": reports[rel],
            "paginator": paginator,
            "next_page": next_page,
        }
