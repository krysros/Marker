import logging
import datetime
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther, HTTPSeeOther

from sqlalchemy import (
    select,
    func,
)

from ..models import (
    User,
    checked,
    recommended,
    watched,
    Tag,
    Company,
    Comment,
    Project,
    Person,
)
from ..forms import (
    UserForm,
    UserSearchForm,
)
from ..paginator import get_paginator
from ..export import (
    export_companies_to_xlsx,
    export_projects_to_xlsx,
)
from ..forms.select import (
    ROLES,
    STATES,
    COLORS,
    DROPDOWN_SORT,
    DROPDOWN_EXT_SORT,
    DROPDOWN_STATUS,
    DROPDOWN_SORT_COMPANIES,
    DROPDOWN_SORT_PROJECTS,
    DROPDOWN_ORDER,
)

log = logging.getLogger(__name__)


class UserView(object):
    def __init__(self, request):
        self.request = request

    def count_companies(self, user):
        return self.request.dbsession.scalar(
            select(func.count()).select_from(Company).filter(Company.created_by == user)
        )

    def count_projects(self, user):
        return self.request.dbsession.scalar(
            select(func.count()).select_from(Project).filter(Project.created_by == user)
        )

    def count_tags(self, user):
        return self.request.dbsession.scalar(
            select(func.count()).select_from(Tag).filter(Tag.created_by == user)
        )

    def count_persons(self, user):
        return self.request.dbsession.scalar(
            select(func.count()).select_from(Person).filter(Person.created_by == user)
        )

    def count_comments(self, user):
        return self.request.dbsession.scalar(
            select(func.count()).select_from(Comment).filter(Comment.created_by == user)
        )

    @view_config(route_name="user_all", renderer="user_all.mako", permission="view")
    @view_config(route_name="user_more", renderer="user_more.mako", permission="view")
    def all(self):
        page = int(self.request.params.get("page", 1))
        role = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        roles = dict(ROLES)
        dropdown_sort = dict(DROPDOWN_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        stmt = select(User)

        if role in list(roles):
            stmt = stmt.filter(User.role == role)

        if order == "asc":
            stmt = stmt.order_by(getattr(User, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(User, sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_more",
            _query={
                "filter": role,
                "sort": sort,
                "order": order,
                "page": page + 1,
            },
        )
        return {
            "roles": roles,
            "dropdown_sort": dropdown_sort,
            "dropdown_order": dropdown_order,
            "filter": role,
            "sort": sort,
            "order": order,
            "paginator": paginator,
            "next_page": next_page,
        }

    @view_config(route_name="user_view", renderer="user_view.mako", permission="view")
    def view(self):
        user = self.request.context.user
        return {
            "user": user,
            "c_companies": self.count_companies(user),
            "c_projects": self.count_projects(user),
            "c_tags": self.count_tags(user),
            "c_persons": self.count_persons(user),
            "c_comments": self.count_comments(user),
        }

    @view_config(
        route_name="user_comments",
        renderer="user_comments.mako",
        permission="view",
    )
    @view_config(
        route_name="user_comments_more",
        renderer="comment_more.mako",
        permission="view",
    )
    def comments(self):
        page = int(self.request.params.get("page", 1))
        user = self.request.context.user
        stmt = (
            select(Comment)
            .filter(Comment.created_by == user)
            .order_by(Comment.created_at.desc())
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_comments_more",
            username=user.name,
            _query={"page": page + 1},
        )
        return {
            "user": user,
            "paginator": paginator,
            "next_page": next_page,
            "c_companies": self.count_companies(user),
            "c_projects": self.count_projects(user),
            "c_tags": self.count_tags(user),
            "c_persons": self.count_persons(user),
            "c_comments": self.count_comments(user),
        }

    @view_config(
        route_name="user_tags",
        renderer="user_tags.mako",
        permission="view",
    )
    @view_config(
        route_name="user_tags_more",
        renderer="tag_more.mako",
        permission="view",
    )
    def tags(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        dropdown_sort = dict(DROPDOWN_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        stmt = select(Tag).filter(Tag.created_by == user)

        if order == "asc":
            stmt = stmt.order_by(getattr(Tag, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Tag, sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_tags_more",
            username=user.name,
            _query={"filter": filter, "sort": sort, "order": order, "page": page + 1},
        )
        return {
            "user": user,
            "paginator": paginator,
            "filter": filter,
            "sort": sort,
            "order": order,
            "dropdown_sort": dropdown_sort,
            "dropdown_order": dropdown_order,
            "next_page": next_page,
            "c_companies": self.count_companies(user),
            "c_projects": self.count_projects(user),
            "c_tags": self.count_tags(user),
            "c_persons": self.count_persons(user),
            "c_comments": self.count_comments(user),
        }

    @view_config(
        route_name="user_companies",
        renderer="user_companies.mako",
        permission="view",
    )
    @view_config(
        route_name="user_companies_more",
        renderer="company_more.mako",
        permission="view",
    )
    def companies(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")
        dropdown_sort = dict(DROPDOWN_SORT_COMPANIES)
        dropdown_order = dict(DROPDOWN_ORDER)
        colors = dict(COLORS)
        stmt = select(Company).filter(Company.created_by == user)

        if sort == "recommended":
            if order == "asc":
                stmt = (
                    stmt.join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).asc(), Company.id)
                )
            elif order == "desc":
                stmt = (
                    stmt.join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).desc(), Company.id)
                )
        else:
            if order == "asc":
                stmt = stmt.order_by(getattr(Company, sort).asc(), Company.id)
            elif order == "desc":
                stmt = stmt.order_by(getattr(Company, sort).desc(), Company.id)

        if filter in list(colors):
            stmt = stmt.filter(Company.color == filter)

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_companies_more",
            username=user.name,
            _query={"page": page + 1, "filter": filter, "sort": sort, "order": order},
        )
        return {
            "user": user,
            "sort": sort,
            "order": order,
            "filter": filter,
            "colors": colors,
            "paginator": paginator,
            "next_page": next_page,
            "dropdown_sort": dropdown_sort,
            "dropdown_order": dropdown_order,
            "c_companies": self.count_companies(user),
            "c_projects": self.count_projects(user),
            "c_tags": self.count_tags(user),
            "c_persons": self.count_persons(user),
            "c_comments": self.count_comments(user),
        }

    @view_config(
        route_name="user_projects",
        renderer="user_projects.mako",
        permission="view",
    )
    @view_config(
        route_name="user_projects_more",
        renderer="project_more.mako",
        permission="view",
    )
    def projects(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        status = dict(DROPDOWN_STATUS)
        dropdown_order = dict(DROPDOWN_ORDER)
        dropdown_sort = dict(DROPDOWN_SORT_PROJECTS)
        states = dict(STATES)
        stmt = select(Project).filter(Project.created_by == user)

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
            "user_projects_more",
            username=user.name,
            _query={
                "filter": filter,
                "sort": sort,
                "order": order,
                "page": page + 1,
            },
        )
        return {
            "user": user,
            "states": states,
            "filter": filter,
            "sort": sort,
            "order": order,
            "status": status,
            "dropdown_order": dropdown_order,
            "dropdown_sort": dropdown_sort,
            "paginator": paginator,
            "next_page": next_page,
            "c_companies": self.count_companies(user),
            "c_projects": self.count_projects(user),
            "c_tags": self.count_tags(user),
            "c_persons": self.count_persons(user),
            "c_comments": self.count_comments(user),
        }

    @view_config(
        route_name="user_persons",
        renderer="user_persons.mako",
        permission="view",
    )
    @view_config(
        route_name="user_persons_more",
        renderer="person_more.mako",
        permission="view",
    )
    def persons(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        dropdown_sort = dict(DROPDOWN_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        stmt = select(Person).filter(Person.created_by == user)

        if order == "asc":
            stmt = stmt.order_by(getattr(Person, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Person, sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_persons_more",
            username=user.name,
            _query={"filter": filter, "sort": sort, "order": order, "page": page + 1},
        )
        return {
            "user": user,
            "filter": filter,
            "sort": sort,
            "order": order,
            "dropdown_sort": dropdown_sort,
            "dropdown_order": dropdown_order,
            "paginator": paginator,
            "next_page": next_page,
            "c_companies": self.count_companies(user),
            "c_projects": self.count_projects(user),
            "c_tags": self.count_tags(user),
            "c_persons": self.count_persons(user),
            "c_comments": self.count_comments(user),
        }

    @view_config(route_name="user_add", renderer="user_form.mako", permission="admin")
    def add(self):
        form = UserForm(self.request.POST, dbsession=self.request.dbsession)

        if self.request.method == "POST" and form.validate():
            user = User(
                name=form.name.data,
                fullname=form.fullname.data,
                email=form.email.data,
                role=form.role.data,
                password=form.password.data,
            )
            self.request.dbsession.add(user)
            self.request.session.flash("success:Dodano do bazy danych")
            log.info(f"Użytkownik {self.request.identity.name} dodał użytkownika")
            next_url = self.request.route_url("user_all")
            return HTTPSeeOther(location=next_url)

        return {"heading": "Dodaj użytkownika", "form": form}

    @view_config(route_name="user_edit", renderer="user_form.mako", permission="admin")
    def edit(self):
        user = self.request.context.user
        form = UserForm(
            self.request.POST,
            user,
            dbsession=self.request.dbsession,
            username=user.name,
        )
        if self.request.method == "POST" and form.validate():
            form.populate_obj(user)
            self.request.session.flash("success:Zmiany zostały zapisane")
            log.info(
                f"Użytkownik {self.request.identity.name} zmienił dane użytkownika"
            )
            next_url = self.request.route_url("user_all")
            return HTTPSeeOther(location=next_url)
        return {"heading": "Edytuj dane użytkownika", "form": form}

    @view_config(route_name="user_delete", request_method="POST", permission="admin")
    def delete(self):
        user = self.request.context.user
        user_username = user.name
        self.request.dbsession.delete(user)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(f"Użytkownik {self.request.identity.name} usunął użytkownika")
        next_url = self.request.route_url("home")
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="user_search",
        renderer="basic_form.mako",
        permission="view",
    )
    def search(self):
        form = UserSearchForm(self.request.POST)
        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "user_results", _query={"username": form.name.data}
                )
            )
        return {"heading": "Znajdź użytkownika", "form": form}

    @view_config(
        route_name="user_results",
        renderer="user_results.mako",
        permission="view",
    )
    @view_config(
        route_name="user_results_more",
        renderer="user_more.mako",
        permission="view",
    )
    def results(self):
        username = self.request.params.get("username")
        page = int(self.request.params.get("page", 1))
        stmt = (
            select(User)
            .filter(User.name.ilike("%" + username + "%"))
            .order_by(User.name)
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_more", _query={"username": username, "page": page + 1}
        )
        return {"paginator": paginator, "next_page": next_page}

    @view_config(
        route_name="user_checked",
        renderer="user_checked.mako",
        permission="view",
    )
    @view_config(
        route_name="user_checked_more",
        renderer="company_more.mako",
        permission="view",
    )
    def checked(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")
        dropdown_sort = dict(DROPDOWN_EXT_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        colors = dict(COLORS)
        stmt = select(Company).join(checked).filter(user.id == checked.c.user_id)

        if order == "asc":
            stmt = stmt.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Company, sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_checked_more",
            username=user.name,
            _query={"page": page + 1, "sort": sort, "order": order},
        )

        return {
            "user": user,
            "filter": filter,
            "sort": sort,
            "order": order,
            "dropdown_sort": dropdown_sort,
            "dropdown_order": dropdown_order,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
        }

    @view_config(
        route_name="user_checked_export",
        permission="view",
    )
    def export_checked(self):
        user = self.request.context.user
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")

        query = select(Company).join(checked).filter(user.id == checked.c.user_id)

        if order == "asc":
            query = query.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            query = query.order_by(getattr(Company, sort).desc())

        companies = self.request.dbsession.execute(query).scalars()
        response = export_companies_to_xlsx(companies)
        log.info(
            f"Użytkownik {self.request.identity.name} eksportował dane zaznaczonych firm"
        )
        return response

    @view_config(
        route_name="user_checked_clear",
        request_method="POST",
        permission="view",
    )
    def clear_checked(self):
        user = self.request.context.user
        user.checked = []
        log.info(f"Użytkownik {self.request.identity.name} wyczyścił zaznaczone firmy")
        next_url = self.request.route_url("user_checked", username=user.name)
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="user_recommended",
        renderer="user_recommended.mako",
        permission="view",
    )
    @view_config(
        route_name="user_recommended_more",
        renderer="company_more.mako",
        permission="view",
    )
    def recommended(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")
        dropdown_sort = dict(DROPDOWN_EXT_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        colors = dict(COLORS)

        stmt = (
            select(Company).join(recommended).filter(user.id == recommended.c.user_id)
        )

        if order == "asc":
            stmt = stmt.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Company, sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_recommended_more",
            username=user.name,
            _query={"page": page + 1, "sort": sort, "order": order},
        )

        return {
            "user": user,
            "filter": filter,
            "sort": sort,
            "order": order,
            "dropdown_sort": dropdown_sort,
            "dropdown_order": dropdown_order,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
        }

    @view_config(
        route_name="user_recommended_export",
        permission="view",
    )
    def export_recommended(self):
        user = self.request.context.user
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")

        query = (
            select(Company).join(recommended).filter(user.id == recommended.c.user_id)
        )

        if order == "asc":
            query = query.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            query = query.order_by(getattr(Company, sort).desc())

        companies = self.request.dbsession.execute(query).scalars()
        response = export_companies_to_xlsx(companies)
        log.info(
            f"Użytkownik {self.request.identity.name} eksportował dane rekomendowanych firm"
        )
        return response

    @view_config(
        route_name="user_recommended_clear",
        request_method="POST",
        permission="view",
    )
    def clear_recommended(self):
        user = self.request.context.user
        user.recommended = []
        log.info(f"Użytkownik {self.request.identity.name} wyczyścił rekomendacje")
        next_url = self.request.route_url("user_recommended", username=user.name)
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="user_watched",
        renderer="user_watched.mako",
        permission="view",
    )
    @view_config(
        route_name="user_watched_more",
        renderer="project_more.mako",
        permission="view",
    )
    def watched(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "asc")
        dropdown_sort = dict(DROPDOWN_EXT_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        status = dict(DROPDOWN_STATUS)
        states = dict(STATES)
        now = datetime.datetime.now()

        stmt = select(Project).join(watched).filter(user.id == watched.c.user_id)

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
            "user_watched_more",
            username=user.name,
            _query={
                "page": page + 1,
                "filter": filter,
                "sort": sort,
                "order": order,
            },
        )

        return {
            "user": user,
            "filter": filter,
            "sort": sort,
            "order": order,
            "dropdown_sort": dropdown_sort,
            "dropdown_order": dropdown_order,
            "status": status,
            "states": states,
            "paginator": paginator,
            "next_page": next_page,
        }

    @view_config(
        route_name="user_watched_export",
        permission="view",
    )
    def export_watched(self):
        user = self.request.context.user
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "asc")
        now = datetime.datetime.now()

        query = select(Project).join(watched).filter(user.id == watched.c.user_id)

        if filter == "inprogress":
            query = query.filter(Project.deadline > now.date())
        elif filter == "completed":
            query = query.filter(Project.deadline < now.date())

        if order == "asc":
            query = query.order_by(getattr(Project, sort).asc())
        elif order == "desc":
            query = query.order_by(getattr(Project, sort).desc())

        projects = self.request.dbsession.execute(query).scalars()
        response = export_projects_to_xlsx(projects)
        log.info(
            f"Użytkownik {self.request.identity.name} eksportował dane obserwowanych projektów"
        )
        return response

    @view_config(
        route_name="user_watched_clear",
        request_method="POST",
        permission="view",
    )
    def clear_watched(self):
        user = self.request.context.user
        user.watched = []
        log.info(
            f"Użytkownik {self.request.identity.name} wyczyścił obserwowane projekty"
        )
        next_url = self.request.route_url("user_watched", username=user.name)
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response
