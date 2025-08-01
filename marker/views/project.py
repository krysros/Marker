import datetime
import logging

import pycountry
from pyramid.httpexceptions import HTTPNotFound, HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import and_, func, select

from ..forms import (
    ActivityForm,
    CommentForm,
    CompanyActivityForm,
    ContactForm,
    ProjectFilterForm,
    ProjectForm,
    ProjectSearchForm,
    TagLinkForm,
)
from ..forms.select import (
    COLORS,
    COMPANY_ROLES,
    ORDER_CRITERIA,
    PROJECT_DELIVERY_METHODS,
    SORT_CRITERIA_PROJECTS,
    STAGES,
    STATUS,
    USER_ROLES,
    select_countries,
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
)
from ..utils.geo import location
from ..utils.paginator import get_paginator
from . import Filter

log = logging.getLogger(__name__)


class ProjectView:
    def __init__(self, request):
        self.request = request

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
    def all(self):
        page = int(self.request.params.get("page", 1))
        name = self.request.params.get("name", None)
        street = self.request.params.get("street", None)
        postcode = self.request.params.get("postcode", None)
        city = self.request.params.get("city", None)
        subdivision = self.request.params.getall("subdivision")
        country = self.request.params.get("country", None)
        website = self.request.params.get("website", None)
        color = self.request.params.get("color", None)
        deadline = self.request.params.get("deadline", None)
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
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

        if name:
            stmt = stmt.filter(Project.name.ilike("%" + name + "%"))
            q["name"] = name

        if street:
            stmt = stmt.filter(Project.street.ilike("%" + street + "%"))
            q["street"] = street

        if postcode:
            stmt = stmt.filter(Project.postcode.ilike("%" + postcode + "%"))
            q["postcode"] = postcode

        if city:
            stmt = stmt.filter(Project.city.ilike("%" + city + "%"))
            q["city"] = city

        if website:
            stmt = stmt.filter(Project.website.ilike("%" + website + "%"))
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
                    .group_by(Project)
                    .order_by(func.count(projects_stars.c.project_id).asc(), Project.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(projects_stars)
                    .group_by(Project)
                    .order_by(
                        func.count(projects_stars.c.project_id).desc(), Project.id
                    )
                )
        elif _sort == "comments":
            if _order == "asc":
                stmt = (
                    stmt.join(Project.comments)
                    .group_by(Project)
                    .order_by(func.count(Project.comments).asc())
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(Project.comments)
                    .group_by(Project)
                    .order_by(func.count(Project.comments).desc())
                )
        else:
            if _order == "asc":
                stmt = stmt.order_by(getattr(Project, _sort).asc(), Project.id)
            elif _order == "desc":
                stmt = stmt.order_by(getattr(Project, _sort).desc(), Project.id)

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "project_more",
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
            "form": form,
        }

    @view_config(
        route_name="project_comments",
        renderer="project_comments.mako",
        permission="view",
    )
    @view_config(
        route_name="project_more_comments",
        renderer="project_more.mako",
        permission="view",
    )
    def comments(self):
        project = self.request.context.project
        page = int(self.request.params.get("page", 1))
        stmt = (
            select(Comment)
            .filter(Comment.project_id == project.id)
            .order_by(Comment.created_at.desc())
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "project_more_comments",
            project_id=project.id,
            slug=project.slug,
            _query={"page": page + 1},
        )
        return {
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
        subdivision = self.request.params.getall("subdivision")
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
            stmt = stmt.filter(Project.name.ilike("%" + name + "%"))
            q["name"] = name

        if street:
            stmt = stmt.filter(Project.street.ilike("%" + street + "%"))
            q["street"] = street

        if postcode:
            stmt = stmt.filter(Project.postcode.ilike("%" + postcode + "%"))
            q["postcode"] = postcode

        if city:
            stmt = stmt.filter(Project.city.ilike("%" + city + "%"))
            q["city"] = city

        if website:
            stmt = stmt.filter(Project.website.ilike("%" + website + "%"))
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
                    .group_by(Project)
                    .order_by(func.count(projects_stars.c.project_id).asc(), Project.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(projects_stars)
                    .group_by(Project)
                    .order_by(
                        func.count(projects_stars.c.project_id).desc(), Project.id
                    )
                )
        else:
            if _order == "asc":
                stmt = stmt.order_by(getattr(Project, _sort).asc(), Project.id)
            elif _order == "desc":
                stmt = stmt.order_by(getattr(Project, _sort).desc(), Project.id)

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
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
            stmt = stmt.filter(Project.name.ilike("%" + name + "%"))

        if street:
            stmt = stmt.filter(Project.street.ilike("%" + street + "%"))

        if postcode:
            stmt = stmt.filter(Project.postcode.ilike("%" + postcode + "%"))

        if city:
            stmt = stmt.filter(Project.city.ilike("%" + city + "%"))

        if website:
            stmt = stmt.filter(Project.website.ilike("%" + website + "%"))

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
        project = self.request.context.project
        stages = dict(STAGES)
        countries = dict(select_countries())
        company_roles = dict(COMPANY_ROLES)
        delivery_methods = dict(PROJECT_DELIVERY_METHODS)

        return {
            "project": project,
            "stages": stages,
            "countries": countries,
            "company_roles": company_roles,
            "delivery_methods": delivery_methods,
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
        project = self.request.context.project
        page = int(self.request.params.get("page", 1))
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        colors = dict(COLORS)
        statuses = dict(STATUS)
        stages = dict(STAGES)
        project_delivery_methods = dict(PROJECT_DELIVERY_METHODS)
        q = {}

        stmt = (
            select(Project)
            .join(Tag, Project.tags)
            .filter(
                and_(
                    Tag.projects.any(Project.id == project.id),
                    Project.id != project.id,
                )
            )
            .group_by(Project)
            .order_by(func.count(Tag.projects.any(Project.id == project.id)).desc())
        )

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

        q["sort"] = _sort
        q["order"] = _order

        if _order == "asc":
            stmt = stmt.order_by(getattr(Project, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Project, _sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

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

        if self.request.method == "POST" and form.validate():
            project = Project(
                name=form.name.data,
                street=form.street.data,
                postcode=form.postcode.data,
                city=form.city.data,
                subdivision=form.subdivision.data,
                country=form.country.data,
                website=form.website.data,
                color=form.color.data,
                deadline=form.deadline.data,
                stage=form.stage.data,
                delivery_method=form.delivery_method.data,
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
            self.request.session.flash(_("success:Added to the database"))
            self.request.session.flash(_("info:Add tags and contacts"))
            log.info(_("The user %s has added a project") % self.request.identity.name)
            next_url = self.request.route_url(
                "project_view", project_id=project.id, slug=project.slug
            )
            return HTTPSeeOther(location=next_url)
        return {"heading": _("Add a project"), "form": form}

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
                subdivision=getattr(
                    pycountry.subdivisions.get(code=form.subdivision.data), "name", ""
                ),
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
        q = {}
        for fieldname, value in form.data.items():
            if value:
                q[fieldname] = value

        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "project_all",
                    _query=q,
                )
            )
        return {"heading": _("Find a project"), "form": form}

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
        project = self.request.context.project
        page = int(self.request.params.get("page", 1))
        user_roles = dict(USER_ROLES)
        stmt = (
            select(User)
            .join(projects_stars)
            .filter(project.id == projects_stars.c.project_id)
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "project_more_stars",
            project_id=project.id,
            slug=project.slug,
            _query={"page": page + 1},
        )
        return {
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
                    a = Activity(stage=form.stage.data, role=form.role.data)
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
        project = self.request.context.project
        selected_projects = self.request.identity.selected_projects

        if project in selected_projects:
            selected_projects.remove(project)
            return {"checked": False}
        else:
            selected_projects.append(project)
            return {"checked": True}

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
                select(Project).filter(Project.name.ilike("%" + name + "%"))
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
            tag = self.request.dbsession.execute(
                select(Tag).filter_by(name=form.name.data)
            ).scalar_one_or_none()

            if not tag:
                tag = Tag(name=form.name.data)
                tag.created_by = self.request.identity
            if tag not in project.tags:
                project.tags.append(tag)
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
            )
            contact.created_by = self.request.identity
            if contact not in project.contacts:
                project.contacts.append(contact)
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
