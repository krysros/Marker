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
    ContactFilterForm,
    CommentFilterForm,
)
from ..forms.select import (
    COLORS,
    ORDER_CRITERIA,
    SORT_CRITERIA,
    SORT_CRITERIA_COMPANIES,
    SORT_CRITERIA_EXT,
    SORT_CRITERIA_PROJECTS,
    PROJECT_DELIVERY_METHODS,
    USER_ROLES,
    PARENTS,
    STATUS,
    STAGES,
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
from ..utils.export import response_xlsx
from ..utils.paginator import get_paginator
from . import Filter

log = logging.getLogger(__name__)


class UserView:
    def __init__(self, request):
        self.request = request
        self.count_companies = 0
        self.count_projects = 0
        self.count_tags = 0
        self.count_contacts = 0
        self.count_comments = 0

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
                "init_value": self.count_companies,
            },
            {
                "title": _("Projects"),
                "icon": "briefcase",
                "url": self.request.route_url("user_projects", username=user.name),
                "count": self.request.route_url(
                    "user_count_projects", username=user.name
                ),
                "event": "userEvent",
                "init_value": self.count_projects,
            },
            {
                "title": _("Tags"),
                "icon": "tags",
                "url": self.request.route_url("user_tags", username=user.name),
                "count": self.request.route_url("user_count_tags", username=user.name),
                "event": "userEvent",
                "init_value": self.count_tags,
            },
            {
                "title": _("Contacts"),
                "icon": "people",
                "url": self.request.route_url("user_contacts", username=user.name),
                "count": self.request.route_url(
                    "user_count_contacts", username=user.name
                ),
                "event": "userEvent",
                "init_value": self.count_contacts,
            },
            {
                "title": _("Comments"),
                "icon": "chat-left-text",
                "url": self.request.route_url("user_comments", username=user.name),
                "count": self.request.route_url(
                    "user_count_comments", username=user.name
                ),
                "event": "userEvent",
                "init_value": self.count_comments,
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
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
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

        q["sort"] = _sort
        q["order"] = _order

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

        return {
            "q": q,
            "roles": roles,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "form": form,
        }

    @view_config(route_name="user_view", renderer="user_view.mako", permission="view")
    def view(self):
        user = self.request.context.user
        self.count_companies = user.count_companies
        self.count_projects = user.count_projects
        self.count_tags = user.count_tags
        self.count_contacts = user.count_contacts
        self.count_comments = user.count_comments
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
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        parent = self.request.params.get("parent", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        order_criteria = dict(ORDER_CRITERIA)
        parents = dict(PARENTS)
        q = {}

        stmt = select(Comment).filter(Comment.created_by == user)

        if parent == "companies":
            stmt = stmt.filter(Comment.company)
            q["parent"] = parent
        elif parent == "projects":
            stmt = stmt.filter(Comment.project)
            q["parent"] = parent

        if _order == "asc":
            stmt = stmt.order_by(Comment.created_at.asc())
        elif _order == "desc":
            stmt = stmt.order_by(Comment.created_at.desc())

        q["sort"] = _sort
        q["order"] = _order

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        self.count_companies = user.count_companies
        self.count_projects = user.count_projects
        self.count_tags = user.count_tags
        self.count_contacts = user.count_contacts
        self.count_comments = counter

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_more_comments",
            username=user.name,
            _query={**q, "page": page + 1},
        )

        obj = Filter(**q)
        form = CommentFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "user": user,
            "paginator": paginator,
            "order_criteria": order_criteria,
            "parents": parents,
            "next_page": next_page,
            "title": user.fullname,
            "user_pills": self.pills(user),
            "form": form,
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
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        q = {}

        q["sort"] = _sort
        q["order"] = _order

        stmt = select(Tag).filter(Tag.created_by == user)

        if _order == "asc":
            stmt = stmt.order_by(getattr(Tag, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Tag, _sort).desc())

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        self.count_companies = user.count_companies
        self.count_projects = user.count_projects
        self.count_tags = counter
        self.count_contacts = user.count_contacts
        self.count_comments = user.count_comments

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

        return {
            "q": q,
            "user": user,
            "paginator": paginator,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
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
        name = self.request.params.get("name", None)
        street = self.request.params.get("street", None)
        postcode = self.request.params.get("postcode", None)
        city = self.request.params.get("city", None)
        subdivision = self.request.params.getall("subdivision")
        country = self.request.params.get("country", None)
        link = self.request.params.get("link", None)
        NIP = self.request.params.get("NIP", None)
        REGON = self.request.params.get("REGON", None)
        KRS = self.request.params.get("KRS", None)
        court = self.request.params.get("court", None)
        color = self.request.params.get("color", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA_COMPANIES)
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        q = {}

        stmt = select(Company).filter(Company.created_by == user)

        if name:
            stmt = stmt.filter(Company.name.ilike("%" + name + "%"))
            q["name"] = name

        if street:
            stmt = stmt.filter(Company.street.ilike("%" + street + "%"))
            q["street"] = street

        if postcode:
            stmt = stmt.filter(Company.postcode.ilike("%" + postcode + "%"))
            q["postcode"] = postcode

        if city:
            stmt = stmt.filter(Company.city.ilike("%" + city + "%"))
            q["city"] = city

        if link:
            stmt = stmt.filter(Company.link.ilike("%" + link + "%"))
            q["link"] = link

        if NIP:
            stmt = stmt.filter(Company.NIP.ilike("%" + NIP + "%"))
            q["NIP"] = NIP

        if REGON:
            stmt = stmt.filter(Company.REGON.ilike("%" + REGON + "%"))
            q["REGON"] = REGON

        if KRS:
            stmt = stmt.filter(Company.KRS.ilike("%" + KRS + "%"))
            q["KRS"] = KRS

        if subdivision:
            stmt = stmt.filter(Company.subdivision.in_(subdivision))
            q["subdivision"] = list(subdivision)

        if country:
            stmt = stmt.filter(Company.country == country)
            q["country"] = country

        if court:
            stmt = stmt.filter(Company.court == court)
            q["court"] = court

        if color:
            stmt = stmt.filter(Company.color == color)
            q["color"] = color

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

        q["sort"] = _sort
        q["order"] = _order

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        self.count_companies = counter
        self.count_projects = user.count_projects
        self.count_tags = user.count_tags
        self.count_contacts = user.count_contacts
        self.count_comments = user.count_comments

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

        obj = Filter(**q)
        form = CompanyFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "colors": colors,
            "paginator": paginator,
            "next_page": next_page,
            "title": user.fullname,
            "user_pills": self.pills(user),
            "form": form,
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
        name = self.request.params.get("name", None)
        street = self.request.params.get("street", None)
        postcode = self.request.params.get("postcode", None)
        city = self.request.params.get("city", None)
        subdivision = self.request.params.getall("subdivision")
        country = self.request.params.get("country", None)
        link = self.request.params.get("link", None)
        color = self.request.params.get("color", None)
        deadline = self.request.params.get("deadline", None)
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        order_criteria = dict(ORDER_CRITERIA)
        sort_criteria = dict(SORT_CRITERIA_PROJECTS)
        colors = dict(COLORS)
        statuses = dict(STATUS)
        stages = dict(STAGES)
        project_delivery_methods = dict(PROJECT_DELIVERY_METHODS)
        now = datetime.datetime.now()
        q = {}

        stmt = select(Project).filter(Project.created_by == user)

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

        if link:
            stmt = stmt.filter(Project.link.ilike("%" + link + "%"))
            q["link"] = link

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

        q["sort"] = _sort
        q["order"] = _order

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        self.count_companies = user.count_companies
        self.count_projects = counter
        self.count_tags = user.count_tags
        self.count_contacts = user.count_contacts
        self.count_comments = user.count_comments

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

        obj = Filter(**q)
        form = ProjectFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "colors": colors,
            "statuses": statuses,
            "stages": stages,
            "project_delivery_methods": project_delivery_methods,
            "paginator": paginator,
            "next_page": next_page,
            "title": user.fullname,
            "user_pills": self.pills(user),
            "form": form,
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
        name = self.request.params.get("name", None)
        role = self.request.params.get("role", None)
        phone = self.request.params.get("phone", None)
        email = self.request.params.get("email", None)
        parent = self.request.params.get("parent", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        parents = dict(PARENTS)
        q = {}

        stmt = select(Contact).filter(Contact.created_by == user)

        if name:
            stmt = stmt.filter(Contact.name.ilike("%" + name + "%"))
            q["name"] = name

        if role:
            stmt = stmt.filter(Contact.role.ilike("%" + role + "%"))
            q["role"] = role

        if phone:
            stmt = stmt.filter(Contact.phone.ilike("%" + phone + "%"))
            q["phone"] = phone

        if email:
            stmt = stmt.filter(Contact.email.ilike("%" + email + "%"))
            q["email"] = email

        if parent == "companies":
            stmt = stmt.filter(Contact.company)
            q["parent"] = parent
        elif parent == "projects":
            stmt = stmt.filter(Contact.project)
            q["parent"] = parent

        if _order == "asc":
            stmt = stmt.order_by(getattr(Contact, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Contact, _sort).desc())

        q["sort"] = _sort
        q["order"] = _order

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        self.count_companies = user.count_companies
        self.count_projects = user.count_projects
        self.count_tags = user.count_tags
        self.count_contacts = counter
        self.count_comments = user.count_comments

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more_contacts",
            username=user.name,
            _query={**q, "page": page + 1},
        )

        obj = Filter(**q)
        form = ContactFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "parents": parents,
            "paginator": paginator,
            "next_page": next_page,
            "title": user.fullname,
            "user_pills": self.pills(user),
            "form": form,
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
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA_EXT)
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        q = {}

        stmt = (
            select(Company)
            .join(selected_companies)
            .filter(user.id == selected_companies.c.user_id)
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

        if _order == "asc":
            stmt = stmt.order_by(getattr(Company, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Company, _sort).desc())

        q["sort"] = _sort
        q["order"] = _order

        obj = Filter(**q)
        form = CompanyFilterForm(self.request.GET, obj, request=self.request)

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

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "counter": counter,
            "form": form,
        }

    @view_config(
        route_name="user_json_selected_companies",
        renderer="json",
        permission="view",
    )
    def json_selected_companies(self):
        user = self.request.context.user
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        stmt = (
            select(Company)
            .join(selected_companies)
            .filter(user.id == selected_companies.c.user_id)
        )

        if color:
            stmt = stmt.filter(Company.color == color)

        if country:
            stmt = stmt.filter(Company.country == country)

        if subdivision:
            stmt = stmt.filter(Company.subdivision.in_(subdivision))

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
        route_name="user_map_selected_companies",
        renderer="user_map_selected_companies.mako",
        permission="view",
    )
    def map_selected_companies(self):
        user = self.request.context.user
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        q = {}

        stmt = (
            select(Company)
            .join(selected_companies)
            .filter(user.id == selected_companies.c.user_id)
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

        if _order == "asc":
            stmt = stmt.order_by(getattr(Company, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Company, _sort).desc())

        q["sort"] = _sort
        q["order"] = _order

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        url = self.request.route_url("user_json_selected_companies", username=user.name, _query=q)
        return {"user": user, "url": url, "q": q, "counter": counter}

    @view_config(
        route_name="user_export_selected_companies",
        permission="view",
    )
    def export_selected_companies(self):
        _ = self.request.translate
        user = self.request.context.user
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")

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
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        sort_criteria = dict(SORT_CRITERIA_PROJECTS)
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        q = {}

        stmt = (
            select(Project)
            .join(selected_projects)
            .filter(user.id == selected_projects.c.user_id)
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

        if _order == "asc":
            stmt = stmt.order_by(getattr(Project, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Project, _sort).desc())

        q["sort"] = _sort
        q["order"] = _order

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

        obj = Filter(**q)
        form = ProjectFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "counter": counter,
            "form": form,
        }

    @view_config(
        route_name="user_json_selected_projects",
        renderer="json",
        permission="view",
    )
    def json_selected_projects(self):
        user = self.request.context.user
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        now = datetime.datetime.now()

        stmt = (
            select(Project)
            .join(selected_projects)
            .filter(user.id == selected_projects.c.user_id)
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

        if stage:
            stmt = stmt.filter(Project.stage == stage)

        if delivery_method:
            stmt = stmt.filter(Project.delivery_method == delivery_method)

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
        route_name="user_map_selected_projects",
        renderer="user_map_selected_projects.mako",
        permission="view",
    )
    def map_selected_projects(self):
        user = self.request.context.user
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        q = {}

        stmt = (
            select(Project)
            .join(selected_projects)
            .filter(user.id == selected_projects.c.user_id)
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

        if _order == "asc":
            stmt = stmt.order_by(getattr(Project, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Project, _sort).desc())

        q["sort"] = _sort
        q["order"] = _order

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        url = self.request.route_url("user_json_selected_projects", username=user.name, _query=q)
        return {"user": user, "url": url, "q": q, "counter": counter}

    @view_config(
        route_name="user_export_selected_projects",
        permission="view",
    )
    def export_selected_projects(self):
        _ = self.request.translate
        user = self.request.context.user
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")

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
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        q = {}

        q["sort"] = _sort
        q["order"] = _order

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

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
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
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")

        stmt = (
            select(Tag.name)
            .join(selected_tags)
            .filter(user.id == selected_tags.c.user_id)
        )

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
        name = self.request.params.get("name", None)
        role = self.request.params.get("role", None)
        phone = self.request.params.get("phone", None)
        email = self.request.params.get("email", None)
        parent = self.request.params.get("parent", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        q = {}

        q["sort"] = _sort
        q["order"] = _order

        stmt = (
            select(Contact)
            .join(selected_contacts)
            .filter(user.id == selected_contacts.c.user_id)
        )

        if name:
            stmt = stmt.filter(Contact.name.ilike("%" + name + "%"))
            q["name"] = name

        if role:
            stmt = stmt.filter(Contact.role.ilike("%" + role + "%"))
            q["role"] = role

        if phone:
            stmt = stmt.filter(Contact.phone.ilike("%" + phone + "%"))
            q["phone"] = phone

        if email:
            stmt = stmt.filter(Contact.email.ilike("%" + email + "%"))
            q["email"] = email

        if parent == "companies":
            stmt = stmt.filter(Contact.company)
            q["parent"] = parent
        elif parent == "projects":
            stmt = stmt.filter(Contact.project)
            q["parent"] = parent

        if _order == "asc":
            stmt = stmt.order_by(getattr(Contact, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Contact, _sort).desc())

        q["sort"] = _sort
        q["order"] = _order

        obj = Filter(**q)
        form = ContactFilterForm(self.request.GET, obj, request=self.request)

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

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "form": form,
        }

    @view_config(
        route_name="user_export_selected_contacts",
        permission="view",
    )
    def export_selected_contacts(self):
        _ = self.request.translate
        user = self.request.context.user
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")

        stmt = (
            select(Contact.name, Contact.role, Contact.phone, Contact.email)
            .join(selected_contacts)
            .filter(user.id == selected_contacts.c.user_id)
        )

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
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
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

        q["sort"] = _sort
        q["order"] = _order

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

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
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
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")

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
        route_name="user_json_recommended",
        renderer="json",
        permission="view",
    )
    def json_recommended(self):
        user = self.request.context.user
        stmt = (
            select(Company).join(recommended).filter(user.id == recommended.c.user_id)
        )
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
        route_name="user_map_recommended",
        renderer="user_map_recommended.mako",
        permission="view",
    )
    def map_recommended(self):
        user = self.request.context.user
        stmt = (
            select(Company).join(recommended).filter(user.id == recommended.c.user_id)
        )
        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()
        url = self.request.route_url("user_json_recommended", username=user.name)
        return {"user": user, "url": url, "counter": counter}

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
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA_EXT)
        order_criteria = dict(ORDER_CRITERIA)
        project_delivery_methods = dict(PROJECT_DELIVERY_METHODS)
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

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "project_delivery_methods": project_delivery_methods,
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
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
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
        route_name="user_json_watched",
        renderer="json",
        permission="view",
    )
    def json_watched(self):
        user = self.request.context.user
        stmt = select(Project).join(watched).filter(user.id == watched.c.user_id)
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
        route_name="user_map_watched",
        renderer="user_map_watched.mako",
        permission="view",
    )
    def map_watched(self):
        user = self.request.context.user
        stmt = select(Project).join(watched).filter(user.id == watched.c.user_id)
        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()
        url = self.request.route_url("user_json_watched", username=user.name)
        return {"user": user, "url": url, "counter": counter}

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
