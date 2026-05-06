import datetime
import logging

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import func, select

from ..forms import (
    CompanyFilterForm,
    CompanyLinkForm,
    ProjectFilterForm,
    ProjectLinkForm,
    TagFilterForm,
    TagForm,
    TagSearchForm,
)
from ..forms.select import (
    CATEGORIES,
    COLORS,
    COMPANY_ROLES,
    ORDER_CRITERIA,
    SORT_CRITERIA,
    SORT_CRITERIA_COMPANIES,
    SORT_CRITERIA_PROJECTS,
)
from ..models import (
    Activity,
    Company,
    Project,
    Tag,
    companies_stars,
    companies_tags,
    projects_stars,
    projects_tags,
    selected_companies,
    selected_projects,
    selected_tags,
)
from ..utils.export import make_export_response
from ..utils.paginator import get_paginator
from . import (
    Filter,
    apply_order,
    clear_selected_rows,
    contains_ci,
    handle_bulk_selection,
    is_bulk_select_request,
    selected_ids_for_items,
    sort_column,
    toggle_selected_item,
)

log = logging.getLogger(__name__)


class TagView:
    def __init__(self, request):
        self.request = request
        self.count_companies = 0
        self.count_projects = 0

    def pills(self, tag):
        _ = self.request.translate
        return [
            {
                "title": _("Tag"),
                "icon": "tag",
                "url": self.request.route_url("tag_view", tag_id=tag.id, slug=tag.slug),
                "count": None,
            },
            {
                "title": _("Companies"),
                "icon": "buildings",
                "url": self.request.route_url(
                    "tag_companies", tag_id=tag.id, slug=tag.slug
                ),
                "count": self.request.route_url(
                    "tag_count_companies", tag_id=tag.id, slug=tag.slug
                ),
                "event": "tagEvent",
                "init_value": self.count_companies,
            },
            {
                "title": _("Projects"),
                "icon": "briefcase",
                "url": self.request.route_url(
                    "tag_projects", tag_id=tag.id, slug=tag.slug
                ),
                "count": self.request.route_url(
                    "tag_count_projects", tag_id=tag.id, slug=tag.slug
                ),
                "event": "tagEvent",
                "init_value": self.count_projects,
            },
        ]

    @view_config(route_name="tag_all", renderer="tag_all.mako", permission="view")
    @view_config(
        route_name="tag_more",
        renderer="tag_table#rows.mako",
        permission="view",
    )
    def all(self):
        page = int(self.request.params.get("page", 1))
        name = self.request.params.get("name", None)
        category = self.request.params.get("category", "")
        date_from = self.request.params.get("date_from", None)
        date_to = self.request.params.get("date_to", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA)
        sort_criteria["name"] = self.request.translate("Tag")
        order_criteria = dict(ORDER_CRITERIA)
        categories = dict(CATEGORIES)
        q = {}

        stmt = select(Tag)

        if name:
            stmt = stmt.filter(contains_ci(Tag.name, name))
            q["name"] = name

        if category == "companies":
            company_link_exists = (
                select(companies_tags.c.tag_id)
                .where(companies_tags.c.tag_id == Tag.id)
                .exists()
            )
            stmt = stmt.where(company_link_exists)
            q["category"] = category
        elif category == "projects":
            project_link_exists = (
                select(projects_tags.c.tag_id)
                .where(projects_tags.c.tag_id == Tag.id)
                .exists()
            )
            stmt = stmt.where(project_link_exists)
            q["category"] = category

        if date_from:
            date_from_dt = datetime.datetime.strptime(date_from, "%Y-%m-%dT%H:%M")
            stmt = stmt.filter(Tag.created_at >= date_from_dt)
            q["date_from"] = date_from

        if date_to:
            date_to_dt = datetime.datetime.strptime(date_to, "%Y-%m-%dT%H:%M")
            stmt = stmt.filter(Tag.created_at <= date_to_dt)
            q["date_to"] = date_to

        q["sort"] = _sort
        q["order"] = _order

        stmt = apply_order(stmt, sort_column(Tag, _sort), _order)

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_tags
            )

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "tag_more",
            _query={
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = TagFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "categories": categories,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "form": form,
        }

    @view_config(
        route_name="tag_count",
        renderer="json",
        permission="view",
    )
    def count(self):
        return self.request.dbsession.execute(
            select(func.count()).select_from(select(Tag).subquery())
        ).scalar()

    @view_config(
        route_name="tag_view",
        renderer="tag_view.mako",
        permission="view",
    )
    def view(self):
        tag = self.request.context.tag
        is_tag_selected = (
            self.request.dbsession.execute(
                select(1)
                .select_from(selected_tags)
                .where(
                    selected_tags.c.user_id == self.request.identity.id,
                    selected_tags.c.tag_id == tag.id,
                )
                .limit(1)
            ).first()
            is not None
        )
        self.count_companies = tag.count_companies
        self.count_projects = tag.count_projects
        return {
            "tag": tag,
            "is_tag_selected": is_tag_selected,
            "title": tag.name,
            "tag_pills": self.pills(tag),
        }

    @view_config(
        route_name="tag_map_companies",
        renderer="tag_map_companies.mako",
        permission="view",
    )
    def map_companies(self):
        tag = self.request.context.tag
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = [
            value for value in self.request.params.getall("subdivision") if value
        ]
        q = {}

        stmt = select(Company).filter(Company.tags.any(name=tag.name))

        if color:
            stmt = stmt.filter(Company.color == color)
            q["color"] = color

        if country:
            stmt = stmt.filter(Company.country == country)
            q["country"] = country

        if subdivision:
            stmt = stmt.filter(Company.subdivision.in_(subdivision))
            q["subdivision"] = list(subdivision)

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        ).scalar()

        self.count_companies = counter
        self.count_projects = tag.count_projects

        url = self.request.route_url(
            "tag_json_companies", tag_id=tag.id, slug=tag.slug, _query=q
        )
        return {"tag": tag, "url": url, "q": q, "tag_pills": self.pills(tag)}

    @view_config(
        route_name="tag_map_projects",
        renderer="tag_map_projects.mako",
        permission="view",
    )
    def map_projects(self):
        tag = self.request.context.tag
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = [
            value for value in self.request.params.getall("subdivision") if value
        ]
        now = datetime.datetime.now()
        q = {}

        stmt = select(Project).filter(Project.tags.any(name=tag.name))

        if status == "in_progress":
            stmt = stmt.filter(Project.deadline > now)
            q["status"] = status
        elif status == "completed":
            stmt = stmt.filter(Project.deadline < now)
            q["status"] = status

        if color:
            stmt = stmt.filter(Project.color == color)
            q["color"] = color

        if country:
            stmt = stmt.filter(Project.country == country)
            q["country"] = country

        if subdivision:
            stmt = stmt.filter(Project.subdivision.in_(subdivision))
            q["subdivision"] = list(subdivision)

        if stage:
            stmt = stmt.filter(Project.stage == stage)
            q["stage"] = stage

        if delivery_method:
            stmt = stmt.filter(Project.delivery_method == delivery_method)
            q["delivery_method"] = delivery_method

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        ).scalar()

        self.count_companies = tag.count_companies
        self.count_projects = counter

        url = self.request.route_url(
            "tag_json_projects", tag_id=tag.id, slug=tag.slug, _query=q
        )
        return {"tag": tag, "url": url, "q": q, "tag_pills": self.pills(tag)}

    @view_config(
        route_name="tag_json_companies",
        renderer="json",
        permission="view",
    )
    def json_companies(self):
        tag = self.request.context.tag
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = [
            value for value in self.request.params.getall("subdivision") if value
        ]

        # Bounding box parameters for lazy loading
        north = self.request.params.get("north", None)
        south = self.request.params.get("south", None)
        east = self.request.params.get("east", None)
        west = self.request.params.get("west", None)

        stmt = select(Company).filter(Company.tags.any(name=tag.name))

        if color:
            stmt = stmt.filter(Company.color == color)

        if country:
            stmt = stmt.filter(Company.country == country)

        if subdivision:
            stmt = stmt.filter(Company.subdivision.in_(subdivision))

        # Filter by bounding box if provided
        if north and south and east and west:
            try:
                north = float(north)
                south = float(south)
                east = float(east)
                west = float(west)
                stmt = stmt.filter(Company.latitude.between(south, north))
                stmt = stmt.filter(Company.longitude.between(west, east))
            except (ValueError, TypeError):
                pass  # Invalid coordinates, ignore filtering

        companies = self.request.dbsession.execute(stmt).scalars().all()
        selected_company_ids = selected_ids_for_items(
            self.request,
            selected_companies,
            selected_companies.c.company_id,
            [company.id for company in companies],
        )
        res = [
            {
                "id": company.id,
                "name": company.name,
                "street": company.street,
                "city": company.city,
                "country": company.country,
                "latitude": company.latitude,
                "longitude": company.longitude,
                "color": company.color,
                "url": self.request.route_url(
                    "company_view", company_id=company.id, slug=company.slug
                ),
                "check_url": self.request.route_url(
                    "company_check", company_id=company.id, slug=company.slug
                ),
                "checked": company.id in selected_company_ids,
            }
            for company in companies
        ]
        return res

    @view_config(
        route_name="tag_json_projects",
        renderer="json",
        permission="view",
    )
    def json_projects(self):
        tag = self.request.context.tag
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = [
            value for value in self.request.params.getall("subdivision") if value
        ]
        now = datetime.datetime.now()

        # Bounding box parameters for lazy loading
        north = self.request.params.get("north", None)
        south = self.request.params.get("south", None)
        east = self.request.params.get("east", None)
        west = self.request.params.get("west", None)

        stmt = select(Project).filter(Project.tags.any(name=tag.name))

        if status == "in_progress":
            stmt = stmt.filter(Project.deadline > now)

        elif status == "completed":
            stmt = stmt.filter(Project.deadline < now)

        if color:
            stmt = stmt.filter(Project.color == color)

        if country:
            stmt = stmt.filter(Project.country == country)

        if subdivision:
            stmt = stmt.filter(Project.subdivision.in_(subdivision))

        if stage:
            stmt = stmt.filter(Project.stage == stage)

        if delivery_method:
            stmt = stmt.filter(Project.delivery_method == delivery_method)

        # Filter by bounding box if provided
        if north and south and east and west:
            try:
                north = float(north)
                south = float(south)
                east = float(east)
                west = float(west)
                stmt = stmt.filter(Project.latitude.between(south, north))
                stmt = stmt.filter(Project.longitude.between(west, east))
            except (ValueError, TypeError):
                pass  # Invalid coordinates, ignore filtering

        projects = self.request.dbsession.execute(stmt).scalars().all()
        selected_project_ids = selected_ids_for_items(
            self.request,
            selected_projects,
            selected_projects.c.project_id,
            [project.id for project in projects],
        )
        res = [
            {
                "id": project.id,
                "name": project.name,
                "street": project.street,
                "city": project.city,
                "country": project.country,
                "latitude": project.latitude,
                "longitude": project.longitude,
                "color": project.color,
                "url": self.request.route_url(
                    "project_view", project_id=project.id, slug=project.slug
                ),
                "check_url": self.request.route_url(
                    "project_check", project_id=project.id, slug=project.slug
                ),
                "checked": project.id in selected_project_ids,
            }
            for project in projects
        ]
        return res

    @view_config(
        route_name="tag_companies",
        renderer="tag_companies.mako",
        permission="view",
    )
    @view_config(
        route_name="tag_more_companies",
        renderer="company_table#rows.mako",
        permission="view",
    )
    def companies(self):
        tag = self.request.context.tag
        page = int(self.request.params.get("page", 1))
        role = self.request.params.get("role", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = [
            value for value in self.request.params.getall("subdivision") if value
        ]
        date_from = self.request.params.get("date_from", None)
        date_to = self.request.params.get("date_to", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        colors = dict(COLORS)
        sort_criteria = dict(SORT_CRITERIA_COMPANIES)
        order_criteria = dict(ORDER_CRITERIA)
        role_choices = {k: v for k, v in COMPANY_ROLES if k}
        q = {}

        stmt = select(Company)

        if role:
            q["role"] = role

        if color:
            stmt = stmt.filter(Company.color == color)
            q["color"] = color

        if country:
            stmt = stmt.filter(Company.country == country)
            q["country"] = country

        if subdivision:
            stmt = stmt.filter(Company.subdivision.in_(subdivision))
            q["subdivision"] = list(subdivision)

        if date_from:
            date_from_dt = datetime.datetime.strptime(date_from, "%Y-%m-%dT%H:%M")
            stmt = stmt.filter(Company.created_at >= date_from_dt)
            q["date_from"] = date_from

        if date_to:
            date_to_dt = datetime.datetime.strptime(date_to, "%Y-%m-%dT%H:%M")
            stmt = stmt.filter(Company.created_at <= date_to_dt)
            q["date_to"] = date_to

        if _sort == "stars":
            count_col = func.count(companies_stars.c.company_id)
            stmt = (
                stmt.filter(Company.tags.any(name=tag.name))
                .join(companies_stars)
                .group_by(Company.id)
                .order_by(
                    count_col.asc() if _order == "asc" else count_col.desc(), Company.id
                )
            )
        elif _sort == "comments":
            count_col = func.count(Company.comments)
            stmt = (
                stmt.filter(Company.tags.any(name=tag.name))
                .join(Company.comments)
                .group_by(Company.id)
                .order_by(count_col.asc() if _order == "asc" else count_col.desc())
            )
        else:
            col = sort_column(Company, _sort)
            stmt = stmt.filter(Company.tags.any(name=tag.name)).order_by(
                col.asc() if _order == "asc" else col.desc(), Company.id
            )

        q["sort"] = _sort
        q["order"] = _order

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_companies
            )

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        ).scalar()

        self.count_companies = counter
        self.count_projects = tag.count_projects

        obj = Filter(**q)
        form = CompanyFilterForm(self.request.GET, obj, request=self.request)

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "tag_more_companies",
            tag_id=tag.id,
            slug=tag.slug,
            _query={
                **q,
                "page": page + 1,
            },
        )

        activity_values = {}
        if role and paginator:
            company_ids = [c.id for c in paginator]
            rows = self.request.dbsession.execute(
                select(
                    Activity.company_id,
                    func.sum(Activity.value_net).label("value_net"),
                    func.sum(Activity.value_gross).label("value_gross"),
                )
                .filter(
                    Activity.company_id.in_(company_ids),
                    Activity.role == role,
                )
                .group_by(Activity.company_id)
            ).all()
            activity_values = {row.company_id: row for row in rows}

        return {
            "q": q,
            "tag": tag,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "colors": colors,
            "role_choices": role_choices,
            "activity_values": activity_values if role else None,
            "paginator": paginator,
            "next_page": next_page,
            "title": tag.name,
            "tag_pills": self.pills(tag),
            "form": form,
        }

    @view_config(route_name="tag_export_companies", permission="view")
    def export_companies(self):
        _ = self.request.translate
        tag = self.request.context.tag
        role = self.request.params.get("role", "")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        stmt = select(
            Company.id,
            Company.name,
            Company.street,
            Company.postcode,
            Company.city,
            Company.subdivision,
            Company.country,
            Company.website,
        )

        if _sort == "stars":
            count_col = func.count(companies_stars.c.company_id)
            stmt = (
                stmt.filter(Company.tags.any(name=tag.name))
                .join(companies_stars)
                .group_by(Company.id)
                .order_by(
                    count_col.asc() if _order == "asc" else count_col.desc(), Company.id
                )
            )
        else:
            col = sort_column(Company, _sort)
            stmt = stmt.filter(Company.tags.any(name=tag.name)).order_by(
                col.asc() if _order == "asc" else col.desc(), Company.id
            )

        companies = self.request.dbsession.execute(stmt).all()

        activity_values = {}
        if role and companies:
            company_ids = [c.id for c in companies]
            av_rows = self.request.dbsession.execute(
                select(
                    Activity.company_id,
                    func.sum(Activity.value_net).label("value_net"),
                    func.sum(Activity.value_gross).label("value_gross"),
                )
                .filter(
                    Activity.company_id.in_(company_ids),
                    Activity.role == role,
                )
                .group_by(Activity.company_id)
            ).all()
            activity_values = {row.company_id: row for row in av_rows}

        header_row = [
            _("Name"),
            _("Street"),
            _("Post code"),
            _("City"),
            _("Subdivision"),
            _("Country"),
            _("Website"),
        ]
        if role:
            header_row += [_("Value net"), _("Value gross")]

        rows = []
        for company in companies:
            row = [
                company.name,
                company.street,
                company.postcode,
                company.city,
                company.subdivision,
                company.country,
                company.website,
            ]
            if role:
                av = activity_values.get(company.id)
                row += [
                    float(av.value_net) if av and av.value_net is not None else None,
                    (
                        float(av.value_gross)
                        if av and av.value_gross is not None
                        else None
                    ),
                ]
            rows.append(row)

        response = make_export_response(self.request, rows, header_row)
        log.info(_("The user %s exported company data") % self.request.identity.name)
        return response

    @view_config(
        route_name="tag_count_companies",
        renderer="json",
        permission="view",
    )
    def count_companies(self):
        tag = self.request.context.tag
        return tag.count_companies

    @view_config(
        route_name="tag_projects",
        renderer="tag_projects.mako",
        permission="view",
    )
    @view_config(
        route_name="tag_more_projects",
        renderer="project_table#rows.mako",
        permission="view",
    )
    def projects(self):
        tag = self.request.context.tag
        page = int(self.request.params.get("page", 1))
        role = self.request.params.get("role", None)
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = [
            value for value in self.request.params.getall("subdivision") if value
        ]
        date_from = self.request.params.get("date_from", None)
        date_to = self.request.params.get("date_to", None)
        object_category = self.request.params.get("object_category", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        colors = dict(COLORS)
        sort_criteria = dict(SORT_CRITERIA_PROJECTS)
        order_criteria = dict(ORDER_CRITERIA)
        role_choices = {k: v for k, v in COMPANY_ROLES if k}
        q = {}

        stmt = select(Project)

        if role:
            q["role"] = role

        if status == "in_progress":
            stmt = stmt.filter(Project.deadline > now)
            q["status"] = status
        elif status == "completed":
            stmt = stmt.filter(Project.deadline < now)
            q["status"] = status

        if color:
            stmt = stmt.filter(Project.color == color)
            q["color"] = color

        if country:
            stmt = stmt.filter(Project.country == country)
            q["country"] = country

        if subdivision:
            stmt = stmt.filter(Project.subdivision.in_(subdivision))
            q["subdivision"] = list(subdivision)

        if stage:
            stmt = stmt.filter(Project.stage == stage)
            q["stage"] = stage

        if delivery_method:
            stmt = stmt.filter(Project.delivery_method == delivery_method)
            q["delivery_method"] = delivery_method

        if date_from:
            date_from_dt = datetime.datetime.strptime(date_from, "%Y-%m-%dT%H:%M")
            stmt = stmt.filter(Project.created_at >= date_from_dt)
            q["date_from"] = date_from

        if date_to:
            date_to_dt = datetime.datetime.strptime(date_to, "%Y-%m-%dT%H:%M")
            stmt = stmt.filter(Project.created_at <= date_to_dt)
            q["date_to"] = date_to

        if object_category:
            stmt = stmt.filter(Project.object_category == object_category)
            q["object_category"] = object_category

        if _sort == "stars":
            count_col = func.count(projects_stars.c.project_id)
            stmt = (
                stmt.filter(Project.tags.any(name=tag.name))
                .join(projects_stars)
                .group_by(Project.id)
                .order_by(
                    count_col.asc() if _order == "asc" else count_col.desc(), Project.id
                )
            )
        elif _sort == "comments":
            count_col = func.count(Project.comments)
            stmt = (
                stmt.filter(Project.tags.any(name=tag.name))
                .join(Project.comments)
                .group_by(Project.id)
                .order_by(count_col.asc() if _order == "asc" else count_col.desc())
            )
        else:
            col = sort_column(Project, _sort)
            stmt = stmt.filter(Project.tags.any(name=tag.name)).order_by(
                col.asc() if _order == "asc" else col.desc(), Project.id
            )

        q["sort"] = _sort
        q["order"] = _order

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_projects
            )

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        ).scalar()

        self.count_companies = tag.count_companies
        self.count_projects = counter

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "tag_more_projects",
            tag_id=tag.id,
            slug=tag.slug,
            _query={
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = ProjectFilterForm(self.request.GET, obj, request=self.request)

        activity_values = {}
        if role and paginator:
            project_ids = [p.id for p in paginator]
            rows = self.request.dbsession.execute(
                select(
                    Activity.project_id,
                    func.sum(Activity.value_net).label("value_net"),
                    func.sum(Activity.value_gross).label("value_gross"),
                )
                .filter(
                    Activity.project_id.in_(project_ids),
                    Activity.role == role,
                )
                .group_by(Activity.project_id)
            ).all()
            activity_values = {row.project_id: row for row in rows}

        return {
            "q": q,
            "tag": tag,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "colors": colors,
            "role_choices": role_choices,
            "activity_values": activity_values if role else None,
            "paginator": paginator,
            "next_page": next_page,
            "title": tag.name,
            "tag_pills": self.pills(tag),
            "form": form,
        }

    @view_config(route_name="tag_export_projects", permission="view")
    def export_projects(self):
        _ = self.request.translate
        tag = self.request.context.tag
        role = self.request.params.get("role", "")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        stmt = select(
            Project.id,
            Project.name,
            Project.object_category,
            Project.street,
            Project.postcode,
            Project.city,
            Project.subdivision,
            Project.country,
            Project.website,
            Project.deadline,
            Project.stage,
            Project.delivery_method,
            Project.usable_area,
        )

        if _sort == "stars":
            count_col = func.count(projects_stars.c.project_id)
            stmt = (
                stmt.filter(Project.tags.any(name=tag.name))
                .join(projects_stars)
                .group_by(Project.id)
                .order_by(
                    count_col.asc() if _order == "asc" else count_col.desc(), Project.id
                )
            )
        else:
            col = sort_column(Project, _sort)
            stmt = stmt.filter(Project.tags.any(name=tag.name)).order_by(
                col.asc() if _order == "asc" else col.desc(), Project.id
            )

        projects = self.request.dbsession.execute(stmt).all()

        activity_values = {}
        if role and projects:
            project_ids = [p.id for p in projects]
            av_rows = self.request.dbsession.execute(
                select(
                    Activity.project_id,
                    func.sum(Activity.value_net).label("value_net"),
                    func.sum(Activity.value_gross).label("value_gross"),
                )
                .filter(
                    Activity.project_id.in_(project_ids),
                    Activity.role == role,
                )
                .group_by(Activity.project_id)
            ).all()
            activity_values = {row.project_id: row for row in av_rows}

        header_row = [
            _("Name"),
            _("Object category"),
            _("Street"),
            _("Post code"),
            _("City"),
            _("Subdivision"),
            _("Country"),
            _("Website"),
            _("Deadline"),
            _("Stage"),
            _("Project delivery method"),
        ]
        if role:
            header_row += [
                _("Value net"),
                _("Value gross"),
                _("Net / m\u00b2"),
                _("Gross / m\u00b2"),
            ]

        rows = []
        for project in projects:
            row = [
                project.name,
                project.object_category or "",
                project.street,
                project.postcode,
                project.city,
                project.subdivision,
                project.country,
                project.website,
                project.deadline,
                project.stage,
                project.delivery_method,
            ]
            if role:
                av = activity_values.get(project.id)
                vn = float(av.value_net) if av and av.value_net is not None else None
                vg = (
                    float(av.value_gross) if av and av.value_gross is not None else None
                )
                ua = project.usable_area
                row += [
                    vn,
                    vg,
                    round(vn / float(ua), 2) if vn is not None and ua else None,
                    round(vg / float(ua), 2) if vg is not None and ua else None,
                ]
            rows.append(row)

        response = make_export_response(self.request, rows, header_row)
        log.info(_("The user %s exported project data") % self.request.identity.name)
        return response

    @view_config(
        route_name="tag_count_projects",
        renderer="json",
        permission="view",
    )
    def count_projects(self):
        tag = self.request.context.tag
        return tag.count_projects

    @view_config(
        route_name="tag_add_company",
        renderer="tag_add_company.mako",
        permission="edit",
    )
    def add_company(self):
        _ = self.request.translate
        form = CompanyLinkForm(self.request.POST, request=self.request)
        tag = self.request.context.tag

        if self.request.method == "POST" and form.validate():
            company = self.request.dbsession.execute(
                select(Company).filter_by(name=form.name.data)
            ).scalar_one_or_none()
            if company and company not in tag.companies:
                tag.companies.append(company)
                log.info(
                    _("The user %s has added a company to the tag")
                    % self.request.identity.name
                )
                self.request.session.flash(_("success:Added to the database"))
            next_url = self.request.route_url(
                "tag_companies",
                tag_id=tag.id,
                slug=tag.slug,
            )
            return HTTPSeeOther(location=next_url)
        return {
            "heading": _("Add a company"),
            "form": form,
            "tag": tag,
            "tag_pills": self.pills(tag),
        }

    @view_config(
        route_name="tag_add_project",
        renderer="tag_add_project.mako",
        permission="edit",
    )
    def add_project(self):
        _ = self.request.translate
        form = ProjectLinkForm(self.request.POST, request=self.request)
        tag = self.request.context.tag

        if self.request.method == "POST" and form.validate():
            project = self.request.dbsession.execute(
                select(Project).filter_by(name=form.name.data)
            ).scalar_one_or_none()
            if project and project not in tag.projects:
                tag.projects.append(project)
                log.info(
                    _("The user %s has added a project to the tag")
                    % self.request.identity.name
                )
                self.request.session.flash(_("success:Added to the database"))
            next_url = self.request.route_url(
                "tag_projects",
                tag_id=tag.id,
                slug=tag.slug,
            )
            return HTTPSeeOther(location=next_url)
        return {
            "heading": _("Add a project"),
            "form": form,
            "tag": tag,
            "tag_pills": self.pills(tag),
        }

    @view_config(route_name="tag_add", renderer="tag_form.mako", permission="edit")
    def add(self):
        _ = self.request.translate
        form = TagForm(self.request.POST, request=self.request)

        if self.request.method == "POST" and form.validate():
            tag = Tag(form.name.data)
            tag.created_by = self.request.identity
            self.request.dbsession.add(tag)
            self.request.dbsession.flush()
            clear_selected_rows(
                self.request,
                selected_tags,
                selected_tags.c.tag_id,
                [tag.id],
            )
            self.request.session.flash(_("success:Added to the database"))
            log.info(_("The user %s has added a tag") % self.request.identity.name)
            next_url = self.request.route_url("tag_all")
            return HTTPSeeOther(location=next_url)

        return {"heading": _("Add tag"), "form": form}

    @view_config(route_name="tag_edit", renderer="tag_form.mako", permission="edit")
    def edit(self):
        _ = self.request.translate
        tag = self.request.context.tag
        form = TagForm(self.request.POST, tag, request=self.request)

        if self.request.method == "POST" and form.validate():
            form.populate_obj(tag)
            tag.updated_by = self.request.identity
            self.request.session.flash(_("success:Changes have been saved"))
            log.info(
                _("The user %s changed the name of the tag")
                % self.request.identity.name
            )
            next_url = self.request.route_url("tag_all")
            return HTTPSeeOther(location=next_url)
        return {"heading": _("Edit tag"), "form": form}

    @view_config(route_name="tag_delete", request_method="POST", permission="edit")
    def delete(self):
        _ = self.request.translate
        tag = self.request.context.tag
        clear_selected_rows(
            self.request,
            selected_tags,
            selected_tags.c.tag_id,
            [tag.id],
        )
        self.request.dbsession.delete(tag)
        self.request.session.flash(_("success:Removed from the database"))
        log.info(_("The user %s removed the tag") % self.request.identity.name)
        next_url = self.request.route_url("home")
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="tag_del_row",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def tag_del_row(self):
        _ = self.request.translate
        tag = self.request.context.tag
        clear_selected_rows(
            self.request,
            selected_tags,
            selected_tags.c.tag_id,
            [tag.id],
        )
        self.request.dbsession.delete(tag)
        log.info(_("The user %s removed the tag") % self.request.identity.name)
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": "tagEvent"}
        return ""

    @view_config(
        route_name="tag_check",
        request_method="POST",
        renderer="json",
        permission="view",
    )
    def check(self):
        tag_id = self.request.context.tag.id
        checked = toggle_selected_item(
            self.request,
            selected_tags,
            selected_tags.c.tag_id,
            tag_id,
        )
        return {"checked": checked}

    @view_config(
        route_name="tag_select",
        renderer="tag_datalist.mako",
        request_method="GET",
    )
    def select(self):
        name = self.request.params.get("name") or self.request.params.get("tag")
        list_id = self.request.params.get("list_id", "tags")
        tags = []
        if name:
            tags = self.request.dbsession.execute(
                select(Tag).filter(contains_ci(Tag.name, name))
            ).scalars()
        return {"tags": tags, "list_id": list_id}

    @view_config(
        route_name="tag_search",
        renderer="tag_form.mako",
        permission="view",
    )
    def search(self):
        _ = self.request.translate
        form = TagSearchForm(self.request.POST)
        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "tag_all", _query={"name": form.name.data}
                )
            )
        return {"heading": _("Find the tag"), "form": form}
