import logging

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import func, select

from ..dropdown import Dd, Dropdown
from ..export import export_vcard
from ..forms import PersonForm, PersonSearchForm
from ..forms.select import DROPDOWN_ORDER, DROPDOWN_SORT
from ..models import Person
from ..paginator import get_paginator

log = logging.getLogger(__name__)


class PersonView:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="person_all", renderer="person_all.mako", permission="view")
    @view_config(
        route_name="person_more",
        renderer="person_more.mako",
        permission="view",
    )
    def all(self):
        page = int(self.request.params.get("page", 1))
        name = self.request.params.get("name", None)
        position = self.request.params.get("position", None)
        phone = self.request.params.get("phone", None)
        email = self.request.params.get("email", None)
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        dropdown_sort = dict(DROPDOWN_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        stmt = select(Person)

        if name:
            stmt = stmt.filter(Person.name.ilike("%" + name + "%"))

        if position:
            stmt = stmt.filter(Person.position.ilike("%" + position + "%"))

        if phone:
            stmt = stmt.filter(Person.phone.ilike("%" + phone + "%"))

        if email:
            stmt = stmt.filter(Person.email.ilike("%" + email + "%"))

        if order == "asc":
            stmt = stmt.order_by(getattr(Person, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Person, sort).desc())

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        search_query = {
            "name": name,
            "position": position,
            "phone": phone,
            "email": email,
        }

        next_page = self.request.route_url(
            "person_more",
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

        if any(x is not None for x in search_query.values()):
            heading = "Wyniki wyszukiwania"
        else:
            heading = ""

        form = PersonSearchForm(**search_query)

        return {
            "search_query": search_query,
            "form": form,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "heading": heading,
        }

    @view_config(
        route_name="person_view", renderer="person_view.mako", permission="view"
    )
    def view(self):
        person = self.request.context.person
        return {"person": person, "title": person.name}

    @view_config(
        route_name="person_edit", renderer="person_form.mako", permission="edit"
    )
    def edit(self):
        person = self.request.context.person
        form = PersonForm(self.request.POST, person)
        if self.request.method == "POST" and form.validate():
            form.populate_obj(person)
            person.updated_by = self.request.identity
            self.request.session.flash("success:Zmiany zostały zapisane")
            next_url = self.request.route_url(
                "person_view", person_id=person.id, slug=person.slug
            )
            log.info(f"Użytkownik {self.request.identity.name} zmienił dane osoby")
            return HTTPSeeOther(location=next_url)
        return {"heading": "Edytuj dane osoby", "form": form}

    @view_config(route_name="person_delete", request_method="POST", permission="edit")
    def delete(self):
        person = self.request.context.person
        self.request.dbsession.delete(person)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(f"Użytkownik {self.request.identity.name} usunął osobę")
        next_url = self.request.route_url("home")
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="delete_person",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def delete_person(self):
        person = self.request.context.person
        if person.company:
            event = "personCompanyEvent"
        elif person.project:
            event = "personProjectEvent"
        self.request.dbsession.delete(person)
        log.info(f"Użytkownik {self.request.identity.name} usunął osobę")
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": event}
        return ""

    @view_config(
        route_name="person_search",
        renderer="person_form.mako",
        permission="view",
    )
    def search(self):
        form = PersonSearchForm(self.request.POST)
        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "person_all",
                    _query={
                        "name": form.name.data,
                        "position": form.position.data,
                        "phone": form.phone.data,
                        "email": form.email.data,
                    },
                )
            )
        return {"heading": "Znajdź osobę", "form": form}

    @view_config(route_name="person_vcard", permission="view")
    def vcard(self):
        person = self.request.context.person
        response = export_vcard(person)
        return response
