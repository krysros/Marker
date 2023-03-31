import datetime
import logging

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import func, select

from ..dropdown import Dd, Dropdown
from ..export import (
    export_companies_to_xlsx,
    export_projects_to_xlsx,
    export_contacts_to_xlsx,
    export_tags_to_xlsx,
)
from ..forms import UserForm, UserSearchForm
from ..forms.select import (
    COLORS,
    SORT_CRITERIA_EXT,
    ORDER_CRITERIA,
    SORT_CRITERIA,
    SORT_CRITERIA_COMPANIES,
    SORT_CRITERIA_PROJECTS,
    STATUS,
    REGIONS,
    USER_ROLES,
)
from ..models import (
    Comment,
    Company,
    Contact,
    Project,
    Tag,
    User,
    selected_companies,
    selected_projects,
    selected_tags,
    selected_contacts,
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
        fullname = self.request.params.get("fullname", None)
        email = self.request.params.get("email", None)
        role = self.request.params.get("role", None)
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        roles = dict(USER_ROLES)
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        stmt = select(User)

        if username:
            stmt = stmt.filter(User.name.ilike("%" + username + "%"))

        if fullname:
            stmt = stmt.filter(User.fullname.ilike("%" + fullname + "%"))

        if email:
            stmt = stmt.filter(User.email.ilike("%" + email + "%"))

        if role:
            stmt = stmt.filter(User.role.ilike("%" + role + "%"))

        if _filter:
            stmt = stmt.filter(User.role == _filter)

        if _order == "asc":
            stmt = stmt.order_by(getattr(User, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(User, _sort).desc())

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        search_query = {
            "name": username,
            "fullname": fullname,
            "email": email,
            "role": role,
        }

        next_page = self.request.route_url(
            "user_more",
            _query={
                **search_query,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
                "page": page + 1,
            },
        )

        dd_filter = Dropdown(self.request, roles, Dd.FILTER, _filter, _sort, _order)
        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, _filter, _sort, _order)
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, _filter, _sort, _order
        )

        # Recreate the search form to display the search criteria
        form = UserSearchForm(**search_query)

        return {
            "search_query": search_query,
            "form": form,
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
        route_name="user_more_comments",
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
            "user_more_comments",
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
        route_name="user_more_tags",
        renderer="tag_more.mako",
        permission="view",
    )
    def tags(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        stmt = select(Tag).filter(Tag.created_by == user)

        if _order == "asc":
            stmt = stmt.order_by(getattr(Tag, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Tag, _sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        search_query = {}

        next_page = self.request.route_url(
            "user_more_tags",
            username=user.name,
            _query={
                **search_query,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
                "page": page + 1,
            },
        )

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, _filter, _sort, _order)
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, _filter, _sort, _order
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
        route_name="user_more_companies",
        renderer="company_more.mako",
        permission="view",
    )
    def companies(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "name")
        _order = self.request.params.get("order", "asc")
        sort_criteria = dict(SORT_CRITERIA_COMPANIES)
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        regions = dict(REGIONS)
        stmt = select(Company).filter(Company.created_by == user)

        if _sort == "recommended":
            if _order == "asc":
                stmt = (
                    stmt.join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).asc(), Company.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).desc(), Company.id)
                )
        else:
            if _order == "asc":
                stmt = stmt.order_by(getattr(Company, _sort).asc(), Company.id)
            elif _order == "desc":
                stmt = stmt.order_by(getattr(Company, _sort).desc(), Company.id)

        if _filter:
            stmt = stmt.filter(Company.color == _filter)

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        search_query = {}

        next_page = self.request.route_url(
            "user_more_companies",
            username=user.name,
            _query={
                **search_query,
                "page": page + 1,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
            },
        )

        dd_filter = Dropdown(self.request, colors, Dd.FILTER, _filter, _sort, _order)
        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, _filter, _sort, _order)
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, _filter, _sort, _order
        )

        return {
            "search_query": search_query,
            "user": user,
            "dd_filter": dd_filter,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "colors": colors,
            "regions": regions,
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
        route_name="user_more_projects",
        renderer="project_more.mako",
        permission="view",
    )
    def projects(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        status = dict(STATUS)
        order_criteria = dict(ORDER_CRITERIA)
        sort_criteria = dict(SORT_CRITERIA_PROJECTS)
        regions = dict(REGIONS)
        stmt = select(Project).filter(Project.created_by == user)

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

        if _filter == "in_progress":
            stmt = stmt.filter(Project.deadline > now.date())
        elif _filter == "completed":
            stmt = stmt.filter(Project.deadline < now.date())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        search_query = {}

        next_page = self.request.route_url(
            "user_more_projects",
            username=user.name,
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

        return {
            "search_query": search_query,
            "user": user,
            "regions": regions,
            "dd_filter": dd_filter,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "title": user.fullname,
        }

    @view_config(
        route_name="user_contacts",
        renderer="user_contacts.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_contacts",
        renderer="contact_more.mako",
        permission="view",
    )
    def contacts(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        stmt = select(Contact).filter(Contact.created_by == user)

        if _order == "asc":
            stmt = stmt.order_by(getattr(Contact, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Contact, _sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        search_query = {}

        next_page = self.request.route_url(
            "user_more_contacts",
            username=user.name,
            _query={
                **search_query,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
                "page": page + 1,
            },
        )

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, _filter, _sort, _order)
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, _filter, _sort, _order
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
        _ = self.request.translate
        form = UserForm(self.request.POST, request=self.request)
        if self.request.method == "POST" and form.validate():
            user = User(
                name=form.name.data,
                fullname=form.fullname.data,
                email=form.email.data,
                role=form.role.data,
                password=form.password.data,
            )
            self.request.dbsession.add(user)
            self.request.session.flash(_("success:Added to the database"))
            log.info(_("The user %s has added a user") % self.request.identity.name)
            next_url = self.request.route_url("user_all")
            return HTTPSeeOther(location=next_url)
        return {"heading": _("Add user"), "form": form}

    @view_config(route_name="user_edit", renderer="user_form.mako", permission="admin")
    def edit(self):
        _ = self.request.translate
        user = self.request.context.user
        form = UserForm(
            self.request.POST,
            user,
            dbsession=self.request.dbsession,
            username=user.name,
        )
        if self.request.method == "POST" and form.validate():
            form.populate_obj(user)
            self.request.session.flash(_("success:Changes have been saved"))
            log.info(_("The user %s has changed the user's data") % self.request.identity.name)
            next_url = self.request.route_url("user_all")
            return HTTPSeeOther(location=next_url)
        return {"heading": _("Edit user details"), "form": form}

    @view_config(route_name="user_delete", request_method="POST", permission="admin")
    def delete(self):
        _ = self.request.translate
        user = self.request.context.user
        self.request.dbsession.delete(user)
        self.request.session.flash(_("success:Removed from the database"))
        log.info(_("The user %s deleted the user") % self.request.identity.name)
        next_url = self.request.route_url("home")
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="user_search",
        renderer="user_search.mako",
        permission="view",
    )
    def search(self):
        _ = self.request.translate
        form = UserSearchForm(self.request.POST)
        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "user_all",
                    _query={
                        "username": form.name.data,
                        "fullname": form.fullname.data,
                        "email": form.email.data,
                        "role": form.role.data,
                    },
                )
            )
        return {"heading": _("Find a user"), "form": form}

    @view_config(
        route_name="user_selected_companies",
        renderer="user_selected_companies.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_selected_companies",
        renderer="company_more.mako",
        permission="view",
    )
    def selected_companies(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "name")
        _order = self.request.params.get("order", "asc")
        sort_criteria = dict(SORT_CRITERIA_EXT)
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        regions = dict(REGIONS)
        stmt = (
            select(Company)
            .join(selected_companies)
            .filter(user.id == selected_companies.c.user_id)
        )

        if _filter:
            stmt = stmt.filter(Company.color == _filter)

        if _order == "asc":
            stmt = stmt.order_by(getattr(Company, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Company, _sort).desc())

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
            "user_more_selected_companies",
            username=user.name,
            _query={
                **search_query,
                "page": page + 1,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
            },
        )

        dd_filter = Dropdown(self.request, colors, Dd.FILTER, _filter, _sort, _order)
        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, _filter, _sort, _order)
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, _filter, _sort, _order
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
            "regions": regions,
            "counter": counter,
        }

    @view_config(
        route_name="user_export_selected_companies",
        permission="view",
    )
    def export_selected_companies(self):
        _ = self.request.translate
        user = self.request.context.user
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")

        stmt = (
            select(Company)
            .join(selected_companies)
            .filter(user.id == selected_companies.c.user_id)
        )

        if order == "asc":
            stmt = stmt.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Company, sort).desc())

        companies = self.request.dbsession.execute(stmt).scalars()
        response = export_companies_to_xlsx(self.request, companies)
        log.info(_("The user %s exported the data of selected companies") % self.request.identity.name)
        return response

    @view_config(
        route_name="user_clear_selected_companies",
        request_method="POST",
        permission="view",
    )
    def clear_selected_companies(self):
        _ = self.request.translate
        user = self.request.context.user
        user.selected_companies = []
        log.info(_("The user %s cleared the selected companies") % self.request.identity.name)
        next_url = self.request.route_url("user_selected_companies", username=user.name)
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="user_selected_projects",
        renderer="user_selected_projects.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_selected_projects",
        renderer="project_more.mako",
        permission="view",
    )
    def selected_projects(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "name")
        _order = self.request.params.get("order", "asc")
        status = dict(STATUS)
        sort_criteria = dict(SORT_CRITERIA_PROJECTS)
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        regions = dict(REGIONS)
        now = datetime.datetime.now()
        stmt = (
            select(Project)
            .join(selected_projects)
            .filter(user.id == selected_projects.c.user_id)
        )

        if _filter == "in_progress":
            stmt = stmt.filter(Project.deadline > now.date())
        elif _filter == "completed":
            stmt = stmt.filter(Project.deadline < now.date())

        if _order == "asc":
            stmt = stmt.order_by(getattr(Project, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Project, _sort).desc())

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
            "user_more_selected_projects",
            username=user.name,
            _query={
                **search_query,
                "page": page + 1,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
            },
        )

        dd_filter = Dropdown(self.request, status, Dd.FILTER, _filter, _sort, _order)
        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, _filter, _sort, _order)
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, _filter, _sort, _order
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
            "regions": regions,
            "counter": counter,
        }

    @view_config(
        route_name="user_export_selected_projects",
        permission="view",
    )
    def export_selected_projects(self):
        _ = self.request.translate
        user = self.request.context.user
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")

        stmt = (
            select(Project)
            .join(selected_projects)
            .filter(user.id == selected_projects.c.user_id)
        )

        if order == "asc":
            stmt = stmt.order_by(getattr(Project, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Project, sort).desc())

        projects = self.request.dbsession.execute(stmt).scalars()
        response = export_projects_to_xlsx(self.request, projects)
        log.info(_("The user %s exported the data of selected projects") % self.request.identity.name)
        return response

    @view_config(
        route_name="user_clear_selected_projects",
        request_method="POST",
        permission="view",
    )
    def clear_selected_projects(self):
        _ = self.request.translate
        user = self.request.context.user
        user.selected_projects = []
        log.info(_("The user %s cleared the selected projects") % self.request.identity.name)
        next_url = self.request.route_url("user_selected_projects", username=user.name)
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="user_selected_tags",
        renderer="user_selected_tags.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_selected_tags",
        renderer="tag_more.mako",
        permission="view",
    )
    def selected_tags(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "name")
        _order = self.request.params.get("order", "asc")
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        stmt = (
            select(Tag).join(selected_tags).filter(user.id == selected_tags.c.user_id)
        )

        if _order == "asc":
            stmt = stmt.order_by(getattr(Tag, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Tag, _sort).desc())

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
            "user_more_selected_tags",
            username=user.name,
            _query={
                **search_query,
                "page": page + 1,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
            },
        )

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, _filter, _sort, _order)
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, _filter, _sort, _order
        )

        return {
            "search_query": search_query,
            "user": user,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
        }

    @view_config(
        route_name="user_export_selected_tags",
        permission="view",
    )
    def export_selected_tags(self):
        _ = self.request.translate
        user = self.request.context.user
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")

        stmt = (
            select(Tag).join(selected_tags).filter(user.id == selected_tags.c.user_id)
        )

        if order == "asc":
            stmt = stmt.order_by(getattr(Tag, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Tag, sort).desc())

        tags = self.request.dbsession.execute(stmt).scalars()
        response = export_tags_to_xlsx(self.request, tags)
        log.info(_("The user %s exported the data of selected tags") % self.request.identity.name)
        return response

    @view_config(
        route_name="user_clear_selected_tags",
        request_method="POST",
        permission="view",
    )
    def clear_selected_tags(self):
        _ = self.request.translate
        user = self.request.context.user
        user.selected_tags = []
        log.info(_("The user %s cleared the selected tags") % self.request.identity.name)
        next_url = self.request.route_url("user_selected_tags", username=user.name)
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="user_selected_contacts",
        renderer="user_selected_contacts.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_selected_contacts",
        renderer="contact_more.mako",
        permission="view",
    )
    def selected_contacts(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "name")
        _order = self.request.params.get("order", "asc")
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        stmt = (
            select(Contact)
            .join(selected_contacts)
            .filter(user.id == selected_contacts.c.user_id)
        )

        if _order == "asc":
            stmt = stmt.order_by(getattr(Contact, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Contact, _sort).desc())

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
            "user_more_selected_contacts",
            username=user.name,
            _query={
                **search_query,
                "page": page + 1,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
            },
        )

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, _filter, _sort, _order)
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, _filter, _sort, _order
        )

        return {
            "search_query": search_query,
            "user": user,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
        }

    @view_config(
        route_name="user_export_selected_contacts",
        permission="view",
    )
    def export_selected_contacts(self):
        _ = self.request.translate
        user = self.request.context.user
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")

        stmt = (
            select(Contact)
            .join(selected_contacts)
            .filter(user.id == selected_contacts.c.user_id)
        )

        if order == "asc":
            stmt = stmt.order_by(getattr(Contact, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Contact, sort).desc())

        contacts = self.request.dbsession.execute(stmt).scalars()
        response = export_contacts_to_xlsx(contacts)
        log.info(_("The user %s exported the data of selected contacts") % self.request.identity.name)
        return response

    @view_config(
        route_name="user_clear_selected_contacts",
        request_method="POST",
        permission="view",
    )
    def clear_selected_contacts(self):
        _ = self.request.translate
        user = self.request.context.user
        user.selected_contacts = []
        log.info(_("The user %s cleared the selected contacts") % self.request.identity.name)
        next_url = self.request.route_url("user_selected_contacts", username=user.name)
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
        route_name="user_more_recommended",
        renderer="company_more.mako",
        permission="view",
    )
    def recommended(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "name")
        _order = self.request.params.get("order", "asc")
        sort_criteria = dict(SORT_CRITERIA_EXT)
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        regions = dict(REGIONS)

        stmt = (
            select(Company).join(recommended).filter(user.id == recommended.c.user_id)
        )

        if _filter:
            stmt = stmt.filter(Company.color == _filter)

        if _order == "asc":
            stmt = stmt.order_by(getattr(Company, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Company, _sort).desc())

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
            "user_more_recommended",
            username=user.name,
            _query={
                **search_query,
                "page": page + 1,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
            },
        )

        dd_filter = Dropdown(self.request, colors, Dd.FILTER, _filter, _sort, _order)
        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, _filter, _sort, _order)
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, _filter, _sort, _order
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
            "regions": regions,
            "counter": counter,
        }

    @view_config(
        route_name="user_export_recommended",
        permission="view",
    )
    def export_recommended(self):
        _ = self.request.translate
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
        response = export_companies_to_xlsx(self.request, companies)
        log.info(_("The user %s exported the data of recommended companies") % self.request.identity.name)
        return response

    @view_config(
        route_name="user_clear_recommended",
        request_method="POST",
        permission="view",
    )
    def clear_recommended(self):
        _ = self.request.translate
        user = self.request.context.user
        user.recommended = []
        log.info(_("The user %s cleared recommendations") % self.request.identity.name)
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
        route_name="user_more_watched",
        renderer="project_more.mako",
        permission="view",
    )
    def watched(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "asc")
        status = dict(STATUS)
        sort_criteria = dict(SORT_CRITERIA_EXT)
        order_criteria = dict(ORDER_CRITERIA)
        regions = dict(REGIONS)
        now = datetime.datetime.now()

        stmt = select(Project).join(watched).filter(user.id == watched.c.user_id)

        if _filter == "in_progress":
            stmt = stmt.filter(Project.deadline > now.date())
        elif _filter == "completed":
            stmt = stmt.filter(Project.deadline < now.date())

        if _order == "asc":
            stmt = stmt.order_by(getattr(Project, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Project, _sort).desc())

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
            "user_more_watched",
            username=user.name,
            _query={
                **search_query,
                "page": page + 1,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
            },
        )

        dd_filter = Dropdown(self.request, status, Dd.FILTER, _filter, _sort, _order)
        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, _filter, _sort, _order)
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, _filter, _sort, _order
        )

        return {
            "search_query": search_query,
            "user": user,
            "dd_filter": dd_filter,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "regions": regions,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
        }

    @view_config(
        route_name="user_export_watched",
        permission="view",
    )
    def export_watched(self):
        _ = self.request.translate
        user = self.request.context.user
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "asc")
        now = datetime.datetime.now()

        stmt = select(Project).join(watched).filter(user.id == watched.c.user_id)

        if _filter == "in_progress":
            stmt = stmt.filter(Project.deadline > now.date())
        elif _filter == "completed":
            stmt = stmt.filter(Project.deadline < now.date())

        if _order == "asc":
            stmt = stmt.order_by(getattr(Project, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Project, _sort).desc())

        projects = self.request.dbsession.execute(stmt).scalars()
        response = export_projects_to_xlsx(self.request, projects)
        log.info(_("The user %s exported the data of the observed projects") % self.request.identity.name)
        return response

    @view_config(
        route_name="user_clear_watched",
        request_method="POST",
        permission="view",
    )
    def clear_watched(self):
        _ = self.request.translate
        user = self.request.context.user
        user.watched = []
        log.info(_("The user %s cleared watched projects") % self.request.identity.name)
        next_url = self.request.route_url("user_watched", username=user.name)
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response
