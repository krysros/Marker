import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther

from sqlalchemy import (
    select,
    func,
)

from ..models import (
    Tag,
    Company,
    recommended,
)
from ..forms import TagForm, TagSearchForm
from ..paginator import get_paginator
from ..export import export_companies_to_xlsx
from ..forms.select import (
    COLORS,
    STATES,
    DROPDOWN_SORT_COMPANIES,
    DROPDOWN_SORT,
    DROPDOWN_ORDER,
)
from ..dropdown import Dropdown, Dd

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
        name = self.request.params.get("name", None)
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        dropdown_sort = dict(DROPDOWN_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        stmt = select(Tag)

        if name:
            stmt = stmt.filter(Tag.name.ilike("%" + name + "%"))

        if order == "asc":
            stmt = stmt.order_by(getattr(Tag, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Tag, sort).desc())

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        search_query = {"name": name}

        next_page = self.request.route_url(
            "tag_more",
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
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
        }

    @view_config(
        route_name="tag_view",
        renderer="tag_view.mako",
        permission="view",
    )
    def view(self):
        tag = self.request.context.tag
        return {"tag": tag, "title": tag.name}

    @view_config(
        route_name="tag_map",
        renderer="tag_map.mako",
        permission="view",
    )
    def map(self):
        tag = self.request.context.tag
        url = self.request.route_url("tag_json", tag_id=tag.id, slug=tag.slug)
        return {"tag": tag, "url": url}

    @view_config(
        route_name="tag_json",
        renderer="json",
        permission="view",
    )
    def tag_json(self):
        tag = self.request.context.tag
        stmt = select(Company).filter(Company.tags.any(name=tag.name))
        companies = self.request.dbsession.execute(stmt).scalars()
        res = [
            {
                "id": company.id,
                "name": company.name,
                "street": company.street,
                "postcode": company.postcode,
                "city": company.city,
                "state": company.state,
                "country": company.country,
                "latitude": company.latitude,
                "longitude": company.longitude,
                "link": company.link,
                "NIP": company.NIP,
                "REGON": company.REGON,
                "KRS": company.KRS,
                "court": company.court,
                "color": company.color,
            }
            for company in companies
        ]
        return res

    @view_config(
        route_name="tag_companies",
        renderer="tag_companies.mako",
        permission="view",
    )
    @view_config(
        route_name="tag_companies_more",
        renderer="company_more.mako",
        permission="view",
    )
    def companies(self):
        tag = self.request.context.tag
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")
        colors = dict(COLORS)
        states = dict(STATES)
        dropdown_sort = dict(DROPDOWN_SORT_COMPANIES)
        dropdown_order = dict(DROPDOWN_ORDER)
        stmt = select(Company)

        if sort == "recommended":
            if order == "asc":
                stmt = (
                    stmt.filter(Company.tags.any(name=tag.name))
                    .join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).asc(), Company.id)
                )
            elif order == "desc":
                stmt = (
                    stmt.filter(Company.tags.any(name=tag.name))
                    .join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).desc(), Company.id)
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

        if filter:
            stmt = stmt.filter(Company.color == filter)

        search_query = {}

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "tag_companies_more",
            tag_id=tag.id,
            slug=tag.slug,
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
            "tag": tag,
            "dd_filter": dd_filter,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "colors": colors,
            "states": states,
            "paginator": paginator,
            "next_page": next_page,
            "title": tag.name,
        }

    @view_config(route_name="tag_companies_export", permission="view")
    def export_companies(self):
        tag = self.request.context.tag
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", "name")
        order = self.request.params.get("order", "asc")
        stmt = select(Company)

        if sort == "recommended":
            if order == "asc":
                stmt = (
                    stmt.filter(Company.tags.any(name=tag.name))
                    .join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).asc(), Company.id)
                )
            elif order == "desc":
                stmt = (
                    stmt.filter(Company.tags.any(name=tag.name))
                    .join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).desc(), Company.id)
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

        if filter:
            stmt = stmt.filter(Company.color == filter)

        companies = self.request.dbsession.execute(stmt).scalars()
        response = export_companies_to_xlsx(companies)
        log.info(f"Użytkownik {self.request.identity.name} eksportował dane firm")
        return response

    @view_config(
        route_name="count_tag_companies",
        renderer="json",
        permission="view",
    )
    def count_tag_companies(self):
        tag = self.request.context.tag
        return tag.count_companies

    @view_config(route_name="tag_add", renderer="basic_form.mako", permission="edit")
    def add(self):
        form = TagForm(self.request.POST, dbsession=self.request.dbsession)

        if self.request.method == "POST" and form.validate():
            tag = Tag(form.name.data)
            tag.created_by = self.request.identity
            self.request.dbsession.add(tag)
            self.request.session.flash("success:Dodano do bazy danych")
            log.info(f"Użytkownik {self.request.identity.name} dodał tag")
            next_url = self.request.route_url("tag_all")
            return HTTPSeeOther(location=next_url)

        return {"heading": "Dodaj tag", "form": form}

    @view_config(route_name="tag_edit", renderer="basic_form.mako", permission="edit")
    def edit(self):
        tag = self.request.context.tag
        form = TagForm(self.request.POST, tag, dbsession=self.request.dbsession)

        if self.request.method == "POST" and form.validate():
            form.populate_obj(tag)
            tag.updated_by = self.request.identity
            self.request.session.flash("success:Zmiany zostały zapisane")
            log.info(f"Użytkownik {self.request.identity.name} zmienił nazwę tagu")
            next_url = self.request.route_url("tag_all")
            return HTTPSeeOther(location=next_url)
        return {"heading": "Edytuj tag", "form": form}

    @view_config(route_name="tag_delete", request_method="POST", permission="edit")
    def delete(self):
        tag = self.request.context.tag
        self.request.dbsession.delete(tag)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(f"Użytkownik {self.request.identity.name} usunął tag")
        next_url = self.request.route_url("home")
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

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
        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "tag_all", _query={"name": form.name.data}
                )
            )
        return {"heading": "Znajdź tag", "form": form}

    @view_config(
        route_name="add_company_to_tag",
        renderer="company_list_tag.mako",
        request_method="POST",
        permission="edit",
    )
    def add_company_to_tag(self):
        tag = self.request.context.tag
        name = self.request.POST.get("name")
        if name:
            company = self.request.dbsession.execute(
                select(Company).filter_by(name=name)
            ).scalar_one_or_none()
            if company not in tag.companies:
                tag.companies.append(company)
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "tagCompanyEvent"}
        return {"tag": tag}
