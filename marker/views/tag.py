import logging
from pyramid.csrf import new_csrf_token
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther

from sqlalchemy import (
    select,
    func,
)

from ..models import (
    Tag,
    Company,
    recomended,
)
from ..forms import TagForm, TagSearchForm
from ..paginator import get_paginator
from ..export import export_companies_to_xlsx
from ..forms.select import (
    DROPDOWN_SORT,
    DROPDOWN_ORDER,
)

log = logging.getLogger(__name__)


class TagView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="tag_all", renderer="tag_all.mako", permission="view")
    @view_config(
        route_name="tag_more",
        renderer="tag_more.mako",
        permission="view",
    )
    def all(self):
        page = int(self.request.params.get("page", 1))
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        dropdown_sort = dict(DROPDOWN_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        stmt = select(Tag)

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
            "tag_more",
            _query={"sort": sort, "order": order, "page": page + 1},
        )

        return dict(
            sort=sort,
            order=order,
            dropdown_sort=dropdown_sort,
            dropdown_order=dropdown_order,
            paginator=paginator,
            next_page=next_page,
        )

    @view_config(
        route_name="tag_view",
        renderer="tag_view.mako",
        permission="view",
    )
    @view_config(
        route_name="tag_view_more",
        renderer="company_more.mako",
        permission="view",
    )
    def view(self):
        from ..forms.select import STATES

        tag = self.request.context.tag
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")
        states = dict(STATES)
        dropdown_sort = dict(DROPDOWN_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        stmt = select(Company)

        if sort == "recomended":
            if order == "asc":
                stmt = (
                    stmt.filter(Company.tags.any(name=tag.name))
                    .join(recomended)
                    .group_by(Company)
                    .order_by(func.count(recomended.c.company_id).asc(), Company.id)
                )
            elif order == "desc":
                stmt = (
                    stmt.filter(Company.tags.any(name=tag.name))
                    .join(recomended)
                    .group_by(Company)
                    .order_by(func.count(recomended.c.company_id).desc(), Company.id)
                )
        else:
            if order == "asc":
                stmt = stmt.filter(Company.tags.any(name=tag.name)).order_by(
                    getattr(Company, sort).asc(), Company.id
                )
            elif order == "desc":
                stmt = stmt.filter(Company.tags.any(name=tag.name)).order_by(
                    getattr(Company, sort).desc(), Company.id
                )

        if filter in list(states):
            stmt = stmt.filter(Company.state == filter)

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "tag_view_more",
            tag_id=tag.id,
            slug=tag.slug,
            _query={
                "page": page + 1,
                "filter": filter,
                "sort": sort,
                "order": order,
            },
        )

        return dict(
            tag=tag,
            sort=sort,
            order=order,
            filter=filter,
            dropdown_sort=dropdown_sort,
            dropdown_order=dropdown_order,
            paginator=paginator,
            next_page=next_page,
            states=states,
            title=tag.name,
        )

    @view_config(route_name="tag_export", request_method="POST", permission="view")
    def export(self):
        from ..forms.select import STATES

        tag = self.request.context.tag
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")
        states = dict(STATES)
        query = select(Company)

        if sort == "recomended":
            if order == "asc":
                query = (
                    query.filter(Company.tags.any(name=tag.name))
                    .join(recomended)
                    .group_by(Company)
                    .order_by(func.count(recomended.c.company_id).asc(), Company.id)
                )
            elif order == "desc":
                query = (
                    query.filter(Company.tags.any(name=tag.name))
                    .join(recomended)
                    .group_by(Company)
                    .order_by(func.count(recomended.c.company_id).desc(), Company.id)
                )
        else:
            if order == "asc":
                query = query.filter(Company.tags.any(name=tag.name)).order_by(
                    getattr(Company, sort).asc(), Company.id
                )
            elif order == "desc":
                query = query.filter(Company.tags.any(name=tag.name)).order_by(
                    getattr(Company, sort).desc(), Company.id
                )

        if filter in list(states):
            query = query.filter(Company.state == filter)

        companies = self.request.dbsession.execute(query).scalars()
        response = export_companies_to_xlsx(companies)
        log.info(
            f"Użytkownik {self.request.identity.name} eksportował dane firm otagowanych {tag.name}"
        )
        return response

    @view_config(route_name="tag_add", renderer="basic_form.mako", permission="edit")
    def add(self):
        form = TagForm(self.request.POST, dbsession=self.request.dbsession)

        if self.request.method == "POST" and form.validate():
            new_csrf_token(self.request)
            tag = Tag(form.name.data)
            tag.created_by = self.request.identity
            self.request.dbsession.add(tag)
            self.request.session.flash("success:Dodano do bazy danych")
            log.info(f"Użytkownik {self.request.identity.name} dodał tag {tag.name}")
            next_url = self.request.route_url("tag_all")
            return HTTPSeeOther(location=next_url)

        return dict(
            heading="Dodaj tag",
            form=form,
        )

    @view_config(route_name="tag_edit", renderer="basic_form.mako", permission="edit")
    def edit(self):
        tag = self.request.context.tag
        form = TagForm(self.request.POST, tag, dbsession=self.request.dbsession)

        if self.request.method == "POST" and form.validate():
            new_csrf_token(self.request)
            form.populate_obj(tag)
            tag.updated_by = self.request.identity
            self.request.session.flash("success:Zmiany zostały zapisane")
            log.info(
                f"Użytkownik {self.request.identity.name} zmienił nazwę tagu {tag.name}"
            )
            next_url = self.request.route_url("tag_all")
            return HTTPSeeOther(location=next_url)

        return dict(
            heading="Edytuj tag",
            form=form,
        )

    @view_config(route_name="tag_delete", request_method="POST", permission="edit")
    def delete(self):
        tag = self.request.context.tag
        tag_name = tag.name
        self.request.dbsession.delete(tag)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(f"Użytkownik {self.request.identity.name} usunął tag {tag_name}")
        next_url = self.request.route_url("home")
        return HTTPSeeOther(location=next_url)

    @view_config(
        route_name="tag_select",
        renderer="tag_datalist.mako",
        request_method="GET",
    )
    def select(self):
        name = self.request.params.get("name")
        tags = []
        if name:
            tags = self.request.dbsession.execute(
                select(Tag).filter(Tag.name.ilike("%" + name + "%"))
            ).scalars()
        return {"tags": tags}

    @view_config(
        route_name="tag_search",
        renderer="basic_form.mako",
        permission="view",
    )
    def search(self):
        form = TagSearchForm(self.request.POST)
        if self.request.method == 'POST' and form.validate():
            return HTTPSeeOther(location=self.request.route_url('tag_results', _query={'name': form.name.data}))
        return dict(
            heading='Znajdź tag',
            form=form,
        )

    @view_config(
        route_name="tag_results",
        renderer="tag_results.mako",
        permission="view",
    )
    @view_config(
        route_name="tag_results_more",
        renderer="tag_more.mako",
        permission="view",
    )
    def results(self):
        name = self.request.params.get("name")
        page = int(self.request.params.get("page", 1))
        stmt = select(Tag).filter(Tag.name.ilike("%" + name + "%")).order_by(Tag.name)
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "tag_results_more", _query={"name": name, "page": page + 1}
        )
        return {"paginator": paginator, "next_page": next_page}
