import csv
import logging
from io import StringIO
from uuid import uuid4

from pyramid.httpexceptions import HTTPFound, HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import delete, func, or_, select

from ..forms import ContactFilterForm, ContactForm, ContactImportForm, ContactSearchForm
from ..forms.select import CATEGORIES, ORDER_CRITERIA, SORT_CRITERIA_CONTACTS
from ..models import Comment, Company, Contact, Project, Tag, selected_contacts
from ..utils.export import response_vcard, vcard_template
from ..utils.geo import location
from ..utils.paginator import get_paginator
from . import (
    Filter,
    enforce_delete_rate_limit,
    handle_bulk_selection,
    is_bulk_select_request,
    set_select_all_state,
    sort_column,
)

log = logging.getLogger(__name__)


GOOGLE_CONTACTS_REQUIRED_COLUMNS = {
    "Organization Name": ("Organization Name", "Organization 1 - Name"),
    "First Name": ("First Name", "Given Name"),
    "E-mail 1 - Value": ("E-mail 1 - Value",),
    "Phone 1 - Value": ("Phone 1 - Value",),
    "Labels": ("Labels", "Group Membership"),
}


class ContactView:
    def __init__(self, request):
        self.request = request

    def _normalized_tags(self):
        seen = set()
        tags = []
        for value in self.request.params.getall("tag"):
            name = value.strip()
            if name and name not in seen:
                seen.add(name)
                tags.append(name)
        return tags

    def _stmt_contacts_by_tags(self, tags):
        stmt = (
            select(Contact)
            .distinct()
            .order_by(Contact.created_at.desc(), Contact.id.desc())
        )

        if tags:
            stmt = stmt.filter(
                or_(
                    Contact.company.has(Company.tags.any(Tag.name.in_(tags))),
                    Contact.project.has(Project.tags.any(Tag.name.in_(tags))),
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
        category = self.request.params.get("category", "companies")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA_CONTACTS)
        order_criteria = dict(ORDER_CRITERIA)
        categories = dict(CATEGORIES)
        q = {}
        stmt = select(Contact)

        if name:
            stmt = stmt.filter(Contact.name.ilike("%" + name + "%"))
            q["name"] = name

        if role:
            stmt = stmt.filter(Contact.role.ilike("%" + role + "%"))
            q["role"] = role

        if phone:
            stmt = stmt.filter(Contact.phone.ilike("%" + phone + "%"))
            q["phone"] = phone

        if email:
            stmt = stmt.filter(Contact.email.ilike("%" + email + "%"))
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

        if color:
            stmt = stmt.filter(Contact.color == color)
            q["color"] = color

        q["sort"] = _sort
        q["order"] = _order

        if _sort in {"country", "subdivision"}:
            if category == "projects":
                stmt = stmt.join(Contact.project)
                if _order == "asc":
                    stmt = stmt.order_by(sort_column(Project, _sort).asc(), Contact.id)
                elif _order == "desc":
                    stmt = stmt.order_by(sort_column(Project, _sort).desc(), Contact.id)
            else:
                stmt = stmt.join(Contact.company)
                if _order == "asc":
                    stmt = stmt.order_by(sort_column(Company, _sort).asc(), Contact.id)
                elif _order == "desc":
                    stmt = stmt.order_by(sort_column(Company, _sort).desc(), Contact.id)
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
        template = vcard_template()
        vcard = template.render(contact=contact)
        vcard = vcard.replace("\r", r"\r").replace("\n", r"\n")
        return {"contact": contact, "title": contact.name, "vcard": vcard}

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
        blocked_response = enforce_delete_rate_limit(self.request, records_to_delete=1)
        if blocked_response:
            return blocked_response
        contact = self.request.context.contact
        stmt = delete(selected_contacts).where(
            selected_contacts.c.contact_id == contact.id
        )
        self.request.dbsession.execute(stmt)
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
        blocked_response = enforce_delete_rate_limit(self.request, records_to_delete=1)
        if blocked_response:
            return blocked_response
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
        q = {}

        if not tags:
            return HTTPSeeOther(location=self.request.route_url("contact_search_tags"))

        q["tag"] = tags

        paginator = []
        counter = 0
        next_page = self.request.route_url(
            "contact_search_tags_results_more",
            _query={
                **q,
                "page": page + 1,
            },
        )

        stmt = self._stmt_contacts_by_tags(tags)

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

        return {
            "q": q,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "tags": tags,
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
        contact = self.request.context.contact
        selected_contacts = self.request.identity.selected_contacts
        set_select_all_state(self.request, False)

        if contact in selected_contacts:
            selected_contacts.remove(contact)
            return {"checked": False}
        else:
            selected_contacts.append(contact)
            return {"checked": True}

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

            reader, headers = self._parse_csv(csv_file)

            if not reader:
                self.request.session.flash(
                    _(
                        "warning:Could not read CSV file. Please upload a valid UTF-8, comma-separated CSV."
                    )
                )
                return HTTPFound(location=referrer)

            missing_columns = self._missing_google_contacts_columns(headers)
            if missing_columns:
                self.request.session.flash(
                    _(
                        "warning:CSV structure is incompatible with Google Contacts. "
                        "Missing columns: %s"
                    )
                    % ", ".join(missing_columns)
                )
                return HTTPFound(location=referrer)

            imported_count = 0
            skipped_count = 0
            for row in reader:
                if self._add_row(row):
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

    def _parse_csv(self, file):
        try:
            data = file.read()
            if isinstance(data, bytes):
                try:
                    # utf-8-sig strips BOM when present.
                    text = data.decode("utf-8-sig")
                except UnicodeDecodeError:
                    text = data.decode("utf-8", errors="replace")
            else:
                text = str(data)
        except Exception:
            return None, set()

        f = StringIO(text)
        sample = text[:4096]
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel

        if getattr(dialect, "delimiter", ",") != ",":
            return None, set()

        reader = csv.DictReader(f, dialect=dialect)
        if reader.fieldnames:
            reader.fieldnames = [
                self._normalize_csv_header(header) for header in reader.fieldnames
            ]
        headers = set(reader.fieldnames or [])
        return reader, headers

    def _missing_google_contacts_columns(self, headers):
        available_headers = {
            self._normalize_csv_header(header) for header in (headers or [])
        }
        missing_columns = []

        for display_name, aliases in GOOGLE_CONTACTS_REQUIRED_COLUMNS.items():
            if not any(alias in available_headers for alias in aliases):
                missing_columns.append(display_name)

        return missing_columns

    @staticmethod
    def _normalize_csv_header(header):
        if header is None:
            return ""
        return str(header).lstrip("\ufeff").strip()

    @staticmethod
    def _csv_row_value(row, *columns):
        for column in columns:
            value = row.get(column)
            if value is None:
                continue

            value = value.strip()
            if value:
                return value

        for column in columns:
            value = row.get(column)
            if value is not None:
                return value.strip()

        return ""

    @staticmethod
    def _same_contact_data(contact, name, role, phone, email):
        return (
            (contact.name or "") == name
            and (contact.role or "") == role
            and (contact.phone or "") == phone
            and (contact.email or "") == email
        )

    def _company_has_same_contact(self, company, name, role, phone, email):
        for existing_contact in company.contacts:
            if self._same_contact_data(
                existing_contact,
                name=name,
                role=role,
                phone=phone,
                email=email,
            ):
                return True

        existing_contact_id = self.request.dbsession.execute(
            select(Contact.id)
            .where(Contact.company_id == company.id)
            .where(Contact.name == name)
            .where(func.coalesce(Contact.role, "") == role)
            .where(func.coalesce(Contact.phone, "") == phone)
            .where(func.coalesce(Contact.email, "") == email)
            .limit(1)
        ).scalar_one_or_none()

        return existing_contact_id is not None

    def _add_row(self, row):
        # Prepare Company

        company_name = self._csv_row_value(
            row,
            "Organization Name",
            "Organization 1 - Name",
        )

        if not company_name:
            return False

        street = self._csv_row_value(row, "Address 1 - Street")

        postcode = self._csv_row_value(row, "Address 1 - Postal Code")

        city = self._csv_row_value(row, "Address 1 - City")

        subdivision = self._csv_row_value(row, "Address 1 - Region")

        country = self._csv_row_value(row, "Address 1 - Country")

        website = self._csv_row_value(row, "Website 1 - Value")

        company = self.request.dbsession.execute(
            select(Company).filter_by(name=company_name)
        ).scalar_one_or_none()
        if not company:
            company = Company(
                name=company_name,
                street=street,
                postcode=postcode,
                city=city,
                subdivision=subdivision,
                country=country,
                website=website,
                color="",
                NIP="",
                REGON="",
                KRS="",
                court="",
            )
            loc = location(
                street=street,
                city=city,
                # state=getattr(
                #     pycountry.subdivisions.get(code=subdivision), "name", ""
                # ),
                country=country,
                postalcode=postcode,
            )
            if loc is not None:
                company.latitude = loc["lat"]
                company.longitude = loc["lon"]

            company.created_by = self.request.identity
            self.request.dbsession.add(company)
            self.request.dbsession.flush()

        # Prepare Contact

        first_name = self._csv_row_value(row, "First Name", "Given Name", "Name")
        prefix = self._csv_row_value(row, "Name Prefix")
        middle_name = self._csv_row_value(row, "Middle Name", "Additional Name")
        last_name = self._csv_row_value(row, "Last Name", "Family Name")
        suffix = self._csv_row_value(row, "Name Suffix")

        name_parts = []
        if prefix:
            name_parts.append(prefix)
        if first_name:
            name_parts.append(first_name.title())
        if middle_name:
            name_parts.append(middle_name.title())
        if last_name:
            name_parts.append(last_name.title())
        if suffix:
            name_parts.append(suffix)

        name = " ".join(name_parts).strip()

        if not name:
            return False

        role = self._csv_row_value(
            row,
            "Organization Title",
            "Organization 1 - Title",
        )
        if not role:
            role = self._csv_row_value(
                row,
                "Organization Department",
                "Organization 1 - Department",
            )

        phone = self._csv_row_value(row, "Phone 1 - Value")

        email = self._csv_row_value(row, "E-mail 1 - Value")

        if not "@" in email:
            email = ""

        if self._company_has_same_contact(company, name, role, phone, email):
            return False

        # Prepare Tags

        labels = self._csv_row_value(row, "Labels", "Group Membership")
        tags = [
            label.strip()
            for label in labels.split(":::")
            if label.strip() and not label.strip().startswith("*")
        ]

        for tag_name in tags:
            tag = self.request.dbsession.execute(
                select(Tag).filter_by(name=tag_name)
            ).scalar_one_or_none()
            if not tag:
                tag = Tag(tag_name)
                tag.created_by = self.request.identity
            if tag not in company.tags:
                company.tags.append(tag)

        # Prepare Comments

        comment = self._csv_row_value(row, "Notes")

        if comment:
            comment = Comment(comment=comment)
            comment.created_by = self.request.identity
            company.comments.append(comment)

        contact = Contact(
            name=name,
            role=role,
            phone=phone,
            email=email,
            color="",
        )
        contact.created_by = self.request.identity

        if contact not in company.contacts:
            company.contacts.append(contact)
            return True

        return False
