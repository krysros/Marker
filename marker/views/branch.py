import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther

from sqlalchemy import (
    select,
    func,
)

import deform
import colander

from ..models import (
    Branch,
    Company,
    upvotes,
)
from deform.schema import CSRFSchema
from ..paginator import get_paginator
from ..export import export_companies_to_xlsx


log = logging.getLogger(__name__)


class BranchView(object):
    def __init__(self, request):
        self.request = request

    @property
    def branch_form(self):
        def check_name(node, value):
            exists = self.request.dbsession.execute(
                select(Branch).filter_by(name=value)
            ).scalar_one_or_none()
            current_id = self.request.matchdict.get("branch_id", None)
            if current_id:
                current_id = int(current_id)
            if exists and current_id != exists.id:
                raise colander.Invalid(node, "Ta nazwa branży jest już zajęta")

        class Schema(CSRFSchema):
            name = colander.SchemaNode(
                colander.String(),
                title="Nazwa branży",
                validator=colander.All(
                    colander.Length(min=3, max=50), check_name
                ),
            )

        schema = Schema().bind(request=self.request)
        submit_btn = deform.form.Button(name="submit", title="Zapisz")
        return deform.Form(schema, buttons=(submit_btn,))

    @view_config(
        route_name="branch_all", renderer="branch_all.mako", permission="view"
    )
    @view_config(
        route_name="branch_more",
        renderer="branch_more.mako",
        permission="view",
    )
    def all(self):
        page = int(self.request.params.get("page", 1))
        sort = self.request.params.get("sort", "added")
        order = self.request.params.get("order", "desc")
        stmt = select(Branch)

        if order == "asc":
            stmt = stmt.order_by(getattr(Branch, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Branch, sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "branch_more",
            _query={"sort": sort, "order": order, "page": page + 1},
        )

        return dict(
            sort=sort,
            order=order,
            paginator=paginator,
            next_page=next_page,
        )

    @view_config(
        route_name="branch_view",
        renderer="branch_view.mako",
        permission="view",
    )
    @view_config(
        route_name="branch_view_more",
        renderer="company_more.mako",
        permission="view",
    )
    def view(self):
        from .select import VOIVODESHIPS

        branch = self.request.context.branch
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")
        voivodeships = dict(VOIVODESHIPS)
        stmt = select(Company)

        if sort == "upvotes":
            if order == "asc":
                stmt = (
                    stmt.filter(Company.branches.any(name=branch.name))
                    .join(upvotes)
                    .group_by(Company)
                    .order_by(
                        func.count(upvotes.c.company_id).asc(), Company.id
                    )
                )
            elif order == "desc":
                stmt = (
                    stmt.filter(Company.branches.any(name=branch.name))
                    .join(upvotes)
                    .group_by(Company)
                    .order_by(
                        func.count(upvotes.c.company_id).desc(), Company.id
                    )
                )
        else:
            if order == "asc":
                stmt = stmt.filter(
                    Company.branches.any(name=branch.name)
                ).order_by(getattr(Company, sort).asc(), Company.id)
            elif order == "desc":
                stmt = stmt.filter(
                    Company.branches.any(name=branch.name)
                ).order_by(getattr(Company, sort).desc(), Company.id)

        if filter in list(voivodeships):
            stmt = stmt.filter(Company.voivodeship == filter)

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "branch_view_more",
            branch_id=branch.id,
            slug=branch.slug,
            _query={
                "page": page + 1,
                "filter": filter,
                "sort": sort,
                "order": order,
            },
        )

        return dict(
            branch=branch,
            sort=sort,
            order=order,
            filter=filter,
            paginator=paginator,
            next_page=next_page,
            voivodeships=voivodeships,
            title=branch.name,
        )

    @view_config(
        route_name="branch_export", request_method="POST", permission="view"
    )
    def export(self):
        from .select import VOIVODESHIPS

        branch = self.request.context.branch
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")
        voivodeships = dict(VOIVODESHIPS)
        query = select(Company)

        if sort == "upvotes":
            if order == "asc":
                query = (
                    query.filter(Company.branches.any(name=branch.name))
                    .join(upvotes)
                    .group_by(Company)
                    .order_by(
                        func.count(upvotes.c.company_id).asc(), Company.id
                    )
                )
            elif order == "desc":
                query = (
                    query.filter(Company.branches.any(name=branch.name))
                    .join(upvotes)
                    .group_by(Company)
                    .order_by(
                        func.count(upvotes.c.company_id).desc(), Company.id
                    )
                )
        else:
            if order == "asc":
                query = query.filter(
                    Company.branches.any(name=branch.name)
                ).order_by(getattr(Company, sort).asc(), Company.id)
            elif order == "desc":
                query = query.filter(
                    Company.branches.any(name=branch.name)
                ).order_by(getattr(Company, sort).desc(), Company.id)

        if filter in list(voivodeships):
            query = query.filter(Company.voivodeship == filter)

        companies = self.request.dbsession.execute(query).scalars()
        response = export_companies_to_xlsx(companies)
        log.info(
            f"Użytkownik {self.request.identity.username} eksportował dane firm z branży {branch.name}"
        )
        return response

    @view_config(
        route_name="branch_add", renderer="form.mako", permission="edit"
    )
    def add(self):
        form = self.branch_form
        appstruct = {}
        rendered_form = None

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                rendered_form = e.render()
            else:
                branch = Branch(appstruct["name"])
                branch.added_by = self.request.identity
                self.request.dbsession.add(branch)
                self.request.session.flash("success:Dodano do bazy danych")
                log.info(
                    f"Użytkownik {self.request.identity.username} dodał branżę {branch.name}"
                )
                next_url = self.request.route_url("branch_all")
                return HTTPSeeOther(location=next_url)

        if rendered_form is None:
            rendered_form = form.render(appstruct=appstruct)

        return dict(
            heading="Dodaj branżę",
            rendered_form=rendered_form,
        )

    @view_config(
        route_name="branch_edit", renderer="form.mako", permission="edit"
    )
    def edit(self):
        branch = self.request.context.branch
        form = self.branch_form
        rendered_form = None

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                rendered_form = e.render()
            else:
                branch.name = appstruct["name"]
                branch.edited_by = self.request.identity
                self.request.session.flash("success:Zmiany zostały zapisane")
                next_url = self.request.route_url(
                    "branch_edit", branch_id=branch.id, slug=branch.slug
                )
                log.info(
                    f"Użytkownik {self.request.identity.username} zmienił nazwę branży {branch.name}"
                )
                return HTTPSeeOther(location=next_url)

        appstruct = {"name": branch.name}
        if rendered_form is None:
            rendered_form = form.render(appstruct=appstruct)

        return dict(
            heading="Edytuj dane branży",
            rendered_form=rendered_form,
        )

    @view_config(
        route_name="branch_delete", request_method="POST", permission="edit"
    )
    def delete(self):
        branch = self.request.context.branch
        branch_id = branch.id
        branch_name = branch.name
        self.request.dbsession.delete(branch)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(
            f"Użytkownik {self.request.identity.username} usunął branżę {branch_name}"
        )
        next_url = self.request.route_url("home")
        return HTTPSeeOther(location=next_url)

    @view_config(
        route_name="branch_select",
        request_method="GET",
        renderer="json",
    )
    def select(self):
        term = self.request.params.get("term")
        items = self.request.dbsession.execute(
            select(Branch).filter(Branch.name.ilike("%" + term + "%"))
        ).scalars()
        data = [i.name for i in items]
        return data

    @view_config(
        route_name="branch_search",
        renderer="branch_search.mako",
        permission="view",
    )
    def search(self):
        return {}

    @view_config(
        route_name="branch_results",
        renderer="branch_results.mako",
        permission="view",
    )
    @view_config(
        route_name="branch_results_more",
        renderer="branch_more.mako",
        permission="view",
    )
    def results(self):
        name = self.request.params.get("name")
        page = int(self.request.params.get("page", 1))
        stmt = (
            select(Branch)
            .filter(Branch.name.ilike("%" + name + "%"))
            .order_by(Branch.name)
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "branch_results_more", _query={"name": name, "page": page + 1}
        )
        return {"paginator": paginator, "next_page": next_page}
