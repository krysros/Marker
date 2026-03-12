import logging
from uuid import uuid4

from pyramid.httpexceptions import HTTPFound, HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import delete, func, or_, select

from ..forms import ContactFilterForm, ContactForm, ContactImportForm, ContactSearchForm
from ..forms.select import CATEGORIES, ORDER_CRITERIA, SORT_CRITERIA_CONTACTS
from ..models import Company, Contact, Project, Tag, selected_contacts
from ..utils.contact_csv_import import (
    GoogleContactsCsvImporter,
    missing_google_contacts_columns,
    parse_google_contacts_csv,
)
from ..utils.export import response_vcard, vcard_template
from ..utils.geo import location
from ..utils.paginator import get_paginator
from . import (
    Filter,
    clear_selected_rows,
    contains_ci,
    handle_bulk_selection,
    is_bulk_select_request,
    polish_sort_expression,
    set_select_all_state,
    sort_column,
    toggle_selected_item,
)

log = logging.getLogger(__name__)


class ContactView:
    def __init__(self, request):
        self.request = request

    def _normalized_tags(self):
        seen = set()
        tags = []
        for value in self.request.params.getall("tag"):
            name = value.strip()
            normalized = name.lower()
            if name and normalized not in seen:
                seen.add(normalized)
                tags.append(name)
        return tags

    def _stmt_contacts_by_tags(self, tags):
        stmt = select(Contact).distinct()

        if tags:
            normalized_tags = [tag.lower() for tag in tags]
            stmt = stmt.filter(
                or_(
                    Contact.company.has(
                        Company.tags.any(func.lower(Tag.name).in_(normalized_tags))
                    ),
                    Contact.project.has(
                        Project.tags.any(func.lower(Tag.name).in_(normalized_tags))
                    ),
                )
            )

        return stmt

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
        subdivision = self.request.params.getall("subdivision")
        country = self.request.params.get("country", None)
        color = self.request.params.get("color", None)
        category = self.request.params.get("category", "")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA_CONTACTS)
        order_criteria = dict(ORDER_CRITERIA)
        categories = dict(CATEGORIES)
        q = {}
        stmt = select(Contact)

        if name:
            stmt = stmt.filter(contains_ci(Contact.name, name))
            q["name"] = name

        if role:
            stmt = stmt.filter(contains_ci(Contact.role, role))
            q["role"] = role

        if phone:
            stmt = stmt.filter(contains_ci(Contact.phone, phone))
            q["phone"] = phone

        if email:
            stmt = stmt.filter(contains_ci(Contact.email, email))
            q["email"] = email

        if category == "companies":
            stmt = stmt.filter(Contact.company)
            q["category"] = category
            if country:
                stmt = stmt.filter(Contact.company.has(Company.country == country))
                q["country"] = country
            if subdivision:
                stmt = stmt.filter(
                    Contact.company.has(Company.subdivision.in_(subdivision))
                )
                q["subdivision"] = list(subdivision)
        elif category == "projects":
            stmt = stmt.filter(Contact.project)
            q["category"] = category
            if country:
                stmt = stmt.filter(Contact.project.has(Project.country == country))
                q["country"] = country
            if subdivision:
                stmt = stmt.filter(
                    Contact.project.has(Project.subdivision.in_(subdivision))
                )
                q["subdivision"] = list(subdivision)
        else:
            if country:
                stmt = stmt.filter(
                    or_(
                        Contact.company.has(Company.country == country),
                        Contact.project.has(Project.country == country),
                    )
                )
                q["country"] = country
            if subdivision:
                stmt = stmt.filter(
                    or_(
                        Contact.company.has(Company.subdivision.in_(subdivision)),
                        Contact.project.has(Project.subdivision.in_(subdivision)),
                    )
                )
                q["subdivision"] = list(subdivision)

        if color:
            stmt = stmt.filter(Contact.color == color)
            q["color"] = color

        q["sort"] = _sort
        q["order"] = _order

        if _sort in {"city", "country", "subdivision"}:
            if category == "projects":
                stmt = stmt.join(Contact.project)
                if _order == "asc":
                    stmt = stmt.order_by(sort_column(Project, _sort).asc(), Contact.id)
                elif _order == "desc":
                    stmt = stmt.order_by(sort_column(Project, _sort).desc(), Contact.id)
            elif category == "companies":
                stmt = stmt.join(Contact.company)
                if _order == "asc":
                    stmt = stmt.order_by(sort_column(Company, _sort).asc(), Contact.id)
                elif _order == "desc":
                    stmt = stmt.order_by(sort_column(Company, _sort).desc(), Contact.id)
            else:
                stmt = stmt.outerjoin(Contact.project).outerjoin(Contact.company)
                relation_sort = func.coalesce(
                    getattr(Project, _sort), getattr(Company, _sort)
                )
                if _order == "asc":
                    stmt = stmt.order_by(
                        polish_sort_expression(relation_sort).asc(), Contact.id
                    )
                elif _order == "desc":
                    stmt = stmt.order_by(
                        polish_sort_expression(relation_sort).desc(), Contact.id
                    )
        elif _sort == "color":
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Contact, _sort).asc(), Contact.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Contact, _sort).desc(), Contact.id)
        else:
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Contact, _sort).asc(), Contact.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Contact, _sort).desc(), Contact.id)

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_contacts
            )

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
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = ContactFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "categories": categories,
            "form": form,
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
        is_contact_selected = (
            self.request.dbsession.execute(
                select(1)
                .select_from(selected_contacts)
                .where(
                    selected_contacts.c.user_id == self.request.identity.id,
                    selected_contacts.c.contact_id == contact.id,
                )
                .limit(1)
            ).first()
            is not None
        )
        template = vcard_template()
        vcard = template.render(contact=contact)
        vcard = vcard.replace("\r", r"\r").replace("\n", r"\n")
        return {
            "contact": contact,
            "is_contact_selected": is_contact_selected,
            "title": contact.name,
            "vcard": vcard,
        }

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
        clear_selected_rows(
            self.request,
            selected_contacts,
            selected_contacts.c.contact_id,
            [contact.id],
        )
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
        clear_selected_rows(
            self.request,
            selected_contacts,
            selected_contacts.c.contact_id,
            [contact.id],
        )
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
        q = {}
        for fieldname, value in form.data.items():
            if value:
                q[fieldname] = value

        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "contact_all",
                    _query=q,
                )
            )
        return {"heading": _("Find a contact"), "form": form}

    @view_config(
        route_name="contact_search_tags",
        renderer="contact_search_tags.mako",
        permission="view",
    )
    def search_tags(self):
        _ = self.request.translate
        tags = self._normalized_tags()
        q = {}

        if tags:
            q["tag"] = tags

        if self.request.method == "POST":
            return HTTPSeeOther(
                location=self.request.route_url("contact_search_tags_results", _query=q)
            )

        return {
            "tags": tags,
            "heading": _("Search contacts"),
        }

    @view_config(
        route_name="contact_search_tags_results",
        renderer="contact_search_tags_results.mako",
        permission="view",
    )
    @view_config(
        route_name="contact_search_tags_results_more",
        renderer="contact_more.mako",
        permission="view",
    )
    def search_tags_results(self):
        _ = self.request.translate
        tags = self._normalized_tags()
        page = int(self.request.params.get("page", 1))
        name = self.request.params.get("name", None)
        role = self.request.params.get("role", None)
        phone = self.request.params.get("phone", None)
        email = self.request.params.get("email", None)
        subdivision = self.request.params.getall("subdivision")
        country = self.request.params.get("country", None)
        color = self.request.params.get("color", None)
        category = self.request.params.get("category", "")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA_CONTACTS)
        order_criteria = dict(ORDER_CRITERIA)
        categories = dict(CATEGORIES)
        q = {}

        if not tags:
            return HTTPSeeOther(location=self.request.route_url("contact_search_tags"))

        q["tag"] = tags

        stmt = self._stmt_contacts_by_tags(tags)

        if name:
            stmt = stmt.filter(contains_ci(Contact.name, name))
            q["name"] = name

        if role:
            stmt = stmt.filter(contains_ci(Contact.role, role))
            q["role"] = role

        if phone:
            stmt = stmt.filter(contains_ci(Contact.phone, phone))
            q["phone"] = phone

        if email:
            stmt = stmt.filter(contains_ci(Contact.email, email))
            q["email"] = email

        if category == "companies":
            stmt = stmt.filter(Contact.company)
            q["category"] = category
            if country:
                stmt = stmt.filter(Contact.company.has(Company.country == country))
                q["country"] = country
            if subdivision:
                stmt = stmt.filter(
                    Contact.company.has(Company.subdivision.in_(subdivision))
                )
                q["subdivision"] = list(subdivision)
        elif category == "projects":
            stmt = stmt.filter(Contact.project)
            q["category"] = category
            if country:
                stmt = stmt.filter(Contact.project.has(Project.country == country))
                q["country"] = country
            if subdivision:
                stmt = stmt.filter(
                    Contact.project.has(Project.subdivision.in_(subdivision))
                )
                q["subdivision"] = list(subdivision)
        else:
            if country:
                stmt = stmt.filter(
                    or_(
                        Contact.company.has(Company.country == country),
                        Contact.project.has(Project.country == country),
                    )
                )
                q["country"] = country
            if subdivision:
                stmt = stmt.filter(
                    or_(
                        Contact.company.has(Company.subdivision.in_(subdivision)),
                        Contact.project.has(Project.subdivision.in_(subdivision)),
                    )
                )
                q["subdivision"] = list(subdivision)

        if color:
            stmt = stmt.filter(Contact.color == color)
            q["color"] = color

        q["sort"] = _sort
        q["order"] = _order

        if _sort in {"city", "country", "subdivision"}:
            if category == "projects":
                stmt = stmt.join(Contact.project)
                if _order == "asc":
                    stmt = stmt.order_by(sort_column(Project, _sort).asc(), Contact.id)
                elif _order == "desc":
                    stmt = stmt.order_by(sort_column(Project, _sort).desc(), Contact.id)
            elif category == "companies":
                stmt = stmt.join(Contact.company)
                if _order == "asc":
                    stmt = stmt.order_by(sort_column(Company, _sort).asc(), Contact.id)
                elif _order == "desc":
                    stmt = stmt.order_by(sort_column(Company, _sort).desc(), Contact.id)
            else:
                stmt = stmt.outerjoin(Contact.project).outerjoin(Contact.company)
                relation_sort = func.coalesce(
                    getattr(Project, _sort), getattr(Company, _sort)
                )
                if _order == "asc":
                    stmt = stmt.order_by(
                        polish_sort_expression(relation_sort).asc(), Contact.id
                    )
                elif _order == "desc":
                    stmt = stmt.order_by(
                        polish_sort_expression(relation_sort).desc(), Contact.id
                    )
        elif _sort == "color":
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Contact, _sort).asc(), Contact.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Contact, _sort).desc(), Contact.id)
        else:
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Contact, _sort).asc(), Contact.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Contact, _sort).desc(), Contact.id)

        paginator = []
        counter = 0
        next_page = self.request.route_url(
            "contact_search_tags_results_more",
            _query={
                **q,
                "page": page + 1,
            },
        )

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_contacts
            )

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        obj = Filter(**q)
        form = ContactFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "tags": tags,
            "categories": categories,
            "form": form,
            "heading": _("Search contacts"),
        }

    @view_config(
        route_name="contact_search_tags_input",
        renderer="contact_tag_input_row.mako",
        permission="view",
    )
    def search_tags_input(self):
        return {
            "row_id": uuid4().hex,
            "value": "",
        }

    @view_config(
        route_name="contact_search_tags_input_remove",
        renderer="string",
        permission="view",
    )
    def search_tags_input_remove(self):
        return ""

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
        contact_id = self.request.context.contact.id
        set_select_all_state(self.request, False)
        checked = toggle_selected_item(
            self.request,
            selected_contacts,
            selected_contacts.c.contact_id,
            contact_id,
        )
        return {"checked": checked}

    @view_config(
        route_name="contact_import_csv",
        renderer="contact_import.mako",
        permission="edit",
    )
    def contact_import_csv(self):
        _ = self.request.translate
        form = ContactImportForm(self.request.POST)
        if self.request.method == "POST":
            referrer = self.request.referrer or self.request.route_url("home")
            csv_file = self.request.POST["csv_file"].file
            if not csv_file:
                return HTTPFound(location=referrer)

            reader, headers = parse_google_contacts_csv(csv_file)

            if not reader:
                self.request.session.flash(
                    _(
                        "warning:Could not read CSV file. Please upload a valid UTF-8, comma-separated CSV."
                    )
                )
                return HTTPFound(location=referrer)

            missing_columns = missing_google_contacts_columns(headers)
            if missing_columns:
                self.request.session.flash(
                    _(
                        "warning:CSV structure is incompatible with Google Contacts. "
                        "Missing columns: %s"
                    )
                    % ", ".join(missing_columns)
                )
                return HTTPFound(location=referrer)

            importer = self._get_csv_importer()
            imported_count = 0
            skipped_count = 0
            for row in reader:
                if importer.add_row(row):
                    imported_count += 1
                else:
                    skipped_count += 1

            self.request.session.flash(
                _(
                    "success:CSV file has been imported. Contacts added: %s. "
                    "Skipped rows: %s"
                )
                % (imported_count, skipped_count)
            )
            log.info(
                _("User %s imported CSV file (%s contacts, %s skipped)")
                % (self.request.identity.name, imported_count, skipped_count)
            )
            # return HTTPSeeOther(location=next_url)
            return HTTPFound(location=referrer)
        return {"heading": _("Import CSV"), "form": form}

    def _get_csv_importer(self):
        return GoogleContactsCsvImporter(
            dbsession=self.request.dbsession,
            identity=self.request.identity,
            geocode=location,
        )

