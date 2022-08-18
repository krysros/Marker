import datetime
import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
from sqlalchemy import select

from ..forms.project import ProjectForm

from ..forms.select import (
    STATES,
    DROPDOWN_ORDER,
    DROPDOWN_EXT_SORT,
    DROPDOWN_PROGRESS,
)

from ..models import (
    Company,
    Project,
)
from ..paginator import get_paginator

log = logging.getLogger(__name__)


class ProjectView(object):
    def __init__(self, request):
        self.request = request

    def _get_company(self, name):
        return self.request.dbsession.execute(
            select(Company).filter_by(name=name)
        ).scalar_one()

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
        dropdown_progress = dict(DROPDOWN_PROGRESS)
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
        return dict(
            filter=filter,
            sort=sort,
            order=order,
            dropdown_progress=dropdown_progress,
            dropdown_order = dropdown_order,
            dropdown_sort=dropdown_sort,
            states=states,
            paginator=paginator,
            next_page=next_page,
        )

    @view_config(
        route_name="project_view",
        renderer="project_view.mako",
        permission="view",
    )
    def view(self):
        project = self.request.context.project
        states = dict(STATES)
        return {"project": project, "title": project.name, "states": states}

    @view_config(
        route_name="project_add", renderer="project_form.mako", permission="edit"
    )
    def add(self):
        form = ProjectForm(self.request.POST)

        if self.request.method == 'POST' and form.validate():
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
            project.created_by = self.request.identity
            self.request.dbsession.add(project)
            self.request.session.flash("success:Dodano do bazy danych")
            log.info(
                f"Użytkownik {self.request.identity.name} dodał projekt {project.name}"
            )
            next_url = self.request.route_url("project_all")
            return HTTPSeeOther(location=next_url)

        return dict(
            heading="Dodaj projekt",
            form=form,
            companies=[],
        )

    @view_config(
        route_name="project_edit", renderer="project_form.mako", permission="edit"
    )
    def edit(self):
        project = self.request.context.project
        form = ProjectForm(self.request.POST, project)

        if self.request.method == 'POST' and form.validate():
            form.populate_obj(project)
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

        return dict(
            heading="Edytuj dane projektu",
            form=form,
        )

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
        return HTTPSeeOther(location=next_url)

    # @view_config(
    #     route_name="project_select",
    #     request_method="GET",
    #     renderer="json",
    # )
    # def select(self):
    #     term = self.request.params.get("term")
    #     items = self.request.dbsession.execute(
    #         select(Project).query.filter(
    #             Project.name.ilike("%" + term + "%")
    #         )
    #     ).scalars()
    #     data = [i.name for i in items]
    #     return data

    @view_config(
        route_name="project_search",
        renderer="project_search.mako",
        permission="view",
    )
    def search(self):
        states = dict(STATES)
        return {"states": states}

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
        city = self.request.params.get("city")
        state = self.request.params.get("state")
        page = int(self.request.params.get("page", 1))
        states = dict(STATES)
        stmt = (
            select(Project)
            .filter(Project.name.ilike("%" + name + "%"))
            .filter(Project.city.ilike("%" + city + "%"))
            .filter(Project.state.ilike("%" + state + "%"))
            .order_by(Project.name)
        )

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "project_results_more",
            _query={
                "name": name,
                "city": city,
                "state": state,
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