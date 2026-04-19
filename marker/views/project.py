import datetime
import logging
from decimal import Decimal, InvalidOperation

from pyramid.httpexceptions import HTTPNotFound, HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import func, select
from webob.multidict import MultiDict

from ..forms import (
    ActivityForm,
    CommentForm,
    CompanyActivityForm,
    ContactForm,
    ProjectFilterForm,
    ProjectForm,
    ProjectSearchForm,
    TagLinkForm,
    ProjectAddAIForm,
)
from ..forms.select import (
    COLORS,
    COMPANY_ROLES,
    ORDER_CRITERIA,
    PROJECT_DELIVERY_METHODS,
    SORT_CRITERIA,
    SORT_CRITERIA_CONTACTS,
    SORT_CRITERIA_PROJECTS,
    STAGES,
    STATUS,
    USER_ROLES,
    select_countries,
    select_currencies,
)
from ..models import (
    Activity,
    Comment,
    Company,
    Contact,
    Project,
    Tag,
    User,
    projects_stars,
    projects_tags,
    selected_contacts,
    selected_projects,
    selected_tags,
)
from ..subscribers import get_subdivision_name
from ..utils.geo import location, location_details
from ..utils.paginator import get_paginator
from ..utils.website_autofill import project_autofill_from_website
from . import (
    Filter,
    clear_selected_rows,
    contains_ci,
    handle_bulk_selection,
    htmx_refresh_response,
    is_bulk_select_request,
    normalize_ci_expression,
    normalize_ci_value,
    polish_sort_expression,
    set_select_all_state,
    sort_column,
    toggle_selected_item,
)

log = logging.getLogger(__name__)


class ProjectView:
    def __init__(self, request):
        self.request = request

    def _normalized_tags(self):
        seen = set()
        tags = []
        for value in self.request.params.getall("tag"):
            name = value.strip()
            normalized = name.lower()
            if name and normalized not in seen:
                seen.add(normalized)
                tags.append(name)
        return tags

    def pills(self, project):
        _ = self.request.translate
        return [
            {
                "title": _("Project"),
                "icon": "briefcase",
                "url": self.request.route_url(
                    "project_view", project_id=project.id, slug=project.slug
                ),
                "count": None,
            },
            {
                "title": _("Companies"),
                "icon": "buildings",
                "url": self.request.route_url(
                    "project_companies", project_id=project.id, slug=project.slug
                ),
                "count": self.request.route_url(
                    "project_count_companies", project_id=project.id, slug=project.slug
                ),
                "event": "assocEvent",
                "init_value": project.count_companies,
            },
            {
                "title": _("Tags"),
                "icon": "tags",
                "url": self.request.route_url(
                    "project_tags", project_id=project.id, slug=project.slug
                ),
                "count": self.request.route_url(
                    "project_count_tags", project_id=project.id, slug=project.slug
                ),
                "event": "tagEvent",
                "init_value": project.count_tags,
            },
            {
                "title": _("Contacts"),
                "icon": "people",
                "url": self.request.route_url(
                    "project_contacts", project_id=project.id, slug=project.slug
                ),
                "count": self.request.route_url(
                    "project_count_contacts", project_id=project.id, slug=project.slug
                ),
                "event": "contactEvent",
                "init_value": project.count_contacts,
            },
            {
                "title": _("Comments"),
                "icon": "chat-left-text",
                "url": self.request.route_url(
                    "project_comments", project_id=project.id, slug=project.slug
                ),
                "count": self.request.route_url(
                    "project_count_comments", project_id=project.id, slug=project.slug
                ),
                "event": "commentEvent",
                "init_value": project.count_comments,
            },
            {
                "title": _("Stars"),
                "icon": "star",
                "url": self.request.route_url(
                    "project_stars", project_id=project.id, slug=project.slug
                ),
                "count": self.request.route_url(
                    "project_count_stars",
                    project_id=project.id,
                    slug=project.slug,
                ),
                "event": "starProjectEvent",
                "init_value": project.count_stars,
            },
            {
                "title": _("Similar"),
                "icon": "intersect",
                "url": self.request.route_url(
                    "project_similar", project_id=project.id, slug=project.slug
                ),
                "count": self.request.route_url(
                    "project_count_similar", project_id=project.id, slug=project.slug
                ),
                "event": "tagEvent",
                "init_value": project.count_similar,
            },
        ]

    @view_config(
        route_name="project_all",
        renderer="project_all.mako",
        permission="view",
    )
    @view_config(
        route_name="project_more",
        renderer="project_more.mako",
        permission="view",
    )
    @view_config(
        route_name="project_more_contacts",
        renderer="contact_more.mako",
        permission="view",
    )
    def all(self):
        page = int(self.request.params.get("page", 1))
        tags = self._normalized_tags()
        requested_view_mode = self.request.params.get("view", "projects")
        if requested_view_mode not in {"projects", "contacts"}:
            requested_view_mode = "projects"
        # Contact view is available only for tag-based result sets.
        view_mode = requested_view_mode if tags else "projects"
        show_contacts_toggle = bool(tags)
        name = self.request.params.get("name", None)
        street = self.request.params.get("street", None)
        postcode = self.request.params.get("postcode", None)
        city = self.request.params.get("city", None)
        subdivision = [
            value for value in self.request.params.getall("subdivision") if value
        ]
        country = self.request.params.get("country", None)
        website = self.request.params.get("website", None)
        color = self.request.params.get("color", None)
        deadline = self.request.params.get("deadline", None)
        deadline_from = self.request.params.get("deadline_from", None)
        deadline_to = self.request.params.get("deadline_to", None)
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
        usable_area_from = self.request.params.get("usable_area_from", None)
        usable_area_to = self.request.params.get("usable_area_to", None)
        cubic_volume_from = self.request.params.get("cubic_volume_from", None)
        cubic_volume_to = self.request.params.get("cubic_volume_to", None)
        currency = self.request.params.get("currency", None)
        value_net_from = self.request.params.get("value_net_from", None)
        value_net_to = self.request.params.get("value_net_to", None)
        value_gross_from = self.request.params.get("value_gross_from", None)
        value_gross_to = self.request.params.get("value_gross_to", None)
        date_from = self.request.params.get("date_from", None)
        date_to = self.request.params.get("date_to", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        order_criteria = dict(ORDER_CRITERIA)
        sort_criteria = dict(SORT_CRITERIA_PROJECTS)
        colors = dict(COLORS)
        statuses = dict(STATUS)
        stages = dict(STAGES)
        project_delivery_methods = dict(PROJECT_DELIVERY_METHODS)
        q = {}

        stmt = select(Project)

        if tags:
            normalized_tags = [normalize_ci_value(tag) for tag in tags]
            stmt = stmt.filter(
                Project.tags.any(normalize_ci_expression(Tag.name).in_(normalized_tags))
            )
            q["tag"] = tags

        if name:
            normalized_name = normalize_ci_value(name)
            stmt = stmt.filter(
                normalize_ci_expression(Project.name).like("%" + normalized_name + "%")
            )
            q["name"] = name

        if street:
            stmt = stmt.filter(contains_ci(Project.street, street))
            q["street"] = street

        if postcode:
            stmt = stmt.filter(contains_ci(Project.postcode, postcode))
            q["postcode"] = postcode

        if city:
            stmt = stmt.filter(contains_ci(Project.city, city))
            q["city"] = city

        if website:
            stmt = stmt.filter(contains_ci(Project.website, website))
            q["website"] = website

        if subdivision:
            stmt = stmt.filter(Project.subdivision.in_(subdivision))
            q["subdivision"] = list(subdivision)

        if country:
            stmt = stmt.filter(Project.country == country)
            q["country"] = country

        if color:
            stmt = stmt.filter(Project.color == color)
            q["color"] = color

        if stage:
            stmt = stmt.filter(Project.stage == stage)
            q["stage"] = stage

        if delivery_method:
            stmt = stmt.filter(Project.delivery_method == delivery_method)
            q["delivery_method"] = delivery_method

        if deadline:
            deadline_dt = datetime.datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
            stmt = stmt.filter(Project.deadline <= deadline_dt)
            q["deadline"] = deadline

        if deadline_from:
            deadline_from_dt = datetime.datetime.strptime(
                deadline_from, "%Y-%m-%dT%H:%M"
            )
            stmt = stmt.filter(Project.deadline >= deadline_from_dt)
            q["deadline_from"] = deadline_from

        if deadline_to:
            deadline_to_dt = datetime.datetime.strptime(deadline_to, "%Y-%m-%dT%H:%M")
            stmt = stmt.filter(Project.deadline <= deadline_to_dt)
            q["deadline_to"] = deadline_to

        if status == "in_progress":
            stmt = stmt.filter(Project.deadline > now)
            q["status"] = status
        elif status == "completed":
            stmt = stmt.filter(Project.deadline < now)
            q["status"] = status

        if usable_area_from:
            try:
                stmt = stmt.filter(Project.usable_area >= Decimal(usable_area_from))
                q["usable_area_from"] = usable_area_from
            except InvalidOperation:
                pass

        if usable_area_to:
            try:
                stmt = stmt.filter(Project.usable_area <= Decimal(usable_area_to))
                q["usable_area_to"] = usable_area_to
            except InvalidOperation:
                pass

        if cubic_volume_from:
            try:
                stmt = stmt.filter(Project.cubic_volume >= Decimal(cubic_volume_from))
                q["cubic_volume_from"] = cubic_volume_from
            except InvalidOperation:
                pass

        if cubic_volume_to:
            try:
                stmt = stmt.filter(Project.cubic_volume <= Decimal(cubic_volume_to))
                q["cubic_volume_to"] = cubic_volume_to
            except InvalidOperation:
                pass

        if date_from:
            date_from_dt = datetime.datetime.strptime(date_from, "%Y-%m-%dT%H:%M")
            stmt = stmt.filter(Project.created_at >= date_from_dt)
            q["date_from"] = date_from

        if date_to:
            date_to_dt = datetime.datetime.strptime(date_to, "%Y-%m-%dT%H:%M")
            stmt = stmt.filter(Project.created_at <= date_to_dt)
            q["date_to"] = date_to

        if view_mode == "contacts":
            q["view"] = "contacts"

        q["sort"] = _sort
        q["order"] = _order

        if _sort == "stars":
            if _order == "asc":
                stmt = (
                    stmt.join(projects_stars)
                    .group_by(Project.id)
                    .order_by(func.count(projects_stars.c.project_id).asc(), Project.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(projects_stars)
                    .group_by(Project.id)
                    .order_by(
                        func.count(projects_stars.c.project_id).desc(), Project.id
                    )
                )
        elif _sort == "comments":
            if _order == "asc":
                stmt = (
                    stmt.join(Project.comments)
                    .group_by(Project.id)
                    .order_by(func.count(Project.comments).asc())
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(Project.comments)
                    .group_by(Project.id)
                    .order_by(func.count(Project.comments).desc())
                )
        else:
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Project, _sort).asc(), Project.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Project, _sort).desc(), Project.id)

        selected_items = self.request.identity.selected_projects
        if view_mode == "contacts":
            project_ids = stmt.order_by(None).with_only_columns(Project.id).subquery()
            stmt = (
                select(Contact)
                .filter(Contact.project_id.in_(select(project_ids.c.id)))
                .order_by(polish_sort_expression(Contact.name).asc(), Contact.id)
            )
            selected_items = self.request.identity.selected_contacts

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(self.request, stmt, selected_items)

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_route = (
            "project_more_contacts" if view_mode == "contacts" else "project_more"
        )
        next_page = self.request.route_url(
            next_route,
            _query={
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = ProjectFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "colors": colors,
            "statuses": statuses,
            "stages": stages,
            "project_delivery_methods": project_delivery_methods,
            "currencies": dict(select_currencies()),
            "form": form,
            "view_mode": view_mode,
            "show_contacts_toggle": show_contacts_toggle,
            "contact_q": {"category": "projects"},
        }

    @view_config(
        route_name="project_comments",
        renderer="project_comments.mako",
        permission="view",
    )
    @view_config(
        route_name="project_more_comments",
        renderer="comment_more.mako",
        permission="view",
    )
    def comments(self):
        _ = self.request.translate
        project = self.request.context.project
        page = int(self.request.params.get("page", 1))
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = {
            "created_at": _("Date created"),
            "updated_at": _("Date modified"),
        }
        order_criteria = dict(ORDER_CRITERIA)
        q = {"sort": _sort, "order": _order}

        allowed_sorts = {"created_at", "updated_at"}
        if _sort not in allowed_sorts:
            _sort = "created_at"
            q["sort"] = _sort

        if _order not in {"asc", "desc"}:
            _order = "desc"
            q["order"] = _order

        stmt = select(Comment).filter(Comment.project_id == project.id)
        if _order == "asc":
            stmt = stmt.order_by(sort_column(Comment, _sort).asc(), Comment.id)
        else:
            stmt = stmt.order_by(sort_column(Comment, _sort).desc(), Comment.id)

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "project_more_comments",
            project_id=project.id,
            slug=project.slug,
            _query={
                **q,
                "page": page + 1,
            },
        )
        return {
            "q": q,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "project": project,
            "title": project.name,
            "project_pills": self.pills(project),
        }

    @view_config(
        route_name="project_map",
        renderer="project_map.mako",
        permission="view",
    )
    def map(self):
        name = self.request.params.get("name", None)
        street = self.request.params.get("street", None)
        postcode = self.request.params.get("postcode", None)
        city = self.request.params.get("city", None)
        subdivision = [
            value for value in self.request.params.getall("subdivision") if value
        ]
        country = self.request.params.get("country", None)
        website = self.request.params.get("website", None)
        color = self.request.params.get("color", None)
        deadline = self.request.params.get("deadline", None)
        stage = self.request.params.get("stage", None)
        delivery_method = self.request.params.get("delivery_method", None)
        status = self.request.params.get("status", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        q = {}

        stmt = select(Project)

        if name:
            normalized_name = normalize_ci_value(name)
            stmt = stmt.filter(
                normalize_ci_expression(Project.name).like("%" + normalized_name + "%")
            )
            q["name"] = name

        if street:
            stmt = stmt.filter(contains_ci(Project.street, street))
            q["street"] = street

        if postcode:
            stmt = stmt.filter(contains_ci(Project.postcode, postcode))
            q["postcode"] = postcode

        if city:
            stmt = stmt.filter(contains_ci(Project.city, city))
            q["city"] = city

        if website:
            stmt = stmt.filter(contains_ci(Project.website, website))
            q["website"] = website

        if subdivision:
            stmt = stmt.filter(Project.subdivision.in_(subdivision))
            q["subdivision"] = list(subdivision)

        if country:
            stmt = stmt.filter(Project.country == country)
            q["country"] = country

        if color:
            stmt = stmt.filter(Project.color == color)
            q["color"] = color

        if stage:
            stmt = stmt.filter(Project.stage == stage)
            q["stage"] = stage

        if delivery_method:
            stmt = stmt.filter(Project.delivery_method == delivery_method)
            q["delivery_method"] = delivery_method

        if deadline:
            deadline_dt = datetime.datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
            stmt = stmt.filter(Project.deadline <= deadline_dt)
            q["deadline"] = deadline

        if status == "in_progress":
            stmt = stmt.filter(Project.deadline > now)
            q["status"] = status
        elif status == "completed":
            stmt = stmt.filter(Project.deadline < now)
            q["status"] = status

        q["sort"] = _sort
        q["order"] = _order

        if _sort == "stars":
            if _order == "asc":
                stmt = (
                    stmt.join(projects_stars)
                    .group_by(Project.id)
                    .order_by(func.count(projects_stars.c.project_id).asc(), Project.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(projects_stars)
                    .group_by(Project.id)
                    .order_by(
                        func.count(projects_stars.c.project_id).desc(), Project.id
                    )
                )
        else:
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Project, _sort).asc(), Project.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Project, _sort).desc(), Project.id)

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        ).scalar()

        url = self.request.route_url("project_json", _query=q)
        return {"url": url, "q": q, "counter": counter}

    @view_config(
        route_name="project_json",
        renderer="json",
        permission="view",
    )
    def project_json(self):
        name = self.request.params.get("name", None)
        street = self.request.params.get("street", None)
        postcode = self.request.params.get("postcode", None)
        city = self.request.params.get("city", None)
        subdivision = self.request.params.get("subdivision", None)
        country = self.request.params.get("country", None)
        website = self.request.params.get("website", None)
        color = self.request.params.get("color", None)
        deadline = self.request.params.get("deadline", None)
        stage = self.request.params.get("stage", None)
        delivery_method = self.request.params.get("delivery_method", None)

        stmt = select(Project)

        if name:
            normalized_name = normalize_ci_value(name)
            stmt = stmt.filter(
                normalize_ci_expression(Project.name).like("%" + normalized_name + "%")
            )

        if street:
            stmt = stmt.filter(contains_ci(Project.street, street))

        if postcode:
            stmt = stmt.filter(contains_ci(Project.postcode, postcode))

        if city:
            stmt = stmt.filter(contains_ci(Project.city, city))

        if website:
            stmt = stmt.filter(contains_ci(Project.website, website))

        if subdivision:
            stmt = stmt.filter(Project.subdivision == subdivision)

        if country:
            stmt = stmt.filter(Project.country == country)

        if color:
            stmt = stmt.filter(Project.color == color)

        if stage:
            stmt = stmt.filter(Project.stage == stage)

        if delivery_method:
            stmt = stmt.filter(Project.delivery_method == delivery_method)

        if deadline:
            deadline_dt = datetime.datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
            stmt = stmt.filter(Project.deadline <= deadline_dt)

        projects = self.request.dbsession.execute(stmt).scalars()

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
            }
            for project in projects
        ]
        return res

    @view_config(
        route_name="project_uptime",
        renderer="project_uptime.mako",
        permission="view",
    )
    def uptime(self):
        stmt = select(Project).filter(
            Project.website.isnot(None), Project.website != ""
        )
        projects = self.request.dbsession.execute(stmt).scalars()
        items = [
            {
                "name": project.name,
                "website": project.website,
            }
            for project in projects
        ]
        return {"items": items}

    @view_config(
        route_name="project_uptime_check",
        renderer="json",
        permission="view",
    )
    def uptime_check(self):
        import urllib.error
        import urllib.request

        url = self.request.params.get("url", "")
        if not url:
            return {"status_code": None, "error": "No URL"}
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        try:
            req = urllib.request.Request(url, method="HEAD")
            req.add_header("User-Agent", "Marker/1.0")
            with urllib.request.urlopen(req, timeout=10) as resp:
                return {"status_code": resp.status}
        except urllib.error.HTTPError as exc:
            return {"status_code": exc.code}
        except Exception as exc:
            return {"status_code": None, "error": str(exc)}

    @view_config(
        route_name="project_count_companies",
        renderer="json",
        permission="view",
    )
    def count_companies(self):
        project = self.request.context.project
        return project.count_companies

    @view_config(
        route_name="project_count_tags",
        renderer="json",
        permission="view",
    )
    def count_tags(self):
        project = self.request.context.project
        return project.count_tags

    @view_config(
        route_name="project_count_contacts",
        renderer="json",
        permission="view",
    )
    def count_contacts(self):
        project = self.request.context.project
        return project.count_contacts

    @view_config(
        route_name="project_count_comments",
        renderer="json",
        permission="view",
    )
    def count_comments(self):
        project = self.request.context.project
        return project.count_comments

    @view_config(
        route_name="project_count_stars",
        renderer="json",
        permission="view",
    )
    def count_stars(self):
        project = self.request.context.project
        return project.count_stars

    @view_config(
        route_name="project_count_similar",
        renderer="json",
        permission="view",
    )
    def count_similar(self):
        project = self.request.context.project
        return project.count_similar

    @view_config(
        route_name="project_view",
        renderer="project_view.mako",
        permission="view",
    )
    @view_config(
        route_name="project_companies",
        renderer="project_companies.mako",
        permission="view",
    )
    @view_config(
        route_name="project_tags",
        renderer="project_tags.mako",
        permission="view",
    )
    @view_config(
        route_name="project_contacts",
        renderer="project_contacts.mako",
        permission="view",
    )
    def view(self):
        _ = self.request.translate
        project = self.request.context.project
        is_project_selected = (
            self.request.dbsession.execute(
                select(1)
                .select_from(selected_projects)
                .where(
                    selected_projects.c.user_id == self.request.identity.id,
                    selected_projects.c.project_id == project.id,
                )
                .limit(1)
            ).first()
            is not None
        )
        route_name = self.request.matched_route.name
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        q = {"sort": _sort, "order": _order}
        stages = dict(STAGES)
        countries = dict(select_countries())
        company_roles = dict(COMPANY_ROLES)
        delivery_methods = dict(PROJECT_DELIVERY_METHODS)
        companies_assoc = []
        contacts = []
        tags = []
        bulk_stmt = None
        bulk_selected_items = None

        if route_name == "project_companies":
            sort_criteria = {
                "name": _("Company"),
                "stage": _("Stage"),
                "role": _("Role"),
                "created_at": _("Created at"),
                "updated_at": _("Updated at"),
            }

            allowed_sorts = {"name", "stage", "role", "created_at", "updated_at"}
            if _sort not in allowed_sorts:
                _sort = "name"
                q["sort"] = _sort

            if _order not in {"asc", "desc"}:
                _order = "asc"
                q["order"] = _order

            _filter_stage = self.request.params.get("stage", "")
            _filter_role = self.request.params.get("role", "")
            if _filter_stage:
                q["stage"] = _filter_stage
            if _filter_role:
                q["role"] = _filter_role

            stmt = (
                select(Activity).join(Company).filter(Activity.project_id == project.id)
            )
            if _filter_stage:
                stmt = stmt.filter(Activity.stage == _filter_stage)
            if _filter_role:
                stmt = stmt.filter(Activity.role == _filter_role)
            order_column = {
                "name": polish_sort_expression(Company.name),
                "stage": Activity.stage,
                "role": Activity.role,
                "created_at": Company.created_at,
                "updated_at": Company.updated_at,
            }[_sort]
            if _order == "asc":
                stmt = stmt.order_by(order_column.asc(), Activity.company_id)
            else:
                stmt = stmt.order_by(order_column.desc(), Activity.company_id)
            companies_assoc = self.request.dbsession.execute(stmt).scalars().all()
            bulk_stmt = stmt
            bulk_selected_items = self.request.identity.selected_companies

        elif route_name == "project_contacts":
            sort_criteria = dict(SORT_CRITERIA_CONTACTS)

            allowed_sorts = {"name", "role", "created_at", "updated_at"}
            if _sort not in allowed_sorts:
                _sort = "created_at"
                q["sort"] = _sort

            if _order not in {"asc", "desc"}:
                _order = "desc"
                q["order"] = _order

            stmt = select(Contact).filter(Contact.project_id == project.id)
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Contact, _sort).asc(), Contact.id)
            else:
                stmt = stmt.order_by(sort_column(Contact, _sort).desc(), Contact.id)
            contacts = self.request.dbsession.execute(stmt).scalars().all()
            bulk_stmt = stmt
            bulk_selected_items = self.request.identity.selected_contacts
        elif route_name == "project_tags":
            sort_criteria = {
                "name": _("Tag"),
                "created_at": _("Date created"),
                "updated_at": _("Date modified"),
            }

            allowed_sorts = {"name", "created_at", "updated_at"}
            if _sort not in allowed_sorts:
                _sort = "created_at"
                q["sort"] = _sort

            if _order not in {"asc", "desc"}:
                _order = "asc"
                q["order"] = _order

            stmt = select(Tag).filter(Tag.projects.any(Project.id == project.id))
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Tag, _sort).asc(), Tag.id)
            else:
                stmt = stmt.order_by(sort_column(Tag, _sort).desc(), Tag.id)
            tags = self.request.dbsession.execute(stmt).scalars().all()
            bulk_stmt = stmt
            bulk_selected_items = self.request.identity.selected_tags

        if is_bulk_select_request(self.request):
            checked = self.request.params.get("checked", "false").lower() == "true"
            if bulk_stmt is not None and bulk_selected_items is not None:
                return handle_bulk_selection(
                    self.request,
                    bulk_stmt,
                    bulk_selected_items,
                )

            set_select_all_state(self.request, checked)
            return htmx_refresh_response(self.request)

        return {
            "project": project,
            "is_project_selected": is_project_selected,
            "stages": stages,
            "filter_stages": {k: v for k, v in stages.items() if k},
            "countries": countries,
            "currencies": dict(select_currencies()),
            "company_roles": company_roles,
            "filter_roles": {k: v for k, v in company_roles.items() if k},
            "delivery_methods": delivery_methods,
            "companies_assoc": companies_assoc,
            "contacts": contacts,
            "tags": tags,
            "q": q,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "title": project.name,
            "project_pills": self.pills(project),
        }

    @view_config(
        route_name="project_similar",
        renderer="project_similar.mako",
        permission="view",
    )
    @view_config(
        route_name="project_more_similar",
        renderer="project_more.mako",
        permission="view",
    )
    def similar(self):
        _ = self.request.translate
        project = self.request.context.project
        page = int(self.request.params.get("page", 1))
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = [
            value for value in self.request.params.getall("subdivision") if value
        ]
        deadline_from = self.request.params.get("deadline_from", None)
        deadline_to = self.request.params.get("deadline_to", None)
        usable_area_from = self.request.params.get("usable_area_from", None)
        usable_area_to = self.request.params.get("usable_area_to", None)
        cubic_volume_from = self.request.params.get("cubic_volume_from", None)
        cubic_volume_to = self.request.params.get("cubic_volume_to", None)
        date_from = self.request.params.get("date_from", None)
        date_to = self.request.params.get("date_to", None)
        _sort = self.request.params.get("sort", "shared_tags")
        _order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        colors = dict(COLORS)
        statuses = dict(STATUS)
        stages = dict(STAGES)
        project_delivery_methods = dict(PROJECT_DELIVERY_METHODS)
        order_criteria = dict(ORDER_CRITERIA)
        sort_criteria = {"shared_tags": _("Tags"), **dict(SORT_CRITERIA_PROJECTS)}
        q = {}

        allowed_sorts = set(sort_criteria.keys())
        if _sort not in allowed_sorts:
            _sort = "shared_tags"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        # Compute similar projects through association-table self-join.
        # This avoids correlated subqueries over tags that are expensive on large datasets.
        base_tags = projects_tags.alias("base_tags")
        other_tags = projects_tags.alias("other_tags")
        similarity = (
            select(
                other_tags.c.project_id.label("project_id"),
                func.count(func.distinct(base_tags.c.tag_id)).label("shared_tags"),
            )
            .select_from(
                base_tags.join(other_tags, base_tags.c.tag_id == other_tags.c.tag_id)
            )
            .where(
                base_tags.c.project_id == project.id,
                other_tags.c.project_id != project.id,
            )
            .group_by(other_tags.c.project_id)
            .subquery()
        )

        stmt = select(Project).join(similarity, similarity.c.project_id == Project.id)

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

        if deadline_from:
            deadline_from_dt = datetime.datetime.strptime(
                deadline_from, "%Y-%m-%dT%H:%M"
            )
            stmt = stmt.filter(Project.deadline >= deadline_from_dt)
            q["deadline_from"] = deadline_from

        if deadline_to:
            deadline_to_dt = datetime.datetime.strptime(deadline_to, "%Y-%m-%dT%H:%M")
            stmt = stmt.filter(Project.deadline <= deadline_to_dt)
            q["deadline_to"] = deadline_to

        if date_from:
            date_from_dt = datetime.datetime.strptime(date_from, "%Y-%m-%dT%H:%M")
            stmt = stmt.filter(Project.created_at >= date_from_dt)
            q["date_from"] = date_from

        if date_to:
            date_to_dt = datetime.datetime.strptime(date_to, "%Y-%m-%dT%H:%M")
            stmt = stmt.filter(Project.created_at <= date_to_dt)
            q["date_to"] = date_to

        if usable_area_from:
            try:
                stmt = stmt.filter(Project.usable_area >= Decimal(usable_area_from))
                q["usable_area_from"] = usable_area_from
            except InvalidOperation:
                pass

        if usable_area_to:
            try:
                stmt = stmt.filter(Project.usable_area <= Decimal(usable_area_to))
                q["usable_area_to"] = usable_area_to
            except InvalidOperation:
                pass

        if cubic_volume_from:
            try:
                stmt = stmt.filter(Project.cubic_volume >= Decimal(cubic_volume_from))
                q["cubic_volume_from"] = cubic_volume_from
            except InvalidOperation:
                pass

        if cubic_volume_to:
            try:
                stmt = stmt.filter(Project.cubic_volume <= Decimal(cubic_volume_to))
                q["cubic_volume_to"] = cubic_volume_to
            except InvalidOperation:
                pass

        q["sort"] = _sort
        q["order"] = _order

        if _sort == "shared_tags":
            if _order == "asc":
                stmt = stmt.order_by(similarity.c.shared_tags.asc(), Project.id)
            else:
                stmt = stmt.order_by(similarity.c.shared_tags.desc(), Project.id)
        elif _sort == "stars":
            if _order == "asc":
                stmt = (
                    stmt.join(projects_stars)
                    .group_by(Project.id)
                    .order_by(func.count(projects_stars.c.project_id).asc(), Project.id)
                )
            else:
                stmt = (
                    stmt.join(projects_stars)
                    .group_by(Project.id)
                    .order_by(
                        func.count(projects_stars.c.project_id).desc(), Project.id
                    )
                )
        elif _sort == "comments":
            if _order == "asc":
                stmt = (
                    stmt.join(Project.comments)
                    .group_by(Project.id)
                    .order_by(func.count(Project.comments).asc())
                )
            else:
                stmt = (
                    stmt.join(Project.comments)
                    .group_by(Project.id)
                    .order_by(func.count(Project.comments).desc())
                )
        elif _order == "asc":
            stmt = stmt.order_by(sort_column(Project, _sort).asc(), Project.id)
        else:
            stmt = stmt.order_by(sort_column(Project, _sort).desc(), Project.id)

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_projects
            )

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        shared_tag_counts = {}
        shared_tag_labels = {}
        if paginator:
            similar_ids = [item.id for item in paginator]
            shared_rows = self.request.dbsession.execute(
                select(similarity.c.project_id, similarity.c.shared_tags).where(
                    similarity.c.project_id.in_(similar_ids)
                )
            ).all()
            shared_tag_counts = {
                project_id: int(shared_tags or 0)
                for project_id, shared_tags in shared_rows
            }

            shared_tag_name_rows = self.request.dbsession.execute(
                select(other_tags.c.project_id, Tag.name)
                .select_from(
                    base_tags.join(
                        other_tags,
                        base_tags.c.tag_id == other_tags.c.tag_id,
                    ).join(Tag, Tag.id == base_tags.c.tag_id)
                )
                .where(
                    base_tags.c.project_id == project.id,
                    other_tags.c.project_id.in_(similar_ids),
                )
                .distinct()
            ).all()

            tag_names_by_project = {}
            for similar_project_id, tag_name in shared_tag_name_rows:
                if not tag_name:
                    continue
                tag_names_by_project.setdefault(similar_project_id, set()).add(tag_name)

            shared_tag_labels = {
                similar_project_id: ", ".join(sorted(names, key=normalize_ci_value))
                for similar_project_id, names in tag_names_by_project.items()
            }

        next_page = self.request.route_url(
            "project_more_similar",
            project_id=project.id,
            slug=project.slug,
            colors=colors,
            _query={
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = ProjectFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "project": project,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "statuses": statuses,
            "stages": stages,
            "project_delivery_methods": project_delivery_methods,
            "currencies": dict(select_currencies()),
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "show_shared_tags": True,
            "shared_tag_counts": shared_tag_counts,
            "shared_tag_labels": shared_tag_labels,
            "title": project.name,
            "project_pills": self.pills(project),
            "form": form,
        }

    @view_config(
        route_name="project_add", renderer="project_form.mako", permission="edit"
    )
    def add(self):
        _ = self.request.translate
        form = ProjectForm(self.request.POST, request=self.request)
        countries = dict(select_countries())
        tags = self._normalized_tags()

        if self.request.method == "POST" and form.validate():
            website = form.website.data
            project = Project(
                name=form.name.data,
                street=form.street.data,
                postcode=form.postcode.data,
                city=form.city.data,
                subdivision=form.subdivision.data,
                country=form.country.data,
                website=website,
                color=form.color.data,
                deadline=form.deadline.data,
                stage=form.stage.data,
                delivery_method=form.delivery_method.data,
                usable_area=form.usable_area.data,
                cubic_volume=form.cubic_volume.data,
            )
            loc = location(
                street=form.street.data,
                city=form.city.data,
                # state=getattr(
                #     pycountry.subdivisions.get(code=form.subdivision.data), "name", ""
                # ),
                country=countries.get(form.country.data),
                postalcode=form.postcode.data,
            )
            if loc is not None:
                project.latitude = loc["lat"]
                project.longitude = loc["lon"]

            project.created_by = self.request.identity
            self.request.dbsession.add(project)
            self.request.dbsession.flush()
            clear_selected_rows(
                self.request,
                selected_projects,
                selected_projects.c.project_id,
                [project.id],
            )
            clear_selected_rows(
                self.request,
                projects_stars,
                projects_stars.c.project_id,
                [project.id],
            )

            for tag_name in tags:
                tag = self.request.dbsession.execute(
                    select(Tag).filter_by(name=tag_name)
                ).scalar_one_or_none()

                if not tag:
                    tag = Tag(name=tag_name)
                    tag.created_by = self.request.identity
                if tag not in project.tags:
                    project.tags.append(tag)

            self.request.session.flash(_("success:Added to the database"))
            self.request.session.flash(_("info:Add tags and contacts"))
            log.info(_("The user %s has added a project") % self.request.identity.name)
            next_url = self.request.route_url(
                "project_view", project_id=project.id, slug=project.slug
            )
            return HTTPSeeOther(location=next_url)

        if self.request.query_string:
            form.name.data = self.request.params.get("name", None)
            form.street.data = self.request.params.get("street", None)
            form.postcode.data = self.request.params.get("postcode", None)
            form.city.data = self.request.params.get("city", None)
            form.country.data = self.request.params.get("country", None)
            form.subdivision.data = self.request.params.get("subdivision", None)
            form.website.data = self.request.params.get("website", None)
            form.color.data = self.request.params.get("color", None)
            form.deadline.data = self.request.params.get("deadline", None)
            form.stage.data = self.request.params.get("stage", None)
            form.delivery_method.data = self.request.params.get("delivery_method", None)

        return {"heading": _("Add a project"), "form": form, "tags": tags}

    @view_config(
        route_name="project_website_autofill",
        renderer="json",
        permission="edit",
    )
    def website_autofill(self):
        website = self.request.params.get("website", "")
        try:
            fields = project_autofill_from_website(website)
        except Exception as e:
            log.error("project_website_autofill error: %s", e)
            _ = self.request.translate
            error_msg = str(e)
            # If the error message contains a long API response, only show a summary
            if "Response:" in error_msg and len(error_msg) > 300:
                error_msg = (
                    error_msg.split("Response:")[0].strip() + " (details omitted)"
                )
            flash_msg = f"Autofill error: {error_msg}"
            max_len = 500
            if len(flash_msg.encode("utf-8")) > max_len:
                flash_msg = (
                    flash_msg.encode("utf-8")[:max_len].decode("utf-8", errors="ignore")
                    + "..."
                )
            self.request.session.flash(_(flash_msg), "error")
            self.request.response.status_code = 502
            return {"error": str(e), "fields": {}}
        return {"fields": fields}

    @view_config(
        route_name="project_edit", renderer="project_form.mako", permission="edit"
    )
    def edit(self):
        _ = self.request.translate
        project = self.request.context.project
        form = ProjectForm(self.request.POST, project, request=self.request)
        countries = dict(select_countries())

        if self.request.method == "POST" and form.validate():
            form.populate_obj(project)
            loc = location(
                street=form.street.data,
                city=form.city.data,
                subdivision=get_subdivision_name(form.subdivision.data),
                country=countries.get(form.country.data),
                postalcode=form.postcode.data,
            )
            if loc is not None:
                project.latitude = loc["lat"]
                project.longitude = loc["lon"]

            project.updated_by = self.request.identity
            self.request.session.flash(_("success:Changes have been saved"))
            next_url = self.request.route_url(
                "project_view",
                project_id=project.id,
                slug=project.slug,
            )
            log.info(
                _("The user %s changed the project details")
                % self.request.identity.name
            )
            return HTTPSeeOther(location=next_url)
        return {"heading": _("Edit project details"), "form": form}

    @view_config(
        route_name="project_delete",
        request_method="POST",
        permission="edit",
    )
    def delete(self):
        _ = self.request.translate
        project = self.request.context.project
        contact_ids = (
            self.request.dbsession.execute(
                select(Contact.id).where(Contact.project_id == project.id)
            )
            .scalars()
            .all()
        )
        clear_selected_rows(
            self.request,
            projects_stars,
            projects_stars.c.project_id,
            [project.id],
        )
        clear_selected_rows(
            self.request,
            selected_contacts,
            selected_contacts.c.contact_id,
            contact_ids,
        )
        clear_selected_rows(
            self.request,
            selected_projects,
            selected_projects.c.project_id,
            [project.id],
        )
        self.request.dbsession.delete(project)
        self.request.session.flash(_("success:Removed from the database"))
        log.info(_("The user %s deleted the project") % self.request.identity.name)
        next_url = self.request.route_url("home")
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="project_del_row",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def del_row(self):
        _ = self.request.translate
        project = self.request.context.project
        contact_ids = (
            self.request.dbsession.execute(
                select(Contact.id).where(Contact.project_id == project.id)
            )
            .scalars()
            .all()
        )
        clear_selected_rows(
            self.request,
            selected_contacts,
            selected_contacts.c.contact_id,
            contact_ids,
        )
        clear_selected_rows(
            self.request,
            selected_projects,
            selected_projects.c.project_id,
            [project.id],
        )
        clear_selected_rows(
            self.request,
            projects_stars,
            projects_stars.c.project_id,
            [project.id],
        )
        self.request.dbsession.delete(project)
        log.info(_("The user %s deleted the project") % self.request.identity.name)
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": "projectEvent"}
        return ""

    @view_config(
        route_name="project_search",
        renderer="project_form.mako",
        permission="view",
    )
    def search(self):
        _ = self.request.translate
        form = ProjectSearchForm(self.request.POST)
        tags = self._normalized_tags()
        q = {}
        for fieldname, value in form.data.items():
            if value:
                q[fieldname] = value

        if tags:
            q["tag"] = tags

        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "project_all",
                    _query=q,
                )
            )
        return {"heading": _("Find a project"), "form": form, "tags": tags}

    @view_config(
        route_name="project_star",
        request_method="POST",
        renderer="string",
        permission="view",
    )
    def star(self):
        project = self.request.context.project
        if project in self.request.identity.projects_stars:
            self.request.identity.projects_stars.remove(project)
            self.request.response.headers = {"HX-Trigger": "starProjectEvent"}
            return '<i class="bi bi-star"></i>'
        else:
            self.request.identity.projects_stars.append(project)
            self.request.response.headers = {"HX-Trigger": "starProjectEvent"}
            return '<i class="bi bi-star-fill"></i>'

    @view_config(
        route_name="project_stars",
        renderer="project_stars.mako",
        permission="view",
    )
    @view_config(
        route_name="project_more_stars",
        renderer="user_more.mako",
        permission="view",
    )
    def projects_stars(self):
        _ = self.request.translate
        project = self.request.context.project
        page = int(self.request.params.get("page", 1))
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = {
            "name": _("Name"),
            "fullname": _("Fullname"),
            "email": _("Email"),
            "created_at": _("Date created"),
            "updated_at": _("Date modified"),
        }
        order_criteria = dict(ORDER_CRITERIA)
        q = {"sort": _sort, "order": _order}
        user_roles = dict(USER_ROLES)

        allowed_sorts = {"name", "fullname", "email", "created_at", "updated_at"}
        if _sort not in allowed_sorts:
            _sort = "created_at"
            q["sort"] = _sort

        if _order not in {"asc", "desc"}:
            _order = "desc"
            q["order"] = _order

        stmt = (
            select(User)
            .join(projects_stars)
            .filter(project.id == projects_stars.c.project_id)
        )
        if _order == "asc":
            stmt = stmt.order_by(sort_column(User, _sort).asc(), User.id)
        else:
            stmt = stmt.order_by(sort_column(User, _sort).desc(), User.id)

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "project_more_stars",
            project_id=project.id,
            slug=project.slug,
            _query={
                **q,
                "page": page + 1,
            },
        )
        return {
            "q": q,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "project": project,
            "title": project.name,
            "roles": user_roles,
            "project_pills": self.pills(project),
        }

    @view_config(
        route_name="project_add_company",
        renderer="project_activity_form.mako",
        permission="edit",
    )
    def add_company(self):
        _ = self.request.translate
        form = CompanyActivityForm(self.request.POST, request=self.request)
        project = self.request.context.project

        if self.request.method == "POST" and form.validate():
            company = self.request.dbsession.execute(
                select(Company).filter_by(name=form.name.data)
            ).scalar_one_or_none()

            if company:
                exist = self.request.dbsession.execute(
                    select(Activity).filter_by(
                        company_id=company.id, project_id=project.id
                    )
                ).scalar_one_or_none()

                if not exist:
                    with self.request.dbsession.no_autoflush:
                        a = Activity(
                            stage=form.stage.data,
                            role=form.role.data,
                            currency=form.currency.data,
                            value_net=form.value_net.data,
                            value_gross=form.value_gross.data,
                        )
                        a.company = company
                        project.companies.append(a)
                        log.info(
                            _("The user %s added the company to the project")
                            % self.request.identity.name
                        )
                        self.request.session.flash(_("success:Added to the database"))
            next_url = self.request.route_url(
                "project_companies", project_id=project.id, slug=project.slug
            )
            return HTTPSeeOther(location=next_url)
        return {
            "heading": _("Add a company"),
            "form": form,
            "project": project,
            "project_pills": self.pills(project),
        }

    @view_config(
        route_name="project_check",
        request_method="POST",
        renderer="json",
        permission="view",
    )
    def check(self):
        project_id = self.request.context.project.id
        set_select_all_state(self.request, False)
        checked = toggle_selected_item(
            self.request,
            selected_projects,
            selected_projects.c.project_id,
            project_id,
        )
        return {"checked": checked}

    @view_config(
        route_name="project_select",
        renderer="project_datalist.mako",
        request_method="GET",
    )
    def select(self):
        name = self.request.params.get("name")
        projects = []
        if name:
            projects = self.request.dbsession.execute(
                select(Project).filter(
                    normalize_ci_expression(Project.name).like(
                        "%" + normalize_ci_value(name) + "%"
                    )
                )
            ).scalars()
        return {"projects": projects}

    @view_config(
        route_name="project_add_tag",
        renderer="project_add_tag.mako",
        permission="edit",
    )
    def add_tag(self):
        _ = self.request.translate
        form = TagLinkForm(self.request.POST, request=self.request)
        project = self.request.context.project

        if self.request.method == "POST" and form.validate():
            created_tag = False
            tag = self.request.dbsession.execute(
                select(Tag).filter_by(name=form.name.data)
            ).scalar_one_or_none()

            if not tag:
                tag = Tag(name=form.name.data)
                tag.created_by = self.request.identity
                created_tag = True
            if tag not in project.tags:
                project.tags.append(tag)
                if created_tag:
                    self.request.dbsession.flush()
                    clear_selected_rows(
                        self.request,
                        selected_tags,
                        selected_tags.c.tag_id,
                        [tag.id],
                    )
                log.info(
                    _("The user %s has added a tag to the project")
                    % self.request.identity.name
                )
                self.request.session.flash(_("success:Added to the database"))
            next_url = self.request.route_url(
                "project_tags", project_id=project.id, slug=project.slug
            )
            return HTTPSeeOther(location=next_url)
        return {
            "heading": _("Add a tag"),
            "form": form,
            "project": project,
            "project_pills": self.pills(project),
        }

    @view_config(
        route_name="project_add_contact",
        renderer="project_add_contact.mako",
        permission="edit",
    )
    def add_contact(self):
        _ = self.request.translate
        form = ContactForm(self.request.POST, request=self.request)
        project = self.request.context.project

        if self.request.method == "POST" and form.validate():
            contact = Contact(
                name=form.name.data,
                role=form.role.data,
                phone=form.phone.data,
                email=form.email.data,
                color=form.color.data,
            )
            contact.created_by = self.request.identity
            if contact not in project.contacts:
                project.contacts.append(contact)
                self.request.dbsession.flush()
                clear_selected_rows(
                    self.request,
                    selected_contacts,
                    selected_contacts.c.contact_id,
                    [contact.id],
                )
                log.info(
                    _("The user %s has added a contact to the project")
                    % self.request.identity.name
                )
                self.request.session.flash(_("success:Added to the database"))
            next_url = self.request.route_url(
                "project_contacts", project_id=project.id, slug=project.slug
            )
            return HTTPSeeOther(location=next_url)
        return {
            "heading": _("Add a contact"),
            "form": form,
            "project": project,
            "project_pills": self.pills(project),
        }

    @view_config(
        route_name="project_add_comment",
        renderer="project_add_comment.mako",
        permission="edit",
    )
    def project_add_comment(self):
        _ = self.request.translate
        project = self.request.context.project
        form = CommentForm(self.request.POST, request=self.request)
        if self.request.method == "POST" and form.validate():
            comment = Comment(comment=form.comment.data)
            comment.created_by = self.request.identity
            project.comments.append(comment)
            log.info(_("The user %s added a comment") % self.request.identity.name)
            self.request.session.flash(_("success:Added to the database"))
            next_url = self.request.route_url(
                "project_comments", project_id=project.id, slug=project.slug
            )
            return HTTPSeeOther(location=next_url)
        return {
            "heading": _("Add a comment"),
            "form": form,
            "project": project,
            "project_pills": self.pills(project),
        }

    @view_config(
        route_name="project_activity_edit",
        renderer="activity_form.mako",
        permission="edit",
    )
    def project_activity_edit(self):
        _ = self.request.translate

        company_id = int(self.request.matchdict["company_id"])
        project_id = int(self.request.matchdict["project_id"])

        company = self.request.dbsession.execute(
            select(Company).filter_by(id=company_id)
        ).scalar_one_or_none()

        if not company:
            raise HTTPNotFound

        project = self.request.dbsession.execute(
            select(Project).filter_by(id=project_id)
        ).scalar_one_or_none()

        if not project:
            raise HTTPNotFound

        assoc = self.request.dbsession.execute(
            select(Activity).filter_by(company_id=company.id, project_id=project.id)
        ).scalar()

        form = ActivityForm(self.request.POST, assoc, request=self.request)

        if self.request.method == "POST" and form.validate():
            form.populate_obj(assoc)

            self.request.session.flash(_("success:Changes have been saved"))
            next_url = self.request.route_url(
                "company_projects", company_id=company.id, slug=company.slug
            )
            log.info(
                _("The user %s changed the activity details")
                % self.request.identity.name
            )
            return HTTPSeeOther(location=next_url)
        return {
            "heading": _("Edit activity details"),
            "form": form,
            "company": company,
            "project": project,
        }

    @view_config(
        route_name="unlink_tag_project",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def unlink_tag(self):
        _ = self.request.translate
        project_id = int(self.request.matchdict["project_id"])
        tag_id = int(self.request.matchdict["tag_id"])

        project = self.request.dbsession.execute(
            select(Project).filter_by(id=project_id)
        ).scalar_one_or_none()

        if not project:
            raise HTTPNotFound

        tag = self.request.dbsession.execute(
            select(Tag).filter_by(id=tag_id)
        ).scalar_one_or_none()

        if not tag:
            raise HTTPNotFound

        project.tags.remove(tag)
        log.info(
            _("The user %s unlinked the tag from the project")
            % self.request.identity.name
        )
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": "tagEvent"}
        return ""

    @view_config(
        route_name="project_add_ai",
        renderer="project/project_add_ai.mako",
        permission="edit",
    )
    def add_ai(self):
        _ = self.request.translate

        form = ProjectAddAIForm(
            self.request.POST if self.request.method == "POST" else None
        )
        if self.request.method == "POST" and form.validate():
            website = form.website.data.strip()
            try:
                autofill = project_autofill_from_website(website)
            except Exception as e:
                error_msg = str(e)
                # If the error message contains a long API response, only show a summary
                if "Response:" in error_msg and len(error_msg) > 300:
                    error_msg = (
                        error_msg.split("Response:")[0].strip() + " (details omitted)"
                    )
                flash_msg = f"Autofill error: {error_msg}"
                max_len = 500
                if len(flash_msg.encode("utf-8")) > max_len:
                    flash_msg = (
                        flash_msg.encode("utf-8")[:max_len].decode(
                            "utf-8", errors="ignore"
                        )
                        + "..."
                    )
                self.request.session.flash(_(flash_msg), "error")
                if self.request.headers.get("HX-Request"):
                    response = self.request.response
                    # Redirect to the same form page to force a full reload and avoid card-in-card
                    response.headers = {
                        "HX-Redirect": self.request.route_url("project_add_ai")
                    }
                    response.status_code = getattr(e, "status_code", 200)
                    return response
                return {"heading": _("Add a project using AI autofill"), "form": form}
            autofill = dict(autofill)
            autofill["website"] = website

            project_form = ProjectForm(MultiDict(autofill), request=self.request)
            name = project_form.name.data or ""
            if name:
                existing = self.request.dbsession.execute(
                    select(Project).where(func.lower(Project.name) == func.lower(name))
                ).scalar_one_or_none()
                if existing:
                    self.request.session.flash(
                        _(
                            "warning:A project with the name obtained from the provided website address already exists in the database."
                        )
                    )
                    next_url = self.request.route_url(
                        "project_view", project_id=existing.id, slug=existing.slug
                    )
                    if self.request.headers.get("HX-Request"):
                        response = self.request.response
                        response.headers["HX-Redirect"] = next_url
                        response.status_code = 200
                        return response
                    return HTTPSeeOther(location=next_url)

            geo = location_details(
                street=project_form.street.data,
                city=project_form.city.data,
                country=project_form.country.data,
                postalcode=project_form.postcode.data,
            )
            project = Project(
                name=project_form.name.data,
                street=project_form.street.data,
                postcode=project_form.postcode.data,
                city=project_form.city.data,
                subdivision=project_form.subdivision.data,
                country=project_form.country.data,
                website=project_form.website.data,
                color=project_form.color.data,
                deadline=project_form.deadline.data,
                stage=project_form.stage.data,
                delivery_method=project_form.delivery_method.data,
                usable_area=project_form.usable_area.data,
                cubic_volume=project_form.cubic_volume.data,
            )
            if geo:
                project.latitude = geo.get("lat")
                project.longitude = geo.get("lon")
            project.created_by = self.request.identity
            self.request.dbsession.add(project)
            self.request.dbsession.flush()
            self.request.session.flash(_("success:Added to the database"))
            next_url = self.request.route_url(
                "project_view", project_id=project.id, slug=project.slug
            )
            if self.request.headers.get("HX-Request"):
                response = self.request.response
                response.headers["HX-Redirect"] = next_url
                response.status_code = 200
                return response
            return HTTPSeeOther(location=next_url)
        return {"heading": _("Add a project using AI autofill"), "form": form}
