import datetime
import logging

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import func, select

from ..dropdown import Dd, Dropdown
from ..export import export_companies_to_xlsx, export_projects_to_xlsx
from ..forms import UserForm, UserSearchForm
from ..forms.select import (
    COLORS,
    DROPDOWN_EXT_SORT,
    DROPDOWN_ORDER,
    DROPDOWN_SORT,
    DROPDOWN_SORT_COMPANIES,
    DROPDOWN_SORT_PROJECTS,
    DROPDOWN_STATUS,
    STATES,
    USER_ROLES,
)
from ..models import (
    Comment,
    Company,
    Person,
    Project,
    Tag,
    User,
    checked,
    recommended,
    watched,
)
from ..paginator import get_paginator

log = logging.getLogger(__name__)


class UserView:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="user_all", renderer="user_all.mako", permission="view")
    @view_config(route_name="user_more", renderer="user_more.mako", permission="view")
    def all(self):
        page = int(self.request.params.get("page", 1))
        username = self.request.params.get("username", None)
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        roles = dict(USER_ROLES)
        dropdown_sort = dict(DROPDOWN_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        stmt = select(User)

        if username:
            stmt = stmt.filter(User.name.ilike("%" + username + "%"))

        if filter:
            stmt = stmt.filter(User.role == filter)

        if order == "asc":
            stmt = stmt.order_by(getattr(User, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(User, sort).desc())

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        search_query = {"username": username}

        next_page = self.request.route_url(
            "user_more",
            _query={
                **search_query,
                "filter": filter,
                "sort": sort,
                "order": order,
                "page": page + 1,
            },
        )

        dd_filter = Dropdown(
            items=roles, typ=Dd.FILTER, _filter=filter, _sort=sort, _order=order
        )
        dd_sort = Dropdown(
            items=dropdown_sort, typ=Dd.SORT, _filter=filter, _sort=sort, _order=order
        )
        dd_order = Dropdown(
            items=dropdown_order, typ=Dd.ORDER, _filter=filter, _sort=sort, _order=order
        )

        return {
            "search_query": search_query,
            "roles": roles,
            "dd_filter": dd_filter,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
        }

    @view_config(route_name="user_view", renderer="user_view.mako", permission="view")
    def view(self):
        user = self.request.context.user
        return {
            "user": user,
            "title": user.fullname,
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
            "title": user.fullname,
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
        filter = self.request.params.get("filter", None)
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

        search_query = {}

        next_page = self.request.route_url(
            "user_tags_more",
            username=user.name,
            _query={
                **search_query,
                "filter": filter,
                "sort": sort,
                "order": order,
                "page": page + 1,
            },
        )

        dd_sort = Dropdown(
            items=dropdown_sort, typ=Dd.SORT, _filter=filter, _sort=sort, _order=order
        )
        dd_order = Dropdown(
            items=dropdown_order, typ=Dd.ORDER, _filter=filter, _sort=sort, _order=order
        )

        return {
            "search_query": search_query,
            "user": user,
            "paginator": paginator,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "next_page": next_page,
            "title": user.fullname,
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
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")
        dropdown_sort = dict(DROPDOWN_SORT_COMPANIES)
        dropdown_order = dict(DROPDOWN_ORDER)
        colors = dict(COLORS)
        states = dict(STATES)
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

        if filter:
            stmt = stmt.filter(Company.color == filter)

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        search_query = {}

        next_page = self.request.route_url(
            "user_companies_more",
            username=user.name,
            _query={
                **search_query,
                "page": page + 1,
                "filter": filter,
                "sort": sort,
                "order": order,
            },
        )

        dd_filter = Dropdown(
            items=colors, typ=Dd.FILTER, _filter=filter, _sort=sort, _order=order
        )
        dd_sort = Dropdown(
            items=dropdown_sort, typ=Dd.SORT, _filter=filter, _sort=sort, _order=order
        )
        dd_order = Dropdown(
            items=dropdown_order, typ=Dd.ORDER, _filter=filter, _sort=sort, _order=order
        )

        return {
            "search_query": search_query,
            "user": user,
            "dd_filter": dd_filter,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "colors": colors,
            "states": states,
            "paginator": paginator,
            "next_page": next_page,
            "title": user.fullname,
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
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        dropdown_status = dict(DROPDOWN_STATUS)
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

        if filter == "in_progress":
            stmt = stmt.filter(Project.deadline > now.date())
        elif filter == "completed":
            stmt = stmt.filter(Project.deadline < now.date())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        search_query = {}

        next_page = self.request.route_url(
            "user_projects_more",
            username=user.name,
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

        return {
            "search_query": search_query,
            "user": user,
            "states": states,
            "dd_filter": dd_filter,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "title": user.fullname,
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
        filter = self.request.params.get("filter", None)
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

        search_query = {}

        next_page = self.request.route_url(
            "user_persons_more",
            username=user.name,
            _query={
                **search_query,
                "filter": filter,
                "sort": sort,
                "order": order,
                "page": page + 1,
            },
        )

        dd_sort = Dropdown(
            items=dropdown_sort, typ=Dd.SORT, _filter=filter, _sort=sort, _order=order
        )
        dd_order = Dropdown(
            items=dropdown_order, typ=Dd.ORDER, _filter=filter, _sort=sort, _order=order
        )

        return {
            "search_query": search_query,
            "user": user,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "title": user.fullname,
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
                    "user_all", _query={"username": form.name.data}
                )
            )
        return {"heading": "Znajdź użytkownika", "form": form}

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
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")
        dropdown_sort = dict(DROPDOWN_EXT_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        colors = dict(COLORS)
        states = dict(STATES)
        stmt = select(Company).join(checked).filter(user.id == checked.c.user_id)

        if filter:
            stmt = stmt.filter(Company.color == filter)

        if order == "asc":
            stmt = stmt.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Company, sort).desc())

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        search_query = {}

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_checked_more",
            username=user.name,
            _query={
                **search_query,
                "page": page + 1,
                "filter": filter,
                "sort": sort,
                "order": order,
            },
        )

        dd_filter = Dropdown(
            items=colors, typ=Dd.FILTER, _filter=filter, _sort=sort, _order=order
        )
        dd_sort = Dropdown(
            items=dropdown_sort, typ=Dd.SORT, _filter=filter, _sort=sort, _order=order
        )
        dd_order = Dropdown(
            items=dropdown_order, typ=Dd.ORDER, _filter=filter, _sort=sort, _order=order
        )

        return {
            "search_query": search_query,
            "user": user,
            "dd_filter": dd_filter,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "states": states,
            "counter": counter,
        }

    @view_config(
        route_name="user_checked_export",
        permission="view",
    )
    def export_checked(self):
        user = self.request.context.user
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")

        stmt = select(Company).join(checked).filter(user.id == checked.c.user_id)

        if order == "asc":
            stmt = stmt.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Company, sort).desc())

        companies = self.request.dbsession.execute(stmt).scalars()
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
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")
        dropdown_sort = dict(DROPDOWN_EXT_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        colors = dict(COLORS)
        states = dict(STATES)

        stmt = (
            select(Company).join(recommended).filter(user.id == recommended.c.user_id)
        )

        if filter:
            stmt = stmt.filter(Company.color == filter)

        if order == "asc":
            stmt = stmt.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Company, sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        search_query = {}

        next_page = self.request.route_url(
            "user_recommended_more",
            username=user.name,
            _query={
                **search_query,
                "page": page + 1,
                "filter": filter,
                "sort": sort,
                "order": order,
            },
        )

        dd_filter = Dropdown(
            items=colors, typ=Dd.FILTER, _filter=filter, _sort=sort, _order=order
        )
        dd_sort = Dropdown(
            items=dropdown_sort, typ=Dd.SORT, _filter=filter, _sort=sort, _order=order
        )
        dd_order = Dropdown(
            items=dropdown_order, typ=Dd.ORDER, _filter=filter, _sort=sort, _order=order
        )

        return {
            "search_query": search_query,
            "user": user,
            "dd_filter": dd_filter,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "states": states,
            "counter": counter,
        }

    @view_config(
        route_name="user_recommended_export",
        permission="view",
    )
    def export_recommended(self):
        user = self.request.context.user
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")

        stmt = (
            select(Company).join(recommended).filter(user.id == recommended.c.user_id)
        )

        if order == "asc":
            stmt = stmt.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Company, sort).desc())

        companies = self.request.dbsession.execute(stmt).scalars()
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
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "asc")
        dropdown_status = dict(DROPDOWN_STATUS)
        dropdown_sort = dict(DROPDOWN_EXT_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        states = dict(STATES)
        now = datetime.datetime.now()

        stmt = select(Project).join(watched).filter(user.id == watched.c.user_id)

        if filter == "in_progress":
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

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        search_query = {}

        next_page = self.request.route_url(
            "user_watched_more",
            username=user.name,
            _query={
                **search_query,
                "page": page + 1,
                "filter": filter,
                "sort": sort,
                "order": order,
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

        return {
            "search_query": search_query,
            "user": user,
            "dd_filter": dd_filter,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "states": states,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
        }

    @view_config(
        route_name="user_watched_export",
        permission="view",
    )
    def export_watched(self):
        user = self.request.context.user
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "asc")
        now = datetime.datetime.now()

        stmt = select(Project).join(watched).filter(user.id == watched.c.user_id)

        if filter == "in_progress":
            stmt = stmt.filter(Project.deadline > now.date())
        elif filter == "completed":
            stmt = stmt.filter(Project.deadline < now.date())

        if order == "asc":
            stmt = stmt.order_by(getattr(Project, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Project, sort).desc())

        projects = self.request.dbsession.execute(stmt).scalars()
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
