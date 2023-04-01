import datetime
import logging

from pyramid.httpexceptions import HTTPNotFound, HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import and_, func, select

from ..dropdown import Dd, Dropdown
from ..forms.project import ProjectForm, ProjectSearchForm
from ..forms.select import (
    COLORS,
    COMPANY_ROLES,
    USER_ROLES,
    COUNTRIES,
    ORDER_CRITERIA,
    SORT_CRITERIA_PROJECTS,
    STATUS,
    PROJECT_DELIVERY_METHODS,
    STAGES,
    SUBDIVISIONS,
)
from ..geo import location
from ..models import (
    Comment,
    CompaniesProjects,
    Company,
    Contact,
    Project,
    Tag,
    User,
    watched,
)
from ..paginator import get_paginator

log = logging.getLogger(__name__)


class ProjectView:
    def __init__(self, request):
        self.request = request

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
        subdivision = self.request.params.get("subdivision", None)
        country = self.request.params.get("country", None)
        link = self.request.params.get("link", None)
        color = self.request.params.get("color", None)
        deadline = self.request.params.get("deadline", None)
        stage = self.request.params.get("stage", None)
        delivery_method = self.request.params.get("delivery_method", None)
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        status = dict(STATUS)
        order_criteria = dict(ORDER_CRITERIA)
        sort_criteria = dict(SORT_CRITERIA_PROJECTS)
        subdivisions = dict(SUBDIVISIONS)
        countries = dict(COUNTRIES)
        colors = dict(COLORS)
        stages = dict(STAGES)
        projects_delivery_methods = dict(PROJECT_DELIVERY_METHODS)
        stmt = select(Project)

        if name:
            stmt = stmt.filter(Project.name.ilike("%" + name + "%"))

        if street:
            stmt = stmt.filter(Project.street.ilike("%" + street + "%"))

        if postcode:
            stmt = stmt.filter(Project.postcode.ilike("%" + postcode + "%"))

        if city:
            stmt = stmt.filter(Project.city.ilike("%" + city + "%"))

        if link:
            stmt = stmt.filter(Project.link.ilike("%" + link + "%"))

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
            deadline_dt = datetime.datetime.strptime(deadline, "%Y-%m-%d")
            stmt = stmt.filter(Project.deadline <= deadline_dt)

        if _filter == "in_progress":
            stmt = stmt.filter(Project.deadline > now.date())
        elif _filter == "completed":
            stmt = stmt.filter(Project.deadline < now.date())

        if _sort == "watched":
            if _order == "asc":
                stmt = (
                    stmt.join(watched)
                    .group_by(Project)
                    .order_by(func.count(watched.c.project_id).asc(), Project.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(watched)
                    .group_by(Project)
                    .order_by(func.count(watched.c.project_id).desc(), Project.id)
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

        search_query = {
            "name": name,
            "street": street,
            "postcode": postcode,
            "city": city,
            "subdivision": subdivision,
            "country": country,
            "link": link,
            "color": color,
            "deadline": deadline,
            "stage": stage,
            "delivery_method": delivery_method,
        }

        next_page = self.request.route_url(
            "project_more",
            _query={
                **search_query,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
                "page": page + 1,
            },
        )

        dd_filter = Dropdown(self.request, status, Dd.FILTER, _filter, _sort, _order)
        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, _filter, _sort, _order)
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, _filter, _sort, _order
        )

        # Recreate the search form to display the search criteria
        form = ProjectSearchForm(**search_query)

        return {
            "search_query": search_query,
            "form": form,
            "subdivisions": subdivisions,
            "countries": countries,
            "stages": stages,
            "project_delivery_methods": projects_delivery_methods,
            "colors": colors,
            "dd_filter": dd_filter,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
        }

    @view_config(
        route_name="project_count",
        renderer="json",
        permission="view",
    )
    def count(self):
        return self.request.dbsession.execute(
            select(func.count()).select_from(select(Project))
        ).scalar()

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
        subdivision = self.request.params.get("subdivision", None)
        country = self.request.params.get("country", None)
        link = self.request.params.get("link", None)
        color = self.request.params.get("color", None)
        deadline = self.request.params.get("deadline", None)
        stage = self.request.params.get("stage", None)
        delivery_method = self.request.params.get("delivery_method", None)

        search_query = {
            "name": name,
            "street": street,
            "postcode": postcode,
            "city": city,
            "subdivision": subdivision,
            "country": country,
            "link": link,
            "color": color,
            "deadline": deadline,
            "stage": stage,
            "delivery_method": delivery_method,
        }

        url = self.request.route_url("project_json", _query=search_query)
        return {"url": url, "search_query": search_query}

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
        link = self.request.params.get("link", None)
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

        if link:
            stmt = stmt.filter(Project.link.ilike("%" + link + "%"))

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
            deadline_dt = datetime.datetime.strptime(deadline, "%Y-%m-%d")
            stmt = stmt.filter(Project.deadline <= deadline_dt)

        projects = self.request.dbsession.execute(stmt).scalars()

        res = [
            {
                "id": project.id,
                "name": project.name,
                "street": project.street,
                "postcode": project.postcode,
                "city": project.city,
                "subdivision": project.subdivision,
                "country": project.country,
                "latitude": project.latitude,
                "longitude": project.longitude,
                "link": project.link,
                "color": project.color,
                "deadline": project.deadline.strftime("%Y-%m-%d"),
                "stage": project.stage,
                "delivery_method": project.delivery_method,
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
        route_name="project_count_watched",
        renderer="json",
        permission="view",
    )
    def count_watched(self):
        project = self.request.context.project
        return project.count_watched

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
        subdivisions = dict(SUBDIVISIONS)
        stages = dict(STAGES)
        countries = dict(COUNTRIES)
        company_roles = dict(COMPANY_ROLES)
        delivery_methods = dict(PROJECT_DELIVERY_METHODS)

        return {
            "project": project,
            "subdivisions": subdivisions,
            "stages": stages,
            "countries": countries,
            "company_roles": company_roles,
            "delivery_methods": delivery_methods,
            "title": project.name,
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
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)
        colors = dict(COLORS)
        subdivisions = dict(SUBDIVISIONS)

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

        if _filter:
            stmt = stmt.filter(Project.color == _filter)

        if _order == "asc":
            stmt = stmt.order_by(getattr(Project, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Project, _sort).desc())

        search_query = {}

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
                **search_query,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
                "page": page + 1,
            },
        )

        dd_filter = Dropdown(self.request, colors, Dd.FILTER, _filter, _sort, _order)

        return {
            "search_query": search_query,
            "project": project,
            "dd_filter": dd_filter,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "subdivisions": subdivisions,
            "title": project.name,
        }

    @view_config(
        route_name="project_add", renderer="project_form.mako", permission="edit"
    )
    def add(self):
        _ = self.request.translate
        form = ProjectForm(self.request.POST, request=self.request)
        subdivisions = dict(SUBDIVISIONS)
        countries = dict(COUNTRIES)

        if self.request.method == "POST" and form.validate():
            project = Project(
                name=form.name.data,
                street=form.street.data,
                postcode=form.city.data,
                city=form.city.data,
                subdivision=form.subdivision.data,
                country=form.country.data,
                link=form.link.data,
                color=form.color.data,
                deadline=form.deadline.data,
                stage=form.stage.data,
                delivery_method=form.delivery_method.data,
            )
            loc = location(
                street=form.street.data,
                city=form.city.data,
                subdivision=subdivisions.get(form.subdivision.data),
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
        subdivisions = dict(SUBDIVISIONS)
        countries = dict(COUNTRIES)

        if self.request.method == "POST" and form.validate():
            form.populate_obj(project)
            loc = location(
                street=form.street.data,
                city=form.city.data,
                subdivision=subdivisions.get(form.subdivision.data),
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
        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "project_all",
                    _query={
                        "name": form.name.data,
                        "street": form.street.data,
                        "postcode": form.postcode.data,
                        "city": form.city.data,
                        "subdivision": form.subdivision.data,
                        "country": form.country.data,
                        "link": form.link.data,
                        "color": form.color.data,
                        "deadline": form.deadline.data,
                        "stage": form.stage.data,
                        "delivery_method": form.delivery_method.data,
                    },
                )
            )
        return {"heading": _("Find a project"), "form": form}

    @view_config(
        route_name="project_watch",
        request_method="POST",
        renderer="string",
        permission="view",
    )
    def watch(self):
        project = self.request.context.project
        if project in self.request.identity.watched:
            self.request.identity.watched.remove(project)
            self.request.response.headers = {"HX-Trigger": "watchEvent"}
            return '<i class="bi bi-eye"></i>'
        else:
            self.request.identity.watched.append(project)
            self.request.response.headers = {"HX-Trigger": "watchEvent"}
            return '<i class="bi bi-eye-fill"></i>'

    @view_config(
        route_name="project_watched",
        renderer="project_watched.mako",
        permission="view",
    )
    @view_config(
        route_name="project_more_watched",
        renderer="user_more.mako",
        permission="view",
    )
    def watched(self):
        project = self.request.context.project
        page = int(self.request.params.get("page", 1))
        user_roles = dict(USER_ROLES)
        stmt = select(User).join(watched).filter(project.id == watched.c.project_id)
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "project_more_watched",
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
        }

    @view_config(
        route_name="project_add_company",
        renderer="company_assoc.mako",
        request_method="POST",
        permission="edit",
    )
    def add_company(self):
        _ = self.request.translate
        project = self.request.context.project
        name = self.request.POST.get("name")
        stage = self.request.POST.get("stage")
        role = self.request.POST.get("role")
        stages = dict(STAGES)
        company_roles = dict(COMPANY_ROLES)
        if name:
            company = self.request.dbsession.execute(
                select(Company).filter_by(name=name)
            ).scalar_one_or_none()

            if company:
                exist = self.request.dbsession.execute(
                    select(CompaniesProjects).filter_by(
                        company_id=company.id, project_id=project.id
                    )
                ).scalar_one_or_none()

                if not exist:
                    a = CompaniesProjects(stage=stage, role=role)
                    a.company = company
                    project.companies.append(a)
                    log.info(
                        _("The user %s added the company to the projekt")
                        % self.request.identity.name
                    )
                # If you want to use the id of a newly created object
                # in the middle of a transaction, you must call dbsession.flush()
                self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "projectCompanyEvent"}
        return {"project": project, "stages": stages, "company_roles": company_roles}

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
        renderer="tag_row_project.mako",
        request_method="POST",
        permission="edit",
    )
    def add_tag(self):
        _ = self.request.translate
        project = self.request.context.project
        name = self.request.POST.get("name")
        new_tag = None
        if name:
            tag = self.request.dbsession.execute(
                select(Tag).filter_by(name=name)
            ).scalar_one_or_none()
            if not tag:
                tag = Tag(name)
                tag.created_by = self.request.identity
            if tag not in project.tags:
                project.tags.append(tag)
                new_tag = tag
                log.info(
                    _("The user %s has added a tag to the project")
                    % self.request.identity.name
                )
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "tagEvent"}
        return {"project": project, "tag": new_tag}

    @view_config(
        route_name="project_add_contact",
        renderer="contact_row.mako",
        request_method="POST",
        permission="edit",
    )
    def add_contact(self):
        _ = self.request.translate
        project = self.request.context.project
        contact = None
        name = self.request.POST.get("name")
        role = self.request.POST.get("role")
        phone = self.request.POST.get("phone")
        email = self.request.POST.get("email")
        if name:
            contact = Contact(name, role, phone, email)
            contact.created_by = self.request.identity
            if contact not in project.contacts:
                project.contacts.append(contact)
                log.info(
                    _("The user %s has added a contact to the project")
                    % self.request.identity.name
                )
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "contactEvent"}
        return {"contact": contact}

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
