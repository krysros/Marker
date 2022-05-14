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
    Investment,
)
from ..paginator import get_paginator
from ..export import export_investments_to_xlsx


log = logging.getLogger(__name__)


class InvestmentView(object):
    def __init__(self, request):
        self.request = request

    @property
    def investment_form(self):
        def check_name(node, value):
            exists = self.request.dbsession.execute(
                select(Investment).filter_by(name=value)
            ).scalar_one_or_none()
            current_id = self.request.matchdict.get("investment_id", None)
            if current_id:
                current_id = int(current_id)
            if exists and current_id != exists.id:
                raise colander.Invalid(
                    node, "Ta nazwa inwestycji jest już zajęta"
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
                title="Nazwa inwestycji",
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
                title="Firma",
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
                title="Termin",
            )

        schema = Schema().bind(request=self.request)
        submit_btn = deform.form.Button(name="submit", title="Zapisz")
        return deform.Form(schema, buttons=(submit_btn,))

    def _get_company(self, name):
        return self.request.dbsession.execute(
            select(Company).filter_by(name=name)
        ).scalar_one()

    @view_config(
        route_name="investment_all",
        renderer="investment_all.mako",
        permission="view",
    )
    @view_config(
        route_name="investment_more",
        renderer="investment_more.mako",
        permission="view",
    )
    def all(self):
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        stmt = select(Investment)

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
            "investment_more",
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
        route_name="investment_view",
        renderer="investment_view.mako",
        permission="view",
    )
    def view(self):
        investment = self.request.context.investment
        return {"investment": investment, "title": investment.name}

    @view_config(
        route_name="investment_add", renderer="form.mako", permission="edit"
    )
    def add(self):
        form = self.investment_form
        appstruct = {}
        rendered_form = None

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                rendered_form = e.render()
            else:
                investment = Investment(
                    name=appstruct["name"],
                    city=appstruct["city"],
                    voivodeship=appstruct["voivodeship"],
                    company=self._get_company(appstruct["company"]),
                    link=appstruct["link"],
                    deadline=appstruct["deadline"],
                )
                investment.created_by = self.request.identity
                self.request.dbsession.add(investment)
                self.request.session.flash("success:Dodano do bazy danych")
                log.info(
                    f"Użytkownik {self.request.identity.username} dodał inwestycję {investment.name}"
                )
                next_url = self.request.route_url("investment_all")
                return HTTPSeeOther(location=next_url)

        if rendered_form is None:
            rendered_form = form.render(appstruct=appstruct)
        reqts = form.get_widget_resources()

        return dict(
            heading="Dodaj inwestycję",
            rendered_form=rendered_form,
            css_links=reqts["css"],
            js_links=reqts["js"],
        )

    @view_config(
        route_name="investment_edit", renderer="form.mako", permission="edit"
    )
    def edit(self):
        investment = self.request.context.investment
        form = self.investment_form
        rendered_form = None

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                rendered_form = e.render()
            else:
                investment.name = appstruct["name"]
                investment.city = appstruct["city"]
                investment.voivodeship = appstruct["voivodeship"]
                investment.company = self._get_company(appstruct["company"])
                investment.link = appstruct["link"]
                investment.deadline = appstruct["deadline"]
                investment.updated_by = self.request.identity
                self.request.session.flash("success:Zmiany zostały zapisane")
                next_url = self.request.route_url(
                    "investment_view",
                    investment_id=investment.id,
                    slug=investment.slug,
                )
                log.info(
                    f"Użytkownik {self.request.identity.username} zmienił dane inwestycji {investment.name}"
                )
                return HTTPSeeOther(location=next_url)

        appstruct = {
            "name": investment.name,
            "city": investment.city,
            "voivodeship": investment.voivodeship,
            "company": investment.company.name if investment.company else "",
            "link": investment.link,
            "deadline": investment.deadline,
        }

        if rendered_form is None:
            rendered_form = form.render(appstruct=appstruct)
        reqts = form.get_widget_resources()

        return dict(
            heading="Edytuj dane inwestycji",
            rendered_form=rendered_form,
            css_links=reqts["css"],
            js_links=reqts["js"],
        )

    @view_config(
        route_name="investment_delete",
        request_method="POST",
        permission="edit",
    )
    def delete(self):
        investment = self.request.context.investment
        investment_id = investment.id
        investment_name = investment.name
        self.request.dbsession.delete(investment)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(
            f"Użytkownik {self.request.identity.username} usunął inwestycję {investment_name}"
        )
        next_url = self.request.route_url("home")
        return HTTPSeeOther(location=next_url)

    @view_config(
        route_name="investment_select",
        request_method="GET",
        renderer="json",
    )
    def select(self):
        term = self.request.params.get("term")
        items = self.request.dbsession.execute(
            select(Investment).query.filter(
                Investment.name.ilike("%" + term + "%")
            )
        ).scalars()
        data = [i.name for i in items]
        return data

    @view_config(
        route_name="investment_search",
        renderer="investment_search.mako",
        permission="view",
    )
    def search(self):
        voivodeships = dict(VOIVODESHIPS)
        return {"voivodeships": voivodeships}

    @view_config(
        route_name="investment_results",
        renderer="investment_results.mako",
        permission="view",
    )
    @view_config(
        route_name="investment_results_more",
        renderer="investment_more.mako",
        permission="view",
    )
    def results(self):
        name = self.request.params.get("name")
        city = self.request.params.get("city")
        voivodeship = self.request.params.get("voivodeship")
        page = int(self.request.params.get("page", 1))
        voivodeships = dict(VOIVODESHIPS)
        stmt = (
            select(Investment)
            .filter(Investment.name.ilike("%" + name + "%"))
            .filter(Investment.city.ilike("%" + city + "%"))
            .filter(Investment.voivodeship.ilike("%" + voivodeship + "%"))
            .order_by(Investment.name)
        )

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "investment_results_more",
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

    @view_config(route_name="investment_export", permission="view")
    def export(self):
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        query = select(Investment)

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
            f"Użytkownik {self.request.identity.username} eksportował dane inwestycji"
        )
        return response

    @view_config(
        route_name="investment_follow",
        request_method="POST",
        renderer="string",
        permission="view",
    )
    def follow(self):
        investment = self.request.context.investment
        if investment in self.request.identity.following:
            self.request.identity.following.remove(investment)
            return '<span class="fa fa-eye-slash fa-lg"></span>'
        else:
            self.request.identity.following.append(investment)
            return '<span class="fa fa-eye fa-lg"></span>'
