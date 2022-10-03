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
    STATES,
    STAGES,
    PROJECT_DELIVERY_METHODS,
    DROPDOWN_ORDER,
    DROPDOWN_EXT_SORT,
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
        dropdown_status = dict(DROPDOWN_STATUS)
        dropdown_order = dict(DROPDOWN_ORDER)
        dropdown_sort = dict(DROPDOWN_EXT_SORT)
        states = dict(STATES)
        stmt = select(Project)

        if filter == "inprogress":
            stmt = stmt.filter(Project.deadline > now.date())
        elif filter == "completed":
            stmt = stmt.filter(Project.deadline < now.date())

        if order == "asc":
            stmt = stmt.order_by(getattr(Project, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Project, sort).desc())

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
            "dropdown_status": dropdown_status,
            "dropdown_order": dropdown_order,
            "dropdown_sort": dropdown_sort,
            "states": states,
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
        route_name="project_view",
        renderer="project_view.mako",
        permission="view",
    )
    def view(self):
        project = self.request.context.project
        states = dict(STATES)
        stages = dict(STAGES)
        project_delivery_methods = dict(PROJECT_DELIVERY_METHODS)

        return {
            "project": project,
            "states": states,
            "stages": stages,
            "project_delivery_methods": project_delivery_methods,
            "c_companies": self.count_companies(project),
            "c_watched": self.count_watched(project),
        }

    @view_config(
        route_name="project_add", renderer="project_form.mako", permission="edit"
    )
    def add(self):
        form = ProjectForm(self.request.POST)

        if self.request.method == "POST" and form.validate():
            project = Project(
                name=form.name.data,
                street=form.street.data,
                postcode=form.city.data,
                city=form.city.data,
                state=form.state.data,
                link=form.link.data,
                deadline=form.deadline.data,
                stage=form.stage.data,
                project_delivery_method=form.project_delivery_method.data,
            )
            loc = location(
                street=form.street.data,
                city=form.city.data,
                state=form.state.data,
                postalcode=form.postcode.data,
            )
            if loc is not None:
                project.latitude = loc["lat"]
                project.longitude = loc["lon"]

            project.created_by = self.request.identity
            self.request.dbsession.add(project)
            self.request.session.flash("success:Dodano do bazy danych")
            log.info(
                f"Użytkownik {self.request.identity.name} dodał projekt {project.name}"
            )
            next_url = self.request.route_url("project_all")
            return HTTPSeeOther(location=next_url)
        return {"heading": "Dodaj projekt", "form": form}

    @view_config(
        route_name="project_edit", renderer="project_form.mako", permission="edit"
    )
    def edit(self):
        project = self.request.context.project
        form = ProjectForm(self.request.POST, project)

        if self.request.method == "POST" and form.validate():
            form.populate_obj(project)
            loc = location(
                street=form.street.data,
                city=form.city.data,
                state=form.state.data,
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
            log.info(
                f"Użytkownik {self.request.identity.name} zmienił dane projektu {project.name}"
            )
            return HTTPSeeOther(location=next_url)
        return {"heading": "Edytuj dane projektu", "form": form}

    @view_config(
        route_name="project_delete",
        request_method="POST",
        permission="edit",
    )
    def delete(self):
        project = self.request.context.project
        project_name = project.name
        self.request.dbsession.delete(project)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(
            f"Użytkownik {self.request.identity.name} usunął projekt {project_name}"
        )
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
                        "link": form.link.data,
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
        link = self.request.params.get("link")
        deadline = self.request.params.get("deadline")
        stage = self.request.params.get("stage")
        project_delivery_method = self.request.params.get("project_delivery_method")
        page = int(self.request.params.get("page", 1))
        states = dict(STATES)
        stmt = (
            select(Project)
            .filter(Project.name.ilike("%" + name + "%"))
            .filter(Project.street.ilike("%" + street + "%"))
            .filter(Project.postcode.ilike("%" + postcode + "%"))
            .filter(Project.city.ilike("%" + city + "%"))
            .filter(Project.state.ilike("%" + state + "%"))
            .filter(Project.link.ilike("%" + link + "%"))
            .filter(Project.stage.ilike("%" + stage + "%"))
            .filter(
                Project.project_delivery_method.ilike(
                    "%" + project_delivery_method + "%"
                )
            )
        )
        if deadline:
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
                "link": link,
                "deadline": deadline,
                "stage": stage,
                "project_delivery_method": project_delivery_method,
                "page": page + 1,
            },
        )
        return {
            "paginator": paginator,
            "next_page": next_page,
            "states": states,
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
            return '<i class="bi bi-eye"></i>'
        else:
            self.request.identity.watched.append(project)
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
        route_name="add_company",
        renderer="company_list.mako",
        request_method="POST",
        permission="edit",
    )
    def add_company(self):
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
