import datetime
import logging

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import func, select

from ..forms import (
    CompanyFilterForm,
    ProjectFilterForm,
    UserFilterForm,
    UserForm,
    UserSearchForm,
)
from ..forms.select import (
    COLORS,
    ORDER_CRITERIA,
    SORT_CRITERIA,
    SORT_CRITERIA_COMPANIES,
    SORT_CRITERIA_EXT,
    SORT_CRITERIA_PROJECTS,
    USER_ROLES,
)
from ..models import (
    Comment,
    Company,
    Contact,
    Project,
    Tag,
    User,
    recommended,
    selected_companies,
    selected_contacts,
    selected_projects,
    selected_tags,
    watched,
)
from ..utils.dropdown import Dd, Dropdown
from ..utils.export import response_xlsx
from ..utils.paginator import get_paginator
from . import Filter

log = logging.getLogger(__name__)


class UserView:
    def __init__(self, request):
        self.request = request

    def pills(self, user):
        _ = self.request.translate
        return [
            {
                "title": _("User"),
                "icon": "person-circle",
                "url": self.request.route_url("user_view", username=user.name),
                "count": None,
            },
            {
                "title": _("Companies"),
                "icon": "buildings",
                "url": self.request.route_url("user_companies", username=user.name),
                "count": self.request.route_url(
                    "user_count_companies", username=user.name
                ),
                "event": "userEvent",
                "init_value": user.count_companies,
            },
            {
                "title": _("Projects"),
                "icon": "briefcase",
                "url": self.request.route_url("user_projects", username=user.name),
                "count": self.request.route_url(
                    "user_count_projects", username=user.name
                ),
                "event": "userEvent",
                "init_value": user.count_projects,
            },
            {
                "title": _("Tags"),
                "icon": "tags",
                "url": self.request.route_url("user_tags", username=user.name),
                "count": self.request.route_url("user_count_tags", username=user.name),
                "event": "userEvent",
                "init_value": user.count_tags,
            },
            {
                "title": _("Contacts"),
                "icon": "people",
                "url": self.request.route_url("user_contacts", username=user.name),
                "count": self.request.route_url(
                    "user_count_contacts", username=user.name
                ),
                "event": "userEvent",
                "init_value": user.count_contacts,
            },
            {
                "title": _("Comments"),
                "icon": "chat-left-text",
                "url": self.request.route_url("user_comments", username=user.name),
                "count": self.request.route_url(
                    "user_count_comments", username=user.name
                ),
                "event": "userEvent",
                "init_value": user.count_comments,
            },
        ]

    @view_config(route_name="user_all", renderer="user_all.mako", permission="view")
    @view_config(route_name="user_more", renderer="user_more.mako", permission="view")
    def all(self):
        page = int(self.request.params.get("page", 1))
        name = self.request.params.get("name", None)
        fullname = self.request.params.get("fullname", None)
        email = self.request.params.get("email", None)
        role = self.request.params.get("role", None)
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)
        roles = dict(USER_ROLES)
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        q = {}

        stmt = select(User)

        if name:
            stmt = stmt.filter(User.name.ilike("%" + name + "%"))
            q["name"] = name

        if fullname:
            stmt = stmt.filter(User.fullname.ilike("%" + fullname + "%"))
            q["fullname"] = fullname

        if email:
            stmt = stmt.filter(User.email.ilike("%" + email + "%"))
            q["email"] = email

        if role:
            stmt = stmt.filter(User.role.ilike("%" + role + "%"))
            q["role"] = role

        if _sort:
            q["sort"] = _sort

        if _order:
            q["order"] = _order

        if not _sort:
            _sort = "created_at"

        if not _order:
            _order = "desc"

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

        next_page = self.request.route_url(
            "user_more",
            _query={
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = UserFilterForm(self.request.GET, obj, request=self.request)

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, q, _sort, _order)
        dd_order = Dropdown(self.request, order_criteria, Dd.ORDER, q, _sort, _order)

        return {
            "q": q,
            "roles": roles,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "form": form,
        }

    @view_config(route_name="user_view", renderer="user_view.mako", permission="view")
    def view(self):
        user = self.request.context.user
        return {
            "user": user,
            "title": user.fullname,
            "user_pills": self.pills(user),
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
            "user_pills": self.pills(user),
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
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        q = {}

        if _sort:
            q["sort"] = _sort

        if _order:
            q["order"] = _order

        if not _sort:
            _sort = "created_at"

        if not _order:
            _order = "desc"

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

        next_page = self.request.route_url(
            "user_more_tags",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, q, _sort, _order)
        dd_order = Dropdown(self.request, order_criteria, Dd.ORDER, q, _sort, _order)

        return {
            "q": q,
            "user": user,
            "paginator": paginator,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "next_page": next_page,
            "title": user.fullname,
            "user_pills": self.pills(user),
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
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)
        sort_criteria = dict(SORT_CRITERIA_COMPANIES)
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        q = {}

        if _sort:
            q["sort"] = _sort

        if _order:
            q["order"] = _order

        if not _sort:
            _sort = "name"

        if not _order:
            _order = "asc"

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

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more_companies",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, q, _sort, _order)
        dd_order = Dropdown(self.request, order_criteria, Dd.ORDER, q, _sort, _order)

        return {
            "q": q,
            "user": user,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "colors": colors,
            "paginator": paginator,
            "next_page": next_page,
            "title": user.fullname,
            "user_pills": self.pills(user),
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
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)
        order_criteria = dict(ORDER_CRITERIA)
        sort_criteria = dict(SORT_CRITERIA_PROJECTS)
        q = {}

        if _sort:
            q["sort"] = _sort

        if _order:
            q["order"] = _order

        if not _sort:
            _sort = "created_at"

        if not _order:
            _order = "desc"

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

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more_projects",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, q, _sort, _order)
        dd_order = Dropdown(self.request, order_criteria, Dd.ORDER, q, _sort, _order)

        return {
            "q": q,
            "user": user,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "title": user.fullname,
            "user_pills": self.pills(user),
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
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        q = {}

        if _sort:
            q["sort"] = _sort

        if _order:
            q["order"] = _order

        if not _sort:
            _sort = "created_at"

        if not _order:
            _order = "desc"

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

        next_page = self.request.route_url(
            "user_more_contacts",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, q, _sort, _order)
        dd_order = Dropdown(self.request, order_criteria, Dd.ORDER, q, _sort, _order)

        return {
            "q": q,
            "user": user,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "title": user.fullname,
            "user_pills": self.pills(user),
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
            log.info(
                _("The user %s has changed the user's data")
                % self.request.identity.name
            )
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
        q = {}
        for fieldname, value in form.data.items():
            if value:
                q[fieldname] = value

        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "user_all",
                    _query=q,
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
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)
        sort_criteria = dict(SORT_CRITERIA_EXT)
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        q = {}

        if _sort:
            q["sort"] = _sort

        if _order:
            q["order"] = _order

        if not _sort:
            _sort = "name"

        if not _order:
            _order = "asc"

        stmt = (
            select(Company)
            .join(selected_companies)
            .filter(user.id == selected_companies.c.user_id)
        )

        if _order == "asc":
            stmt = stmt.order_by(getattr(Company, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Company, _sort).desc())

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more_selected_companies",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, q, _sort, _order)
        dd_order = Dropdown(self.request, order_criteria, Dd.ORDER, q, _sort, _order)

        return {
            "q": q,
            "user": user,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "counter": counter,
        }

    @view_config(
        route_name="user_export_selected_companies",
        permission="view",
    )
    def export_selected_companies(self):
        _ = self.request.translate
        user = self.request.context.user
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)

        stmt = (
            select(
                Company.name,
                Company.street,
                Company.postcode,
                Company.city,
                Company.subdivision,
                Company.country,
                Company.link,
                Company.NIP,
                Company.REGON,
                Company.KRS,
            )
            .join(selected_companies)
            .filter(user.id == selected_companies.c.user_id)
        )

        if not _sort:
            _sort = "name"

        if not _order:
            _order = "asc"

        if _order == "asc":
            stmt = stmt.order_by(getattr(Company, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Company, _sort).desc())

        companies = self.request.dbsession.execute(stmt).all()
        header_row = [
            _("Name"),
            _("Street"),
            _("Post code"),
            _("City"),
            _("Subdivision"),
            _("Country"),
            _("Link"),
            _("NIP"),
            _("REGON"),
            _("KRS"),
        ]
        response = response_xlsx(companies, header_row)
        log.info(
            _("The user %s exported the data of selected companies")
            % self.request.identity.name
        )
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
        log.info(
            _("The user %s cleared the selected companies") % self.request.identity.name
        )
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
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)
        sort_criteria = dict(SORT_CRITERIA_PROJECTS)
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        q = {}

        if _sort:
            q["sort"] = _sort

        if _order:
            q["order"] = _order

        if not _sort:
            _sort = "name"

        if not _order:
            _order = "asc"

        stmt = (
            select(Project)
            .join(selected_projects)
            .filter(user.id == selected_projects.c.user_id)
        )

        if _order == "asc":
            stmt = stmt.order_by(getattr(Project, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Project, _sort).desc())

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more_selected_projects",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, q, _sort, _order)
        dd_order = Dropdown(self.request, order_criteria, Dd.ORDER, q, _sort, _order)

        return {
            "q": q,
            "user": user,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "counter": counter,
        }

    @view_config(
        route_name="user_export_selected_projects",
        permission="view",
    )
    def export_selected_projects(self):
        _ = self.request.translate
        user = self.request.context.user
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)

        stmt = (
            select(
                Project.name,
                Project.street,
                Project.postcode,
                Project.city,
                Project.subdivision,
                Project.country,
                Project.link,
                Project.deadline,
                Project.stage,
                Project.delivery_method,
            )
            .join(selected_projects)
            .filter(user.id == selected_projects.c.user_id)
        )

        if not _sort:
            _sort = "name"

        if not _order:
            _order = "asc"

        if _order == "asc":
            stmt = stmt.order_by(getattr(Project, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Project, _sort).desc())

        projects = self.request.dbsession.execute(stmt).all()
        header_row = [
            _("Name"),
            _("Street"),
            _("Post code"),
            _("City"),
            _("Subdivision"),
            _("Country"),
            _("Link"),
            _("Deadline"),
            _("Stage"),
            _("Project delivery method"),
        ]
        response = response_xlsx(projects, header_row)
        log.info(
            _("The user %s exported the data of selected projects")
            % self.request.identity.name
        )
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
        log.info(
            _("The user %s cleared the selected projects") % self.request.identity.name
        )
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
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        q = {}

        if _sort:
            q["sort"] = _sort

        if _order:
            q["order"] = _order

        if not _sort:
            _sort = "name"

        if not _order:
            _order = "asc"

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

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more_selected_tags",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, q, _sort, _order)
        dd_order = Dropdown(self.request, order_criteria, Dd.ORDER, q, _sort, _order)

        return {
            "q": q,
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
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)

        stmt = (
            select(Tag.name)
            .join(selected_tags)
            .filter(user.id == selected_tags.c.user_id)
        )

        if not _sort:
            _sort = "name"

        if not _order:
            _order = "asc"

        if _order == "asc":
            stmt = stmt.order_by(getattr(Tag, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Tag, _sort).desc())

        tags = self.request.dbsession.execute(stmt).all()
        header_row = [_("Tag")]
        response = response_xlsx(tags, header_row)
        log.info(
            _("The user %s exported the data of selected tags")
            % self.request.identity.name
        )
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
        log.info(
            _("The user %s cleared the selected tags") % self.request.identity.name
        )
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
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        q = {}

        if _sort:
            q["sort"] = _sort

        if _order:
            q["order"] = _order

        if not _sort:
            _sort = "name"

        if not _order:
            _order = "asc"

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

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more_selected_contacts",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, q, _sort, _order)
        dd_order = Dropdown(self.request, order_criteria, Dd.ORDER, q, _sort, _order)

        return {
            "q": q,
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
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)

        stmt = (
            select(Contact.name, Contact.role, Contact.phone, Contact.email)
            .join(selected_contacts)
            .filter(user.id == selected_contacts.c.user_id)
        )

        if not _sort:
            _sort = "name"

        if not _order:
            _order = "asc"

        if _order == "asc":
            stmt = stmt.order_by(getattr(Contact, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Contact, _sort).desc())

        contacts = self.request.dbsession.execute(stmt).all()
        header_row = [_("Fullname"), _("Role"), _("Phone"), _("Email")]
        response = response_xlsx(contacts, header_row)
        log.info(
            _("The user %s exported the data of selected contacts")
            % self.request.identity.name
        )
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
        log.info(
            _("The user %s cleared the selected contacts") % self.request.identity.name
        )
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
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)
        sort_criteria = dict(SORT_CRITERIA_EXT)
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        q = {}

        stmt = (
            select(Company).join(recommended).filter(user.id == recommended.c.user_id)
        )

        if color:
            stmt = stmt.filter(Company.color == color)
            q["color"] = color

        if country:
            stmt = stmt.filter(Company.country == country)
            q["country"] = country

        if subdivision:
            stmt = stmt.filter(Company.subdivision.in_(subdivision))
            q["subdivision"] = list(subdivision)

        if _sort:
            q["sort"] = _sort

        if _order:
            q["order"] = _order

        if not _sort:
            _sort = "name"

        if not _order:
            _order = "asc"

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

        next_page = self.request.route_url(
            "user_more_recommended",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = CompanyFilterForm(self.request.GET, obj, request=self.request)

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, q, _sort, _order)
        dd_order = Dropdown(self.request, order_criteria, Dd.ORDER, q, _sort, _order)

        return {
            "q": q,
            "user": user,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "counter": counter,
            "form": form,
        }

    @view_config(
        route_name="user_export_recommended",
        permission="view",
    )
    def export_recommended(self):
        _ = self.request.translate
        user = self.request.context.user
        color = self.request.params.get("color", None)
        subdivision = self.request.params.getall("subdivision")
        country = self.request.params.get("country", None)
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)

        stmt = (
            select(
                Company.name,
                Company.street,
                Company.postcode,
                Company.city,
                Company.subdivision,
                Company.country,
                Company.link,
                Company.NIP,
                Company.REGON,
                Company.KRS,
            )
            .join(recommended)
            .filter(user.id == recommended.c.user_id)
        )

        if color:
            stmt = stmt.filter(Company.color == color)

        if subdivision:
            stmt = stmt.filter(Company.subdivision.in_(subdivision))

        if country:
            stmt = stmt.filter(Company.country == country)

        if not _sort:
            _sort = "name"

        if not _order:
            _order = "asc"

        if _order == "asc":
            stmt = stmt.order_by(getattr(Company, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Company, _sort).desc())

        companies = self.request.dbsession.execute(stmt).all()
        header_row = [
            _("Name"),
            _("Street"),
            _("Post code"),
            _("City"),
            _("Subdivision"),
            _("Country"),
            _("Link"),
            _("NIP"),
            _("REGON"),
            _("KRS"),
        ]
        response = response_xlsx(companies, header_row)
        log.info(
            _("The user %s exported the data of recommended companies")
            % self.request.identity.name
        )
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
        status = self.request.params.get("status", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)
        sort_criteria = dict(SORT_CRITERIA_EXT)
        order_criteria = dict(ORDER_CRITERIA)
        now = datetime.datetime.now()
        q = {}

        stmt = select(Project).join(watched).filter(user.id == watched.c.user_id)

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

        if _sort:
            q["sort"] = _sort

        if _order:
            q["order"] = _order

        if not _sort:
            _sort = "created_at"

        if not _order:
            _order = "desc"

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

        next_page = self.request.route_url(
            "user_more_watched",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = ProjectFilterForm(self.request.GET, obj, request=self.request)

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, q, _sort, _order)
        dd_order = Dropdown(self.request, order_criteria, Dd.ORDER, q, _sort, _order)

        return {
            "q": q,
            "user": user,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "form": form,
        }

    @view_config(
        route_name="user_export_watched",
        permission="view",
    )
    def export_watched(self):
        _ = self.request.translate
        user = self.request.context.user
        status = self.request.params.get("status", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)
        now = datetime.datetime.now()

        stmt = (
            select(
                Project.name,
                Project.street,
                Project.postcode,
                Project.city,
                Project.subdivision,
                Project.country,
                Project.link,
                Project.deadline,
                Project.stage,
                Project.delivery_method,
            )
            .join(watched)
            .filter(user.id == watched.c.user_id)
        )

        if status == "in_progress":
            stmt = stmt.filter(Project.deadline > now)
        elif status == "completed":
            stmt = stmt.filter(Project.deadline < now)

        if color:
            stmt = stmt.filter(Project.color == color)

        if country:
            stmt = stmt.filter(Project.country == country)

        if subdivision:
            stmt = stmt.filter(Project.subdivision.in_(subdivision))

        if not _sort:
            _sort = "created_at"

        if not _order:
            _order = "desc"

        if _order == "asc":
            stmt = stmt.order_by(getattr(Project, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Project, _sort).desc())

        projects = self.request.dbsession.execute(stmt).all()
        header_row = [
            _("Name"),
            _("Street"),
            _("Post code"),
            _("City"),
            _("Subdivision"),
            _("Country"),
            _("Link"),
            _("Deadline"),
            _("Stage"),
            _("Project delivery method"),
        ]
        response = response_xlsx(projects, header_row)
        log.info(
            _("The user %s exported the data of the observed projects")
            % self.request.identity.name
        )
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

    @view_config(
        route_name="user_count_companies",
        renderer="json",
        permission="view",
    )
    def count_companies(self):
        user = self.request.context.user
        return user.count_companies

    @view_config(
        route_name="user_count_projects",
        renderer="json",
        permission="view",
    )
    def count_projects(self):
        user = self.request.context.user
        return user.count_projects

    @view_config(
        route_name="user_count_tags",
        renderer="json",
        permission="view",
    )
    def count_tags(self):
        user = self.request.context.user
        return user.count_tags

    @view_config(
        route_name="user_count_contacts",
        renderer="json",
        permission="view",
    )
    def count_contacts(self):
        user = self.request.context.user
        return user.count_contacts

    @view_config(
        route_name="user_count_comments",
        renderer="json",
        permission="view",
    )
    def count_comments(self):
        user = self.request.context.user
        return user.count_comments

    @view_config(
        route_name="user_map_companies",
        renderer="user_map_companies.mako",
        permission="view",
    )
    def map_companies(self):
        user = self.request.context.user
        url = self.request.route_url("user_json_companies", username=user.name)
        return {"user": user, "url": url, "user_pills": self.pills(user)}

    @view_config(
        route_name="user_map_projects",
        renderer="user_map_projects.mako",
        permission="view",
    )
    def map_projects(self):
        user = self.request.context.user
        url = self.request.route_url("user_json_projects", username=user.name)
        return {"user": user, "url": url, "user_pills": self.pills(user)}

    @view_config(
        route_name="user_json_companies",
        renderer="json",
        permission="view",
    )
    def json_companies(self):
        user = self.request.context.user
        stmt = select(Company).filter(Company.created_by == user)
        companies = self.request.dbsession.execute(stmt).scalars()
        res = [
            {
                "id": company.id,
                "name": company.name,
                "street": company.street,
                "city": company.city,
                "country": company.country,
                "latitude": company.latitude,
                "longitude": company.longitude,
                "color": company.color,
                "url": self.request.route_url(
                    "company_view", company_id=company.id, slug=company.slug
                ),
            }
            for company in companies
        ]
        return res

    @view_config(
        route_name="user_json_projects",
        renderer="json",
        permission="view",
    )
    def json_projects(self):
        user = self.request.context.user
        stmt = select(Project).filter(Project.created_by == user)
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
