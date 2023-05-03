import logging

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import func, select

from ..forms import ContactForm, ContactSearchForm, ContactFilterForm
from ..forms.select import ORDER_CRITERIA, SORT_CRITERIA
from ..models import Contact
from ..utils.dropdown import Dd, Dropdown
from ..utils.export import response_vcard
from ..utils.paginator import get_paginator

log = logging.getLogger(__name__)


class ContactFilter:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class ContactView:
    def __init__(self, request):
        self.request = request

    @view_config(
        route_name="contact_all", renderer="contact_all.mako", permission="view"
    )
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
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        search_query = {}
        stmt = select(Contact)

        if name:
            stmt = stmt.filter(Contact.name.ilike("%" + name + "%"))
            search_query["name"] = name

        if role:
            stmt = stmt.filter(Contact.role.ilike("%" + role + "%"))
            search_query["role"] = role

        if phone:
            stmt = stmt.filter(Contact.phone.ilike("%" + phone + "%"))
            search_query["phone"] = phone

        if email:
            stmt = stmt.filter(Contact.email.ilike("%" + email + "%"))
            search_query["email"] = email

        if _filter == "companies":
            stmt = stmt.filter(Contact.company)
            search_query["filter"] = _filter
        elif _filter == "projects":
            stmt = stmt.filter(Contact.project)
            search_query["filter"] = _filter

        if _order == "asc":
            stmt = stmt.order_by(getattr(Contact, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Contact, _sort).desc())

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "contact_more",
            _query={
                **search_query,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
                "page": page + 1,
            },
        )

        filter_obj = ContactFilter(**search_query)
        filter_form = ContactFilterForm(self.request.GET, filter_obj, request=self.request)

        dd_sort = Dropdown(
            self.request, sort_criteria, Dd.SORT, search_query, _filter, _sort, _order
        )
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, search_query, _filter, _sort, _order
        )

        return {
            "search_query": search_query,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "form": filter_form,
        }

    @view_config(
        route_name="contact_count",
        renderer="json",
        permission="view",
    )
    def count(self):
        return self.request.dbsession.execute(
            select(func.count()).select_from(select(Contact))
        ).scalar()

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
        _ = self.request.translate
        contact = self.request.context.contact
        form = ContactForm(self.request.POST, contact)
        if self.request.method == "POST" and form.validate():
            form.populate_obj(contact)
            contact.updated_by = self.request.identity
            self.request.session.flash(_("success:Changes have been saved"))
            next_url = self.request.route_url(
                "contact_view", contact_id=contact.id, slug=contact.slug
            )
            log.info(_("User %s changed contact details") % self.request.identity.name)
            return HTTPSeeOther(location=next_url)
        return {"heading": _("Edit contact"), "form": form}

    @view_config(route_name="contact_delete", request_method="POST", permission="edit")
    def delete(self):
        _ = self.request.translate
        contact = self.request.context.contact
        self.request.dbsession.delete(contact)
        self.request.session.flash(_("success:Removed from the database"))
        log.info(_("The user %s deleted the contact") % self.request.identity.name)
        next_url = self.request.route_url("home")
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="contact_del_row",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def del_row(self):
        _ = self.request.translate
        contact = self.request.context.contact
        self.request.dbsession.delete(contact)
        log.info(_("The user %s deleted the company") % self.request.identity.name)
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": "contactEvent"}
        return ""

    @view_config(
        route_name="contact_search",
        renderer="contact_form.mako",
        permission="view",
    )
    def search(self):
        _ = self.request.translate
        form = ContactSearchForm(self.request.POST)
        search_query = {}
        for fieldname, value in form.data.items():
            if value and fieldname != "submit":
                search_query[fieldname] = value

        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "contact_all",
                    _query=search_query,
                )
            )
        return {"heading": _("Find a contact"), "form": form}

    @view_config(route_name="contact_vcard", permission="view")
    def vcard(self):
        contact = self.request.context.contact
        response = response_vcard(contact)
        return response

    @view_config(
        route_name="contact_check",
        request_method="POST",
        renderer="json",
        permission="view",
    )
    def check(self):
        contact = self.request.context.contact
        selected_contacts = self.request.identity.selected_contacts

        if contact in selected_contacts:
            selected_contacts.remove(contact)
            return {"checked": False}
        else:
            selected_contacts.append(contact)
            return {"checked": True}
