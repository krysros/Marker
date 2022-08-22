import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
from sqlalchemy import select
from ..models import Person
from ..paginator import get_paginator
from ..forms import PersonForm
from ..forms.select import (
    DROPDOWN_SORT,
    DROPDOWN_ORDER,
)

log = logging.getLogger(__name__)


class PersonView(object):
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
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        dropdown_sort = dict(DROPDOWN_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        stmt = select(Person)

        if order == "asc":
            stmt = stmt.order_by(getattr(Person, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Person, sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "person_more",
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
        route_name="person_view", renderer="person_view.mako", permission="view"
    )
    def view(self):
        person = self.request.context.person
        return {"person": person}

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
            next_url = self.request.route_url("person_view", person_id=person.id)
            log.info(
                f"Użytkownik {self.request.identity.name} zmienił dane osoby {person.name}"
            )
            return HTTPSeeOther(location=next_url)

        return dict(
            heading="Edytuj dane osoby",
            form=form,
        )

    @view_config(route_name="person_delete", request_method="POST", permission="edit")
    def delete(self):
        person = self.request.context.person
        person_name = person.name
        self.request.dbsession.delete(person)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(f"Użytkownik {self.request.identity.name} usunął osobę {person_name}")
        next_url = self.request.route_url("home")
        return HTTPSeeOther(location=next_url)
