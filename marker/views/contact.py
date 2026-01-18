import csv
import logging
from io import StringIO

from pyramid.httpexceptions import HTTPFound, HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import func, select, delete

from ..forms import ContactFilterForm, ContactForm, ContactImportForm, ContactSearchForm
from ..forms.select import ORDER_CRITERIA, PARENTS, SORT_CRITERIA
from ..models import Comment, Company, Contact, Tag, selected_contacts
from ..utils.export import response_vcard, vcard_template
from ..utils.geo import location
from ..utils.paginator import get_paginator
from . import Filter

log = logging.getLogger(__name__)


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
        parent = self.request.params.get("parent", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        parents = dict(PARENTS)
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

        if parent == "companies":
            stmt = stmt.filter(Contact.company)
            q["parent"] = parent
        elif parent == "projects":
            stmt = stmt.filter(Contact.project)
            q["parent"] = parent

        q["sort"] = _sort
        q["order"] = _order

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
            "parents": parents,
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

            reader = self._parse_csv(csv_file)

            for row in reader:
                self._add_row(row)

            self.request.session.flash(_("success:CSV file has been imported"))
            log.info(_("User %s imported CSV file") % self.request.identity.name)
            # return HTTPSeeOther(location=next_url)
            return HTTPFound(location=referrer)
        return {"heading": _("Import CSV"), "form": form}

    def _parse_csv(self, file):
        try:
            data = file.read()
            if isinstance(data, bytes):
                text = data.decode("utf-8", errors="replace")
            else:
                text = str(data)
        except Exception as e:
            print("Error reading uploaded CSV:", e)

        f = StringIO(text)
        reader = csv.DictReader(f)
        return reader

    def _add_row(self, row):
        # Prepare Company

        company_name = row["Organization Name"]
        company_name = company_name.strip()

        if not company_name:
            return

        street = row["Address 1 - Street"]
        street = street.strip()

        postcode = row["Address 1 - Postal Code"]
        postcode = postcode.strip()

        city = row["Address 1 - City"]
        city = city.strip()

        subdivision = row["Address 1 - Region"]
        subdivision = subdivision.strip()

        country = row["Address 1 - Country"]
        country = country.strip()

        website = row["Website 1 - Value"]
        website = website.strip()

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

        # Prepare Tags

        labels = row["Labels"]
        tags = [
            label.strip()
            for label in labels.split(":::")
            if not label.strip().startswith("*")
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

        comment = row["Notes"]
        comment = comment.strip()

        if comment:
            comment = Comment(comment=comment)
            comment.created_by = self.request.identity
            company.comments.append(comment)

        # Prepare Contact

        name = row["First Name"].title()
        if row["Name Prefix"]:
            name = row["Name Prefix"] + " " + name
        if row["Middle Name"]:
            name = name + " " + row["Middle Name"].title()
        if row["Last Name"]:
            name = name + " " + row["Last Name"].title()
        if row["Name Suffix"]:
            name = name + " " + row["Name Suffix"]
        name = name.strip()

        if not name:
            return

        role = row["Organization Title"] or row["Organization Department"]
        role = role.strip()

        phone = row["Phone 1 - Value"]
        phone = phone.strip()

        email = row["E-mail 1 - Value"]
        email = email.strip()

        if not "@" in email:
            email = ""

        contact = Contact(
            name=name,
            role=role,
            phone=phone,
            email=email,
        )
        contact.created_by = self.request.identity

        if contact not in company.contacts:
            company.contacts.append(contact)
