import logging

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import func, select

from ..dropdown import Dd, Dropdown
from ..export import export_vcard
from ..forms import ContactForm, ContactSearchForm
from ..forms.select import DROPDOWN_ORDER, DROPDOWN_SORT
from ..models import Contact
from ..paginator import get_paginator

log = logging.getLogger(__name__)


class ContactView:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="contact_all", renderer="contact_all.mako", permission="view")
    @view_config(
        route_name="contact_more",
        renderer="contact_more.mako",
        permission="view",
    )
    def all(self):
        page = int(self.request.params.get("page", 1))
        name = self.request.params.get("name", None)
        role = self.request.params.get("role", None)
        phone = self.request.params.get("phone", None)
        email = self.request.params.get("email", None)
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        dropdown_sort = dict(DROPDOWN_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        stmt = select(Contact)

        if name:
            stmt = stmt.filter(Contact.name.ilike("%" + name + "%"))

        if role:
            stmt = stmt.filter(Contact.role.ilike("%" + role + "%"))

        if phone:
            stmt = stmt.filter(Contact.phone.ilike("%" + phone + "%"))

        if email:
            stmt = stmt.filter(Contact.email.ilike("%" + email + "%"))

        if order == "asc":
            stmt = stmt.order_by(getattr(Contact, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Contact, sort).desc())

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
            "role": role,
            "phone": phone,
            "email": email,
        }

        next_page = self.request.route_url(
            "contact_more",
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

        # Recreate the search form to display the search criteria
        form = None
        if any(x for x in search_query.values() if x):
            form = ContactSearchForm(**search_query)

        return {
            "search_query": search_query,
            "form": form,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
        }

    @view_config(
        route_name="contact_view", renderer="contact_view.mako", permission="view"
    )
    def view(self):
        contact = self.request.context.contact
        return {"contact": contact, "title": contact.name}

    @view_config(
        route_name="contact_edit", renderer="contact_form.mako", permission="edit"
    )
    def edit(self):
        contact = self.request.context.contact
        form = ContactForm(self.request.POST, contact)
        if self.request.method == "POST" and form.validate():
            form.populate_obj(contact)
            contact.updated_by = self.request.identity
            self.request.session.flash("success:Zmiany zostały zapisane")
            next_url = self.request.route_url(
                "contact_view", contact_id=contact.id, slug=contact.slug
            )
            log.info(f"Użytkownik {self.request.identity.name} zmienił dane kontaktowe")
            return HTTPSeeOther(location=next_url)
        return {"heading": "Edytuj kontakt", "form": form}

    @view_config(route_name="contact_delete", request_method="POST", permission="edit")
    def delete(self):
        contact = self.request.context.contact
        self.request.dbsession.delete(contact)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(f"Użytkownik {self.request.identity.name} usunął kontakt")
        next_url = self.request.route_url("home")
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="delete_contact",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def delete_contact(self):
        contact = self.request.context.contact
        if contact.company:
            event = "contactCompanyEvent"
        elif contact.project:
            event = "contactProjectEvent"
        self.request.dbsession.delete(contact)
        log.info(f"Użytkownik {self.request.identity.name} usunął kontakt")
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": event}
        return ""

    @view_config(
        route_name="contact_search",
        renderer="contact_form.mako",
        permission="view",
    )
    def search(self):
        form = ContactSearchForm(self.request.POST)
        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "contact_all",
                    _query={
                        "name": form.name.data,
                        "role": form.role.data,
                        "phone": form.phone.data,
                        "email": form.email.data,
                    },
                )
            )
        return {"heading": "Znajdź kontakt", "form": form}

    @view_config(route_name="contact_vcard", permission="view")
    def vcard(self):
        contact = self.request.context.contact
        response = export_vcard(contact)
        return response