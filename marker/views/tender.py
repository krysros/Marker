import datetime
import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
from sqlalchemy import select
import deform
import colander

from deform.schema import CSRFSchema

from .select import VOIVODESHIPS

from ..models import (
    Company,
    Tender,
)
from ..paginator import get_paginator
from ..export import export_tenders_to_xlsx


log = logging.getLogger(__name__)


class TenderView(object):
    def __init__(self, request):
        self.request = request

    @property
    def tender_form(self):
        def check_name(node, value):
            exists = self.request.dbsession.execute(
                select(Tender).filter_by(name=value)
            ).scalar_one_or_none()
            current_id = self.request.matchdict.get("tender_id", None)
            if current_id:
                current_id = int(current_id)
            if exists and current_id != exists.id:
                raise colander.Invalid(
                    node, "Ta nazwa przetargu jest już zajęta"
                )

        def check_company(node, value):
            exists = self.request.dbsession.execute(
                select(Company).filter_by(name=value)
            ).scalar_one_or_none()
            if not exists:
                raise colander.Invalid(
                    node,
                    "Firma o tej nazwie nie występuje w bazie danych",
                )

        company_widget = deform.widget.AutocompleteInputWidget(
            values=self.request.route_url("company_select"),
            min_length=1,
        )

        class Schema(CSRFSchema):
            name = colander.SchemaNode(
                colander.String(),
                title="Nazwa przetargu",
                validator=colander.All(
                    colander.Length(min=3, max=200), check_name
                ),
            )
            city = colander.SchemaNode(
                colander.String(),
                title="Miasto",
                validator=colander.Length(min=3, max=100),
            )
            voivodeship = colander.SchemaNode(
                colander.String(),
                title="Województwo",
                widget=deform.widget.SelectWidget(values=VOIVODESHIPS),
            )
            company = colander.SchemaNode(
                colander.String(),
                title="Zamawiający",
                widget=company_widget,
                validator=check_company,
            )
            link = colander.SchemaNode(
                colander.String(),
                title="Link",
                missing="",
                validaror=colander.All(
                    colander.url, colander.Length(max=2000)
                ),
            )
            deadline = colander.SchemaNode(
                colander.Date(),
                title="Termin składania ofert",
            )

        schema = Schema().bind(request=self.request)
        submit_btn = deform.form.Button(name="submit", title="Zapisz")
        return deform.Form(schema, buttons=(submit_btn,))

    def _get_company(self, name):
        return self.request.dbsession.execute(
            select(Company).filter_by(name=name)
        ).scalar_one()

    @view_config(
        route_name="tender_all", renderer="tender_all.mako", permission="view"
    )
    @view_config(
        route_name="tender_more",
        renderer="tender_more.mako",
        permission="view",
    )
    def all(self):
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "added")
        order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        stmt = select(Tender)

        if filter == "inprogress":
            stmt = stmt.filter(Tender.deadline > now.date())
        elif filter == "completed":
            stmt = stmt.filter(Tender.deadline < now.date())

        if order == "asc":
            stmt = stmt.order_by(getattr(Tender, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Tender, sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "tender_more",
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
            paginator=paginator,
            next_page=next_page,
        )

    @view_config(
        route_name="tender_view",
        renderer="tender_view.mako",
        permission="view",
    )
    def view(self):
        tender = self.request.context.tender
        return {"tender": tender, "title": tender.name}

    @view_config(
        route_name="tender_add", renderer="form.mako", permission="edit"
    )
    def add(self):
        form = self.tender_form
        appstruct = {}
        rendered_form = None

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                rendered_form = e.render()
            else:
                tender = Tender(
                    name=appstruct["name"],
                    city=appstruct["city"],
                    voivodeship=appstruct["voivodeship"],
                    company=self._get_company(appstruct["company"]),
                    link=appstruct["link"],
                    deadline=appstruct["deadline"],
                )
                tender.added_by = self.request.identity
                self.request.dbsession.add(tender)
                self.request.session.flash("success:Dodano do bazy danych")
                log.info(
                    f"Użytkownik {self.request.identity.username} dodał przetarg {tender.name}"
                )
                next_url = self.request.route_url("tender_all")
                return HTTPSeeOther(location=next_url)

        if rendered_form is None:
            rendered_form = form.render(appstruct=appstruct)
        reqts = form.get_widget_resources()

        return dict(
            heading="Dodaj przetarg",
            rendered_form=rendered_form,
            css_links=reqts["css"],
            js_links=reqts["js"],
        )

    @view_config(
        route_name="tender_edit", renderer="form.mako", permission="edit"
    )
    def edit(self):
        tender = self.request.context.tender
        form = self.tender_form
        rendered_form = None

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                rendered_form = e.render()
            else:
                tender.name = appstruct["name"]
                tender.city = appstruct["city"]
                tender.voivodeship = appstruct["voivodeship"]
                tender.company = self._get_company(appstruct["company"])
                tender.link = appstruct["link"]
                tender.deadline = appstruct["deadline"]
                tender.edited_by = self.request.identity
                self.request.session.flash("success:Zmiany zostały zapisane")
                next_url = self.request.route_url(
                    "tender_view", tender_id=tender.id, slug=tender.slug
                )
                log.info(
                    f"Użytkownik {self.request.identity.username} zmienił dane przetargu {tender.name}"
                )
                return HTTPSeeOther(location=next_url)

        appstruct = {
            "name": tender.name,
            "city": tender.city,
            "voivodeship": tender.voivodeship,
            "company": tender.company.name if tender.company else "",
            "link": tender.link,
            "deadline": tender.deadline,
        }

        if rendered_form is None:
            rendered_form = form.render(appstruct=appstruct)
        reqts = form.get_widget_resources()

        return dict(
            heading="Edytuj dane przetargu",
            rendered_form=rendered_form,
            css_links=reqts["css"],
            js_links=reqts["js"],
        )

    @view_config(
        route_name="tender_delete", request_method="POST", permission="edit"
    )
    def delete(self):
        tender = self.request.context.tender
        tender_id = tender.id
        tender_name = tender.name
        self.request.dbsession.delete(tender)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(
            f"Użytkownik {self.request.identity.username} usunął przetarg {tender_name}"
        )
        next_url = self.request.route_url("home")
        return HTTPSeeOther(location=next_url)

    @view_config(
        route_name="tender_select",
        request_method="GET",
        renderer="json",
    )
    def select(self):
        term = self.request.params.get("term")
        items = self.request.dbsession.execute(
            select(Tender).query.filter(Tender.name.ilike("%" + term + "%"))
        ).scalars()
        data = [i.name for i in items]
        return data

    @view_config(
        route_name="tender_search",
        renderer="tender_search.mako",
        permission="view",
    )
    def search(self):
        voivodeships = dict(VOIVODESHIPS)
        return {"voivodeships": voivodeships}

    @view_config(
        route_name="tender_results",
        renderer="tender_results.mako",
        permission="view",
    )
    @view_config(
        route_name="tender_results_more",
        renderer="tender_more.mako",
        permission="view",
    )
    def results(self):
        name = self.request.params.get("name")
        city = self.request.params.get("city")
        voivodeship = self.request.params.get("voivodeship")
        page = int(self.request.params.get("page", 1))
        voivodeships = dict(VOIVODESHIPS)
        stmt = (
            select(Tender)
            .filter(Tender.name.ilike("%" + name + "%"))
            .filter(Tender.city.ilike("%" + city + "%"))
            .filter(Tender.voivodeship.ilike("%" + voivodeship + "%"))
            .order_by(Tender.name)
        )

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "tender_results_more",
            _query={
                "name": name,
                "city": city,
                "voivodeship": voivodeship,
                "page": page + 1,
            },
        )
        return {
            "paginator": paginator,
            "next_page": next_page,
            "voivodeships": voivodeships,
        }

    @view_config(route_name="tender_export", permission="view")
    def export(self):
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "added")
        order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        query = select(Tender)

        if filter == "inprogress":
            query = query.filter(Tender.deadline > now.date())
        elif filter == "completed":
            query = query.filter(Tender.deadline < now.date())

        if order == "asc":
            query = query.order_by(getattr(Tender, sort).asc())
        elif order == "desc":
            query = query.order_by(getattr(Tender, sort).desc())

        tenders = self.request.dbsession.execute(query).scalars()
        response = export_tenders_to_xlsx(tenders)
        log.info(
            f"Użytkownik {self.request.identity.username} eksportował dane przetargów"
        )
        return response

    @view_config(
        route_name="tender_follow",
        request_method="POST",
        renderer="string",
        permission="view",
    )
    def follow(self):
        tender = self.request.context.tender
        if tender in self.request.identity.following:
            self.request.identity.following.remove(tender)
            return '<span class="fa fa-eye-slash fa-lg"></span>'
        else:
            self.request.identity.following.append(tender)
            return '<span class="fa fa-eye fa-lg"></span>'
