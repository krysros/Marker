import datetime
import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
from sqlalchemy import select, func

from ..forms.project import (
    ProjectForm,
    ProjectSearchForm,
)

from ..forms.select import (
    COUNTRIES,
    STATES,
    STAGES,
    COLORS,
    PROJECT_DELIVERY_METHODS,
    DROPDOWN_ORDER,
    DROPDOWN_SORT_PROJECTS,
    DROPDOWN_STATUS,
)

from ..models import (
    Company,
    Project,
    User,
    companies_projects,
    watched,
)
from ..paginator import get_paginator
from ..geo import location

log = logging.getLogger(__name__)


class ProjectView(object):
    def __init__(self, request):
        self.request = request

    def count_companies(self, project):
        return self.request.dbsession.scalar(
            select(func.count())
            .select_from(Project)
            .join(companies_projects)
            .filter(project.id == companies_projects.c.project_id)
        )

    def count_watched(self, project):
        return self.request.dbsession.scalar(
            select(func.count())
            .select_from(User)
            .join(watched)
            .filter(project.id == watched.c.project_id)
        )

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
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        status = dict(DROPDOWN_STATUS)
        dropdown_order = dict(DROPDOWN_ORDER)
        dropdown_sort = dict(DROPDOWN_SORT_PROJECTS)
        states = dict(STATES)
        stmt = select(Project)

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

        if filter == "inprogress":
            stmt = stmt.filter(Project.deadline > now.date())
        elif filter == "completed":
            stmt = stmt.filter(Project.deadline < now.date())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "project_more",
            _query={
                "filter": filter,
                "sort": sort,
                "order": order,
                "page": page + 1,
            },
        )
        return {
            "filter": filter,
            "sort": sort,
            "order": order,
            "status": status,
            "states": states,
            "dropdown_order": dropdown_order,
            "dropdown_sort": dropdown_sort,
            "paginator": paginator,
            "next_page": next_page,
        }

    @view_config(
        route_name="project_companies",
        renderer="project_companies.mako",
        permission="view",
    )
    def companies(self):
        project = self.request.context.project
        return {
            "project": project,
            "c_companies": self.count_companies(project),
            "c_watched": self.count_watched(project),
        }

    @view_config(
        route_name="project_map",
        renderer="project_map.mako",
        permission="view",
    )
    def map(self):
        url = self.request.route_url("project_json")
        return {"url": url}

    @view_config(
        route_name="project_json",
        renderer="json",
        permission="view",
    )
    def project_json(self):
        query = select(Project)
        projects = self.request.dbsession.execute(query).scalars()
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
        return self.count_companies(project)

    @view_config(
        route_name="count_project_watched",
        renderer="json",
        permission="view",
    )
    def count_project_watched(self):
        project = self.request.context.project
        return self.count_watched(project)

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
        project_delivery_methods = dict(PROJECT_DELIVERY_METHODS)

        return {
            "project": project,
            "states": states,
            "stages": stages,
            "countries": countries,
            "project_delivery_methods": project_delivery_methods,
            "c_companies": self.count_companies(project),
            "c_watched": self.count_watched(project),
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
                project_delivery_method=form.project_delivery_method.data,
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
            self.request.session.flash("success:Dodano do bazy danych")
            log.info(f"Użytkownik {self.request.identity.name} dodał projekt")
            next_url = self.request.route_url("project_all")
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
                    "project_results",
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
                        "project_delivery_method": form.project_delivery_method.data,
                    },
                )
            )
        return {"heading": "Znajdź projekt", "form": form}

    @view_config(
        route_name="project_results",
        renderer="project_results.mako",
        permission="view",
    )
    @view_config(
        route_name="project_results_more",
        renderer="project_more.mako",
        permission="view",
    )
    def results(self):
        name = self.request.params.get("name")
        street = self.request.params.get("street")
        postcode = self.request.params.get("postcode")
        city = self.request.params.get("city")
        state = self.request.params.get("state")
        country = self.request.params.get("country")
        link = self.request.params.get("link")
        color = self.request.params.get("color")
        deadline = self.request.params.get("deadline")
        stage = self.request.params.get("stage")
        project_delivery_method = self.request.params.get("project_delivery_method")
        page = int(self.request.params.get("page", 1))
        colors = dict(COLORS)

        stmt = select(Project)
        stmt = stmt.filter(
            Project.name.ilike("%" + name + "%"),
            Project.street.ilike("%" + street + "%"),
            Project.postcode.ilike("%" + postcode + "%"),
            Project.city.ilike("%" + city + "%"),
            Project.link.ilike("%" + link + "%"),
        )

        if state:
            stmt = stmt.filter(Project.state == state)

        if country:
            stmt = stmt.filter(Project.country == country)

        if color:
            stmt = stmt.filter(Project.color == color)

        if stage:
            stmt = stmt.filter(Project.stage == stage)

        if project_delivery_method:
            stmt = stmt.filter(
                Project.project_delivery_method == project_delivery_method
            )

        if deadline:
            deadline = datetime.datetime.strptime(deadline, "%Y-%m-%d")
            stmt = stmt.filter(Project.deadline <= deadline)

        stmt = stmt.order_by(Project.name)

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "project_results_more",
            _query={
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
                "project_delivery_method": project_delivery_method,
                "page": page + 1,
            },
        )
        return {
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
        }

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
            "c_companies": self.count_companies(project),
            "c_watched": self.count_watched(project),
        }

    @view_config(
        route_name="add_company_to_project",
        renderer="company_list_project.mako",
        request_method="POST",
        permission="edit",
    )
    def add_company_to_project(self):
        project = self.request.context.project
        name = self.request.POST.get("name")
        if name:
            company = self.request.dbsession.execute(
                select(Company).filter_by(name=name)
            ).scalar_one_or_none()
            if company not in project.companies:
                project.companies.append(company)
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "projectCompanyEvent"}
        return {"project": project}

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
