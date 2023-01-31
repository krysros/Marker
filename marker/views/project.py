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
    DROPDOWN_ORDER,
    DROPDOWN_SORT_PROJECTS,
    DROPDOWN_STATUS,
    PROJECT_DELIVERY_METHODS,
    STAGES,
    STATES,
)
from ..geo import location
from ..models import (
    Comment,
    CompaniesProjects,
    Company,
    Person,
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
        state = self.request.params.get("state", None)
        country = self.request.params.get("country", None)
        link = self.request.params.get("link", None)
        color = self.request.params.get("color", None)
        deadline = self.request.params.get("deadline", None)
        stage = self.request.params.get("stage", None)
        delivery_method = self.request.params.get("delivery_method", None)
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        dropdown_status = dict(DROPDOWN_STATUS)
        dropdown_order = dict(DROPDOWN_ORDER)
        dropdown_sort = dict(DROPDOWN_SORT_PROJECTS)
        states = dict(STATES)
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

        if state:
            stmt = stmt.filter(Project.state == state)

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

        if filter == "in_progress":
            stmt = stmt.filter(Project.deadline > now.date())
        elif filter == "completed":
            stmt = stmt.filter(Project.deadline < now.date())

        if sort == "watched":
            if order == "asc":
                stmt = (
                    stmt.join(watched)
                    .group_by(Project)
                    .order_by(func.count(watched.c.project_id).asc(), Project.id)
                )
            elif order == "desc":
                stmt = (
                    stmt.join(watched)
                    .group_by(Project)
                    .order_by(func.count(watched.c.project_id).desc(), Project.id)
                )
        else:
            if order == "asc":
                stmt = stmt.order_by(getattr(Project, sort).asc(), Project.id)
            elif order == "desc":
                stmt = stmt.order_by(getattr(Project, sort).desc(), Project.id)

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
            "state": state,
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
                "filter": filter,
                "sort": sort,
                "order": order,
                "page": page + 1,
            },
        )

        dd_filter = Dropdown(
            items=dropdown_status,
            typ=Dd.FILTER,
            _filter=filter,
            _sort=sort,
            _order=order,
        )
        dd_sort = Dropdown(
            items=dropdown_sort, typ=Dd.SORT, _filter=filter, _sort=sort, _order=order
        )
        dd_order = Dropdown(
            items=dropdown_order, typ=Dd.ORDER, _filter=filter, _sort=sort, _order=order
        )

        if any(x is not None for x in search_query.values()):
            heading = "Wyniki wyszukiwania"
        else:
            heading = ""

        form = ProjectSearchForm(**search_query)

        return {
            "search_query": search_query,
            "form": form,
            "states": states,
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
            "heading": heading,
        }

    @view_config(
        route_name="project_comments",
        renderer="project_comments.mako",
        permission="view",
    )
    @view_config(
        route_name="project_comments_more",
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
            "project_comments_more",
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
        route_name="project_companies",
        renderer="project_companies.mako",
        permission="view",
    )
    def companies(self):
        project = self.request.context.project
        stages = dict(STAGES)
        company_roles = dict(COMPANY_ROLES)
        return {
            "project": project,
            "stages": stages,
            "company_roles": company_roles,
            "title": project.name,
        }

    @view_config(
        route_name="project_persons",
        renderer="project_persons.mako",
        permission="view",
    )
    def persons(self):
        project = self.request.context.project
        return {
            "project": project,
            "title": project.name,
        }

    @view_config(
        route_name="project_tags",
        renderer="project_tags.mako",
        permission="view",
    )
    def tags(self):
        project = self.request.context.project
        return {
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
        state = self.request.params.get("state", None)
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
            "state": state,
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
        state = self.request.params.get("state", None)
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

        if state:
            stmt = stmt.filter(Project.state == state)

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
                "state": project.state,
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
        route_name="count_project_companies",
        renderer="json",
        permission="view",
    )
    def count_project_companies(self):
        project = self.request.context.project
        return project.count_companies

    @view_config(
        route_name="count_project_tags",
        renderer="json",
        permission="view",
    )
    def count_project_tags(self):
        project = self.request.context.project
        return project.count_tags

    @view_config(
        route_name="count_project_persons",
        renderer="json",
        permission="view",
    )
    def count_project_persons(self):
        project = self.request.context.project
        return project.count_persons

    @view_config(
        route_name="count_project_comments",
        renderer="json",
        permission="view",
    )
    def count_project_comments(self):
        project = self.request.context.project
        return project.count_comments

    @view_config(
        route_name="count_project_watched",
        renderer="json",
        permission="view",
    )
    def count_project_watched(self):
        project = self.request.context.project
        return project.count_watched

    @view_config(
        route_name="count_project_similar",
        renderer="json",
        permission="view",
    )
    def count_project_similar(self):
        project = self.request.context.project
        return project.count_similar

    @view_config(
        route_name="project_view",
        renderer="project_view.mako",
        permission="view",
    )
    def view(self):
        project = self.request.context.project
        states = dict(STATES)
        stages = dict(STAGES)
        countries = dict(COUNTRIES)
        delivery_methods = dict(PROJECT_DELIVERY_METHODS)

        return {
            "project": project,
            "states": states,
            "stages": stages,
            "countries": countries,
            "delivery_methods": delivery_methods,
            "title": project.name,
        }

    @view_config(
        route_name="project_similar",
        renderer="project_similar.mako",
        permission="view",
    )
    @view_config(
        route_name="project_similar_more",
        renderer="project_more.mako",
        permission="view",
    )
    def similar(self):
        project = self.request.context.project
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", None)
        order = self.request.params.get("order", None)
        colors = dict(COLORS)
        states = dict(STATES)

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

        if filter:
            stmt = stmt.filter(Project.color == filter)

        if order == "asc":
            stmt = stmt.order_by(getattr(Project, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Project, sort).desc())

        search_query = {}

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "project_similar_more",
            project_id=project.id,
            slug=project.slug,
            colors=colors,
            _query={
                **search_query,
                "filter": filter,
                "sort": sort,
                "order": order,
                "page": page + 1,
            },
        )

        dd_filter = Dropdown(
            items=colors, typ=Dd.FILTER, _filter=filter, _sort=sort, _order=order
        )

        return {
            "search_query": search_query,
            "project": project,
            "dd_filter": dd_filter,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "states": states,
            "title": project.name,
        }

    @view_config(
        route_name="project_add", renderer="project_form.mako", permission="edit"
    )
    def add(self):
        form = ProjectForm(self.request.POST, dbsession=self.request.dbsession)
        states = dict(STATES)
        countries = dict(COUNTRIES)

        if self.request.method == "POST" and form.validate():
            project = Project(
                name=form.name.data,
                street=form.street.data,
                postcode=form.city.data,
                city=form.city.data,
                state=form.state.data,
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
                state=states.get(form.state.data),
                country=countries.get(form.country.data),
                postalcode=form.postcode.data,
            )
            if loc is not None:
                project.latitude = loc["lat"]
                project.longitude = loc["lon"]

            project.created_by = self.request.identity
            self.request.dbsession.add(project)
            self.request.dbsession.flush()
            self.request.session.flash("info:Dodaj tagi i osoby do kontaktu")
            log.info(f"Użytkownik {self.request.identity.name} dodał projekt")
            next_url = self.request.route_url(
                "project_view", project_id=project.id, slug=project.slug
            )
            return HTTPSeeOther(location=next_url)
        return {"heading": "Dodaj projekt", "form": form}

    @view_config(
        route_name="project_edit", renderer="project_form.mako", permission="edit"
    )
    def edit(self):
        project = self.request.context.project
        form = ProjectForm(self.request.POST, project, dbsession=self.request.dbsession)
        states = dict(STATES)
        countries = dict(COUNTRIES)

        if self.request.method == "POST" and form.validate():
            form.populate_obj(project)
            loc = location(
                street=form.street.data,
                city=form.city.data,
                state=states.get(form.state.data),
                country=countries.get(form.country.data),
                postalcode=form.postcode.data,
            )
            if loc is not None:
                project.latitude = loc["lat"]
                project.longitude = loc["lon"]

            project.updated_by = self.request.identity
            self.request.session.flash("success:Zmiany zostały zapisane")
            next_url = self.request.route_url(
                "project_view",
                project_id=project.id,
                slug=project.slug,
            )
            log.info(f"Użytkownik {self.request.identity.name} zmienił dane projektu")
            return HTTPSeeOther(location=next_url)
        return {"heading": "Edytuj dane projektu", "form": form}

    @view_config(
        route_name="project_delete",
        request_method="POST",
        permission="edit",
    )
    def delete(self):
        project = self.request.context.project
        self.request.dbsession.delete(project)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(f"Użytkownik {self.request.identity.name} usunął projekt")
        next_url = self.request.route_url("home")
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="project_search",
        renderer="project_form.mako",
        permission="view",
    )
    def search(self):
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
                        "state": form.state.data,
                        "country": form.country.data,
                        "link": form.link.data,
                        "color": form.color.data,
                        "deadline": form.deadline.data,
                        "stage": form.stage.data,
                        "delivery_method": form.delivery_method.data,
                    },
                )
            )
        return {"heading": "Znajdź projekt", "form": form}

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
            self.request.response.headers = {"HX-Trigger": "watchedProjectEvent"}
            return '<i class="bi bi-eye"></i>'
        else:
            self.request.identity.watched.append(project)
            self.request.response.headers = {"HX-Trigger": "watchedProjectEvent"}
            return '<i class="bi bi-eye-fill"></i>'

    @view_config(
        route_name="project_watched",
        renderer="project_watched.mako",
        permission="view",
    )
    @view_config(
        route_name="project_watched_more",
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
            "project_watched_more",
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
        route_name="add_company_to_project",
        renderer="company_list_projects.mako",
        request_method="POST",
        permission="edit",
    )
    def add_company(self):
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

            exist = self.request.dbsession.execute(
                select(CompaniesProjects).filter_by(
                    company_id=company.id, project_id=project.id
                )
            ).scalar_one_or_none()

            if not exist:
                a = CompaniesProjects(stage=stage, role=role)
                a.company = company
                project.companies.append(a)
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "projectCompanyEvent"}
        return {"project": project, "stages": stages, "company_roles": company_roles}

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
        route_name="add_tag_to_project",
        renderer="tag_row_project.mako",
        request_method="POST",
        permission="edit",
    )
    def add_tag(self):
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
                    f"Użytkownik {self.request.identity.name} dodał tag do projektu"
                )
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "tagProjectEvent"}
        return {"project": project, "tag": new_tag}

    @view_config(
        route_name="add_person_to_project",
        renderer="person_row.mako",
        request_method="POST",
        permission="edit",
    )
    def add_person(self):
        project = self.request.context.project
        person = None
        name = self.request.POST.get("name")
        position = self.request.POST.get("position")
        phone = self.request.POST.get("phone")
        email = self.request.POST.get("email")
        if name:
            person = Person(name, position, phone, email)
            person.created_by = self.request.identity
            if person not in project.people:
                project.people.append(person)
                log.info(
                    f"Użytkownik {self.request.identity.name} dodał osobę do projektu"
                )
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "personProjectEvent"}
        return {"person": person}

    @view_config(
        route_name="unlink_tag_from_project",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def unlink_tag(self):
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
        log.info(f"Użytkownik {self.request.identity.name} odpiął tag od projektu")
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": "tagProjectEvent"}
        return ""
