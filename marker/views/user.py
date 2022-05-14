import logging
import datetime
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from sqlalchemy import select

import deform
import colander

from ..models import (
    User,
    marker,
    upvotes,
    following,
    Branch,
    Company,
    Comment,
    Investment,
)
from deform.schema import CSRFSchema
from zxcvbn import zxcvbn
from ..paginator import get_paginator
from ..export import (
    export_companies_to_xlsx,
    export_investments_to_xlsx,
)
from .select import (
    ROLES,
    VOIVODESHIPS,
)

log = logging.getLogger(__name__)


class UserView(object):
    def __init__(self, request):
        self.request = request

    @property
    def user_form(self):
        def check_name(node, value):
            exists = self.request.dbsession.execute(
                select(User).filter_by(username=value)
            ).scalar_one_or_none()
            username = self.request.matchdict.get("username", None)
            if exists and username != exists.username:
                raise colander.Invalid(
                    node, "Ta nazwa użytkownika jest już zajęta"
                )

        def password_strength_estimator(node, value):
            results = zxcvbn(value)
            if results["score"] < 3:
                raise colander.Invalid(node, "Zbyt proste hasło!")

        class Schema(CSRFSchema):
            username = colander.SchemaNode(
                colander.String(),
                title="Nazwa użytkownika",
                validator=colander.All(
                    colander.Length(min=3, max=30), check_name
                ),
            )
            fullname = colander.SchemaNode(
                colander.String(),
                title="Imię i nazwisko",
                validator=colander.Length(min=5, max=50),
            )
            email = colander.SchemaNode(
                colander.String(),
                title="Adres email",
                validator=colander.Email(),
            )
            role = colander.SchemaNode(
                colander.String(),
                title="Rola",
                widget=deform.widget.SelectWidget(values=ROLES),
            )
            password = colander.SchemaNode(
                colander.String(),
                title="Hasło",
                validator=colander.All(
                    colander.Length(min=5, max=100),
                    password_strength_estimator,
                ),
                widget=deform.widget.PasswordWidget(),
            )

        schema = Schema().bind(request=self.request)
        submit_btn = deform.form.Button(name="submit", title="Zapisz")
        return deform.Form(schema, buttons=(submit_btn,))

    @view_config(
        route_name="user_all", renderer="user_all.mako", permission="view"
    )
    @view_config(
        route_name="user_more", renderer="user_more.mako", permission="view"
    )
    def all(self):
        page = int(self.request.params.get("page", 1))
        role = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "added")
        order = self.request.params.get("order", "desc")
        roles = dict(ROLES)
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
            "filter": role,
            "sort": sort,
            "order": order,
            "paginator": paginator,
            "next_page": next_page,
        }

    @view_config(
        route_name="user_view", renderer="user_view.mako", permission="view"
    )
    def view(self):
        user = self.request.context.user
        return {"user": user}

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
            .filter(Comment.added_by == user)
            .order_by(Comment.added.desc())
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_comments_more",
            username=user.username,
            _query={"page": page + 1},
        )
        return {"user": user, "paginator": paginator, "next_page": next_page}

    @view_config(
        route_name="user_branches",
        renderer="user_branches.mako",
        permission="view",
    )
    @view_config(
        route_name="user_branches_more",
        renderer="branch_more.mako",
        permission="view",
    )
    def branches(self):
        page = int(self.request.params.get("page", 1))
        user = self.request.context.user
        stmt = (
            select(Branch)
            .filter(Branch.added_by == user)
            .order_by(Branch.added.desc())
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_branches_more",
            username=user.username,
            _query={"page": page + 1},
        )
        return {"user": user, "paginator": paginator, "next_page": next_page}

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
        page = int(self.request.params.get("page", 1))
        user = self.request.context.user
        voivodeships = dict(VOIVODESHIPS)
        stmt = (
            select(Company)
            .filter(Company.added_by == user)
            .order_by(Company.added.desc())
        )

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_companies_more",
            username=user.username,
            _query={"page": page + 1},
        )
        return {
            "user": user,
            "voivodeships": voivodeships,
            "paginator": paginator,
            "next_page": next_page,
        }

    @view_config(
        route_name="user_investments",
        renderer="user_investments.mako",
        permission="view",
    )
    def investments(self):
        page = int(self.request.params.get("page", 1))
        user = self.request.context.user
        stmt = (
            select(Investment)
            .filter(Investment.added_by == user)
            .order_by(Investment.added.desc())
        )

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_investments_more",
            username=user.username,
            _query={"page": page + 1},
        )
        return {
            "user": user,
            "paginator": paginator,
            "next_page": next_page,
        }

    @view_config(
        route_name="user_add", renderer="form.mako", permission="admin"
    )
    def add(self):
        form = self.user_form
        appstruct = {}
        rendered_form = None

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                rendered_form = e.render()
            else:
                user = User(
                    username=appstruct["username"],
                    fullname=appstruct["fullname"],
                    email=appstruct["email"],
                    role=appstruct["role"],
                    password=appstruct["password"],
                )
                self.request.dbsession.add(user)
                self.request.session.flash("success:Dodano do bazy danych")
                log.info(
                    f"Użytkownik {self.request.identity.username} dodał użytkownika {user.username}"
                )
                return HTTPFound(location=self.request.route_url("user_all"))

        if rendered_form is None:
            rendered_form = form.render(appstruct=appstruct)
        reqts = form.get_widget_resources()

        return dict(
            heading="Dodaj użytkownika",
            rendered_form=rendered_form,
            css_links=reqts["css"],
            js_links=reqts["js"],
        )

    @view_config(
        route_name="user_edit", renderer="form.mako", permission="admin"
    )
    def edit(self):
        user = self.request.context.user
        form = self.user_form
        rendered_form = None

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                rendered_form = e.render()
            else:
                user.username = appstruct["username"]
                user.fullname = appstruct["fullname"]
                user.email = appstruct["email"]
                user.role = appstruct["role"]
                user.password = appstruct["password"]

                self.request.session.flash("success:Zmiany zostały zapisane")
                log.info(
                    f"Użytkownik {self.request.identity.username} zmienił dane użytkownika {user.username}"
                )
                return HTTPFound(location=self.request.route_url("user_all"))

        appstruct = {
            "username": user.username,
            "fullname": user.fullname,
            "email": user.email,
            "role": user.role,
            "password": user.password,
        }
        if rendered_form is None:
            rendered_form = form.render(appstruct=appstruct)
        reqts = form.get_widget_resources()

        return dict(
            heading="Edytuj dane użytkownika",
            rendered_form=rendered_form,
            css_links=reqts["css"],
            js_links=reqts["js"],
        )

    @view_config(
        route_name="user_delete", request_method="POST", permission="admin"
    )
    def delete(self):
        user = self.request.context.user
        user_id = user.id
        user_username = user.username
        self.request.dbsession.delete(user)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(
            f"Użytkownik {self.request.identity.username} usunął użytkownika {user_username}"
        )
        return HTTPFound(location=self.request.route_url("home"))

    @view_config(
        route_name="user_search",
        renderer="user_search.mako",
        permission="view",
    )
    def search(self):
        return {}

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
            .filter(User.username.ilike("%" + username + "%"))
            .order_by(User.username)
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
        route_name="user_marked",
        renderer="user_marked.mako",
        permission="view",
    )
    @view_config(
        route_name="user_marked_more",
        renderer="company_more.mako",
        permission="view",
    )
    def marked(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")
        stmt = select(Company).join(marker).filter(user.id == marker.c.user_id)

        if order == "asc":
            stmt = stmt.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Company, sort).desc())

        voivodeships = dict(VOIVODESHIPS)
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_marked_more",
            username=user.username,
            _query={"page": page + 1, "sort": sort, "order": order},
        )

        return dict(
            user=user,
            sort=sort,
            order=order,
            paginator=paginator,
            next_page=next_page,
            voivodeships=voivodeships,
        )

    @view_config(
        route_name="user_marked_export",
        request_method="POST",
        permission="view",
    )
    def export_marked(self):
        user = self.request.context.user
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")

        query = (
            select(Company).join(marker).filter(user.id == marker.c.user_id)
        )

        if order == "asc":
            query = query.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            query = query.order_by(getattr(Company, sort).desc())

        companies = self.request.dbsession.execute(query).scalars()
        response = export_companies_to_xlsx(companies)
        log.info(
            f"Użytkownik {self.request.identity.username} eksportował dane zaznaczonych firm"
        )
        return response

    @view_config(
        route_name="user_marked_clear",
        request_method="POST",
        permission="view",
    )
    def clear_marked(self):
        user = self.request.context.user
        user.marker = []
        return HTTPFound(
            location=self.request.route_url(
                "user_marked", username=user.username
            )
        )

    @view_config(
        route_name="user_upvotes",
        renderer="user_upvotes.mako",
        permission="view",
    )
    @view_config(
        route_name="user_upvotes_more",
        renderer="company_more.mako",
        permission="view",
    )
    def upvotes(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")

        stmt = (
            select(Company).join(upvotes).filter(user.id == upvotes.c.user_id)
        )

        if order == "asc":
            stmt = stmt.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Company, sort).desc())

        voivodeships = dict(VOIVODESHIPS)
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_upvotes_more",
            username=user.username,
            _query={"page": page + 1, "sort": sort, "order": order},
        )

        return dict(
            user=user,
            sort=sort,
            order=order,
            paginator=paginator,
            next_page=next_page,
            voivodeships=voivodeships,
        )

    @view_config(
        route_name="user_upvotes_export",
        request_method="POST",
        permission="view",
    )
    def export_upvotes(self):
        user = self.request.context.user
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")

        query = (
            select(Company).join(upvotes).filter(user.id == upvotes.c.user_id)
        )

        if order == "asc":
            query = query.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            query = query.order_by(getattr(Company, sort).desc())

        companies = self.request.dbsession.execute(query).scalars()
        response = export_companies_to_xlsx(companies)
        log.info(
            f"Użytkownik {self.request.identity.username} eksportował dane rekomendowanych firm"
        )
        return response

    @view_config(
        route_name="user_upvotes_clear",
        request_method="POST",
        permission="view",
    )
    def clear_upvotes(self):
        user = self.request.context.user
        user.upvotes = []
        log.info(
            f"Użytkownik {self.request.identity.username} wyczyścił wszystkie rekomendacje"
        )
        return HTTPFound(
            location=self.request.route_url(
                "user_upvotes", username=user.username
            )
        )

    @view_config(
        route_name="user_following",
        renderer="user_following.mako",
        permission="view",
    )
    @view_config(
        route_name="user_following_more",
        renderer="investment_more.mako",
        permission="view",
    )
    def following(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "added")
        order = self.request.params.get("order", "asc")
        now = datetime.datetime.now()

        stmt = (
            select(Investment)
            .join(following)
            .filter(user.id == following.c.user_id)
        )

        if filter == "inprogress":
            stmt = stmt.filter(Investment.deadline > now.date())
        elif filter == "completed":
            stmt = stmt.filter(Investment.deadline < now.date())

        if order == "asc":
            stmt = stmt.order_by(getattr(Investment, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Investment, sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_following_more",
            username=user.username,
            _query={
                "page": page + 1,
                "filter": filter,
                "sort": sort,
                "order": order,
            },
        )

        return dict(
            user=user,
            filter=filter,
            sort=sort,
            order=order,
            paginator=paginator,
            next_page=next_page,
        )

    @view_config(
        route_name="user_following_export",
        request_method="POST",
        permission="view",
    )
    def export_following(self):
        user = self.request.context.user
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "added")
        order = self.request.params.get("order", "asc")
        now = datetime.datetime.now()

        query = (
            select(Investment)
            .join(following)
            .filter(user.id == following.c.user_id)
        )

        if filter == "inprogress":
            query = query.filter(Investment.deadline > now.date())
        elif filter == "completed":
            query = query.filter(Investment.deadline < now.date())

        if order == "asc":
            query = query.order_by(getattr(Investment, sort).asc())
        elif order == "desc":
            query = query.order_by(getattr(Investment, sort).desc())

        investments = self.request.dbsession.execute(query).scalars()
        response = export_investments_to_xlsx(investments)
        log.info(
            f"Użytkownik {self.request.identity.username} eksportował dane obserwowanych inwestycji"
        )
        return response

    @view_config(
        route_name="user_following_clear",
        request_method="POST",
        permission="view",
    )
    def clear_following(self):
        user = self.request.context.user
        user.following = []
        log.info(
            f"Użytkownik {self.request.identity.username} wyczyścił wszystkie obserwowane inwestycje"
        )
        return HTTPFound(
            location=self.request.route_url(
                "user_following", username=user.username
            )
        )
