import logging
from uuid import uuid4

import pycountry
from pyramid.httpexceptions import HTTPNotFound, HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import delete, func, select

from ..forms import (
    ActivityForm,
    CommentForm,
    CompanyFilterForm,
    CompanyForm,
    CompanySearchForm,
    ContactForm,
    ProjectActivityForm,
    TagLinkForm,
)
from ..forms.select import (
    COLORS,
    COMPANY_ROLES,
    COURTS,
    ORDER_CRITERIA,
    SORT_CRITERIA,
    SORT_CRITERIA_COMPANIES,
    SORT_CRITERIA_CONTACTS,
    STAGES,
    USER_ROLES,
    select_countries,
)
from ..models import (
    Activity,
    Comment,
    Company,
    Contact,
    Project,
    Tag,
    User,
    companies_stars,
    companies_tags,
    selected_companies,
    selected_contacts,
    selected_tags,
)
from ..utils.geo import location
from ..utils.paginator import get_paginator
from ..utils.website_autofill import (
    company_autofill_from_website,
    shorten_url_to_hostname,
)
from . import (
    Filter,
    clear_selected_rows,
    contains_ci,
    handle_bulk_selection,
    htmx_refresh_response,
    is_bulk_select_request,
    normalize_ci_expression,
    normalize_ci_value,
    polish_sort_expression,
    set_select_all_state,
    sort_column,
    toggle_selected_item,
)

log = logging.getLogger(__name__)


class CompanyView:
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

    def pills(self, company):
        _ = self.request.translate
        return [
            {
                "title": _("Company"),
                "icon": "buildings",
                "url": self.request.route_url(
                    "company_view", company_id=company.id, slug=company.slug
                ),
                "count": None,
            },
            {
                "title": _("Projects"),
                "icon": "briefcase",
                "url": self.request.route_url(
                    "company_projects", company_id=company.id, slug=company.slug
                ),
                "count": self.request.route_url(
                    "company_count_projects", company_id=company.id, slug=company.slug
                ),
                "event": "assocEvent",
                "init_value": company.count_projects,
            },
            {
                "title": _("Tags"),
                "icon": "tags",
                "url": self.request.route_url(
                    "company_tags", company_id=company.id, slug=company.slug
                ),
                "count": self.request.route_url(
                    "company_count_tags", company_id=company.id, slug=company.slug
                ),
                "event": "tagEvent",
                "init_value": company.count_tags,
            },
            {
                "title": _("Contacts"),
                "icon": "people",
                "url": self.request.route_url(
                    "company_contacts", company_id=company.id, slug=company.slug
                ),
                "count": self.request.route_url(
                    "company_count_contacts", company_id=company.id, slug=company.slug
                ),
                "event": "contactEvent",
                "init_value": company.count_contacts,
            },
            {
                "title": _("Comments"),
                "icon": "chat-left-text",
                "url": self.request.route_url(
                    "company_comments", company_id=company.id, slug=company.slug
                ),
                "count": self.request.route_url(
                    "company_count_comments", company_id=company.id, slug=company.slug
                ),
                "event": "commentEvent",
                "init_value": company.count_comments,
            },
            {
                "title": _("Stars"),
                "icon": "star",
                "url": self.request.route_url(
                    "company_stars", company_id=company.id, slug=company.slug
                ),
                "count": self.request.route_url(
                    "company_count_stars",
                    company_id=company.id,
                    slug=company.slug,
                ),
                "event": "starCompanyEvent",
                "init_value": company.count_stars,
            },
            {
                "title": _("Similar"),
                "icon": "intersect",
                "url": self.request.route_url(
                    "company_similar", company_id=company.id, slug=company.slug
                ),
                "count": self.request.route_url(
                    "company_count_similar", company_id=company.id, slug=company.slug
                ),
                "event": "tagEvent",
                "init_value": company.count_similar,
            },
        ]

    @view_config(
        route_name="company_all",
        renderer="company_all.mako",
        permission="view",
    )
    @view_config(
        route_name="company_more",
        renderer="company_more.mako",
        permission="view",
    )
    @view_config(
        route_name="company_more_contacts",
        renderer="contact_more.mako",
        permission="view",
    )
    def all(self):
        page = int(self.request.params.get("page", 1))
        tags = self._normalized_tags()
        requested_view_mode = self.request.params.get("view", "companies")
        if requested_view_mode not in {"companies", "contacts"}:
            requested_view_mode = "companies"
        # Contact view is available only for tag-based result sets.
        view_mode = requested_view_mode if tags else "companies"
        show_contacts_toggle = bool(tags)
        name = self.request.params.get("name", None)
        street = self.request.params.get("street", None)
        postcode = self.request.params.get("postcode", None)
        city = self.request.params.get("city", None)
        subdivision = [
            value for value in self.request.params.getall("subdivision") if value
        ]
        country = self.request.params.get("country", None)
        website = self.request.params.get("website", None)
        color = self.request.params.get("color", None)
        NIP = self.request.params.get("NIP", None)
        REGON = self.request.params.get("REGON", None)
        KRS = self.request.params.get("KRS", None)
        court = self.request.params.get("court", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA_COMPANIES)
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        q = {}

        stmt = select(Company)

        if tags:
            normalized_tags = [normalize_ci_value(tag) for tag in tags]
            stmt = stmt.filter(
                Company.tags.any(normalize_ci_expression(Tag.name).in_(normalized_tags))
            )
            q["tag"] = tags

        if name:
            normalized_name = normalize_ci_value(name)
            stmt = stmt.filter(
                normalize_ci_expression(Company.name).like("%" + normalized_name + "%")
            )
            q["name"] = name

        if street:
            stmt = stmt.filter(contains_ci(Company.street, street))
            q["street"] = street

        if postcode:
            stmt = stmt.filter(contains_ci(Company.postcode, postcode))
            q["postcode"] = postcode

        if city:
            stmt = stmt.filter(contains_ci(Company.city, city))
            q["city"] = city

        if website:
            stmt = stmt.filter(contains_ci(Company.website, website))
            q["website"] = website

        if subdivision:
            stmt = stmt.filter(Company.subdivision.in_(subdivision))
            q["subdivision"] = list(subdivision)

        if country:
            stmt = stmt.filter(Company.country == country)
            q["country"] = country

        if color:
            stmt = stmt.filter(Company.color == color)
            q["color"] = color

        if NIP:
            stmt = stmt.filter(Company.NIP == NIP)
            q["NIP"] = NIP

        if REGON:
            stmt = stmt.filter(Company.REGON == REGON)
            q["REGON"] = REGON

        if KRS:
            stmt = stmt.filter(Company.KRS == KRS)
            q["KRS"] = KRS

        if court:
            stmt = stmt.filter(Company.court == court)
            q["court"] = court

        if view_mode == "contacts":
            q["view"] = "contacts"

        q["sort"] = _sort
        q["order"] = _order

        if _sort == "stars":
            if _order == "asc":
                stmt = (
                    stmt.join(companies_stars)
                    .group_by(Company.id)
                    .order_by(
                        func.count(companies_stars.c.company_id).asc(), Company.id
                    )
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(companies_stars)
                    .group_by(Company.id)
                    .order_by(
                        func.count(companies_stars.c.company_id).desc(), Company.id
                    )
                )
        elif _sort == "comments":
            if _order == "asc":
                stmt = (
                    stmt.join(Company.comments)
                    .group_by(Company.id)
                    .order_by(func.count(Company.comments).asc())
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(Company.comments)
                    .group_by(Company.id)
                    .order_by(func.count(Company.comments).desc())
                )
        else:
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Company, _sort).asc(), Company.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Company, _sort).desc(), Company.id)

        selected_items = self.request.identity.selected_companies
        if view_mode == "contacts":
            company_ids = stmt.order_by(None).with_only_columns(Company.id).subquery()
            stmt = (
                select(Contact)
                .filter(Contact.company_id.in_(select(company_ids.c.id)))
                .order_by(polish_sort_expression(Contact.name).asc(), Contact.id)
            )
            selected_items = self.request.identity.selected_contacts

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(self.request, stmt, selected_items)

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        obj = Filter(**q)
        form = CompanyFilterForm(self.request.GET, obj, request=self.request)

        next_route = (
            "company_more_contacts" if view_mode == "contacts" else "company_more"
        )
        next_page = self.request.route_url(
            next_route,
            _query={
                **q,
                "page": page + 1,
            },
        )

        contact_q = {"category": "companies"}

        return {
            "q": q,
            "next_page": next_page,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "counter": counter,
            "colors": colors,
            "form": form,
            "view_mode": view_mode,
            "show_contacts_toggle": show_contacts_toggle,
            "contact_q": contact_q,
        }

    @view_config(
        route_name="company_view",
        renderer="company_view.mako",
        permission="view",
    )
    @view_config(
        route_name="company_projects",
        renderer="company_projects.mako",
        permission="view",
    )
    @view_config(
        route_name="company_tags",
        renderer="company_tags.mako",
        permission="view",
    )
    @view_config(
        route_name="company_contacts",
        renderer="company_contacts.mako",
        permission="view",
    )
    def view(self):
        _ = self.request.translate
        company = self.request.context.company
        is_company_selected = (
            self.request.dbsession.execute(
                select(1)
                .select_from(selected_companies)
                .where(
                    selected_companies.c.user_id == self.request.identity.id,
                    selected_companies.c.company_id == company.id,
                )
                .limit(1)
            ).first()
            is not None
        )
        route_name = self.request.matched_route.name
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        q = {"sort": _sort, "order": _order}
        courts = dict(COURTS)
        countries = dict(select_countries())
        stages = dict(STAGES)
        company_roles = dict(COMPANY_ROLES)
        projects_assoc = []
        contacts = []
        tags = []
        bulk_stmt = None
        bulk_selected_items = None

        if route_name == "company_projects":
            sort_criteria = {
                "name": _("Project"),
                "stage": _("Stage"),
                "role": _("Role"),
                "created_at": _("Created at"),
                "updated_at": _("Updated at"),
            }

            allowed_sorts = {"name", "stage", "role", "created_at", "updated_at"}
            if _sort not in allowed_sorts:
                _sort = "name"
                q["sort"] = _sort

            if _order not in {"asc", "desc"}:
                _order = "asc"
                q["order"] = _order

            stmt = (
                select(Activity).join(Project).filter(Activity.company_id == company.id)
            )
            order_column = {
                "name": polish_sort_expression(Project.name),
                "stage": Activity.stage,
                "role": Activity.role,
                "created_at": Project.created_at,
                "updated_at": Project.updated_at,
            }[_sort]
            if _order == "asc":
                stmt = stmt.order_by(order_column.asc(), Activity.project_id)
            else:
                stmt = stmt.order_by(order_column.desc(), Activity.project_id)
            projects_assoc = self.request.dbsession.execute(stmt).scalars().all()
            bulk_stmt = stmt
            bulk_selected_items = self.request.identity.selected_projects

        elif route_name == "company_contacts":
            sort_criteria = dict(SORT_CRITERIA_CONTACTS)

            allowed_sorts = {"name", "role", "created_at", "updated_at"}
            if _sort not in allowed_sorts:
                _sort = "created_at"
                q["sort"] = _sort

            if _order not in {"asc", "desc"}:
                _order = "desc"
                q["order"] = _order

            stmt = select(Contact).filter(Contact.company_id == company.id)
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Contact, _sort).asc(), Contact.id)
            else:
                stmt = stmt.order_by(sort_column(Contact, _sort).desc(), Contact.id)
            contacts = self.request.dbsession.execute(stmt).scalars().all()
            bulk_stmt = stmt
            bulk_selected_items = self.request.identity.selected_contacts
        elif route_name == "company_tags":
            sort_criteria = {
                "name": _("Tag"),
                "created_at": _("Date created"),
                "updated_at": _("Date modified"),
            }

            allowed_sorts = {"name", "created_at", "updated_at"}
            if _sort not in allowed_sorts:
                _sort = "created_at"
                q["sort"] = _sort

            if _order not in {"asc", "desc"}:
                _order = "asc"
                q["order"] = _order

            stmt = (
                select(Tag)
                .join(companies_tags)
                .filter(companies_tags.c.company_id == company.id)
            )
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Tag, _sort).asc(), Tag.id)
            else:
                stmt = stmt.order_by(sort_column(Tag, _sort).desc(), Tag.id)
            tags = self.request.dbsession.execute(stmt).scalars().all()
            bulk_stmt = stmt
            bulk_selected_items = self.request.identity.selected_tags

        if is_bulk_select_request(self.request):
            checked = self.request.params.get("checked", "false").lower() == "true"
            if bulk_stmt is not None and bulk_selected_items is not None:
                return handle_bulk_selection(
                    self.request,
                    bulk_stmt,
                    bulk_selected_items,
                )

            set_select_all_state(self.request, checked)
            return htmx_refresh_response(self.request)

        return {
            "company": company,
            "is_company_selected": is_company_selected,
            "courts": courts,
            "countries": countries,
            "stages": stages,
            "company_roles": company_roles,
            "projects_assoc": projects_assoc,
            "contacts": contacts,
            "tags": tags,
            "q": q,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "title": company.name,
            "company_pills": self.pills(company),
        }

    @view_config(
        route_name="company_map",
        renderer="company_map.mako",
        permission="view",
    )
    def map(self):
        name = self.request.params.get("name", None)
        street = self.request.params.get("street", None)
        postcode = self.request.params.get("postcode", None)
        city = self.request.params.get("city", None)
        subdivision = [
            value for value in self.request.params.getall("subdivision") if value
        ]
        country = self.request.params.get("country", None)
        website = self.request.params.get("website", None)
        color = self.request.params.get("color", None)
        NIP = self.request.params.get("NIP", None)
        REGON = self.request.params.get("REGON", None)
        KRS = self.request.params.get("KRS", None)
        court = self.request.params.get("court", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        q = {}

        stmt = select(Company)

        if name:
            normalized_name = normalize_ci_value(name)
            stmt = stmt.filter(
                normalize_ci_expression(Company.name).like("%" + normalized_name + "%")
            )
            q["name"] = name

        if street:
            stmt = stmt.filter(contains_ci(Company.street, street))
            q["street"] = street

        if postcode:
            stmt = stmt.filter(contains_ci(Company.postcode, postcode))
            q["postcode"] = postcode

        if city:
            stmt = stmt.filter(contains_ci(Company.city, city))
            q["city"] = city

        if website:
            stmt = stmt.filter(contains_ci(Company.website, website))
            q["website"] = website

        if subdivision:
            stmt = stmt.filter(Company.subdivision.in_(subdivision))
            q["subdivision"] = list(subdivision)

        if country:
            stmt = stmt.filter(Company.country == country)
            q["country"] = country

        if color:
            stmt = stmt.filter(Company.color == color)
            q["color"] = color

        if NIP:
            stmt = stmt.filter(Company.NIP == NIP)
            q["NIP"] = NIP

        if REGON:
            stmt = stmt.filter(Company.REGON == REGON)
            q["REGON"] = REGON

        if KRS:
            stmt = stmt.filter(Company.KRS == KRS)
            q["KRS"] = KRS

        if court:
            stmt = stmt.filter(Company.court == court)
            q["court"] = court

        q["sort"] = _sort
        q["order"] = _order

        if _sort == "stars":
            if _order == "asc":
                stmt = (
                    stmt.join(companies_stars)
                    .group_by(Company.id)
                    .order_by(
                        func.count(companies_stars.c.company_id).asc(), Company.id
                    )
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(companies_stars)
                    .group_by(Company.id)
                    .order_by(
                        func.count(companies_stars.c.company_id).desc(), Company.id
                    )
                )
        else:
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Company, _sort).asc(), Company.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Company, _sort).desc(), Company.id)

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        ).scalar()

        url = self.request.route_url("company_json", _query=q)
        return {"url": url, "q": q, "counter": counter}

    @view_config(
        route_name="company_json",
        renderer="json",
        permission="view",
    )
    def company_json(self):
        name = self.request.params.get("name", None)
        street = self.request.params.get("street", None)
        postcode = self.request.params.get("postcode", None)
        city = self.request.params.get("city", None)
        subdivision = self.request.params.get("subdivision", None)
        country = self.request.params.get("country", None)
        website = self.request.params.get("website", None)
        color = self.request.params.get("color", None)
        NIP = self.request.params.get("NIP", None)
        REGON = self.request.params.get("REGON", None)
        KRS = self.request.params.get("KRS", None)
        court = self.request.params.get("court", None)

        stmt = select(Company)

        if name:
            normalized_name = normalize_ci_value(name)
            stmt = stmt.filter(
                normalize_ci_expression(Company.name).like("%" + normalized_name + "%")
            )

        if street:
            stmt = stmt.filter(contains_ci(Company.street, street))

        if postcode:
            stmt = stmt.filter(contains_ci(Company.postcode, postcode))

        if city:
            stmt = stmt.filter(contains_ci(Company.city, city))

        if website:
            stmt = stmt.filter(contains_ci(Company.website, website))

        if subdivision:
            stmt = stmt.filter(Company.subdivision == subdivision)

        if country:
            stmt = stmt.filter(Company.country == country)

        if color:
            stmt = stmt.filter(Company.color == color)

        if NIP:
            stmt = stmt.filter(Company.NIP == NIP)

        if REGON:
            stmt = stmt.filter(Company.REGON == REGON)

        if KRS:
            stmt = stmt.filter(Company.KRS == KRS)

        if court:
            stmt = stmt.filter(Company.court == court)

        companies = self.request.dbsession.execute(stmt).scalars()

        res = [
            {
                "id": company.id,
                "name": company.name,
                "street": company.street,
                "city": company.city,
                "country": company.country,
                "latitude": company.latitude,
                "longitude": company.longitude,
                "color": company.color,
                "url": self.request.route_url(
                    "company_view", company_id=company.id, slug=company.slug
                ),
            }
            for company in companies
        ]
        return res

    @view_config(
        route_name="company_count_tags",
        renderer="json",
        permission="view",
    )
    def count_tags(self):
        company = self.request.context.company
        return company.count_tags

    @view_config(
        route_name="company_count_projects",
        renderer="json",
        permission="view",
    )
    def count_projects(self):
        company = self.request.context.company
        return company.count_projects

    @view_config(
        route_name="company_count_contacts",
        renderer="json",
        permission="view",
    )
    def count_contacts(self):
        company = self.request.context.company
        return company.count_contacts

    @view_config(
        route_name="company_count_comments",
        renderer="json",
        permission="view",
    )
    def count_comments(self):
        company = self.request.context.company
        return company.count_comments

    @view_config(
        route_name="company_count_stars",
        renderer="json",
        permission="view",
    )
    def count_stars(self):
        company = self.request.context.company
        return company.count_stars

    @view_config(
        route_name="company_count_similar",
        renderer="json",
        permission="view",
    )
    def count_similar(self):
        company = self.request.context.company
        return company.count_similar

    @view_config(
        route_name="company_stars",
        renderer="company_stars.mako",
        permission="view",
    )
    @view_config(
        route_name="company_more_stars",
        renderer="user_more.mako",
        permission="view",
    )
    def companies_stars(self):
        _ = self.request.translate
        company = self.request.context.company
        page = int(self.request.params.get("page", 1))
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = {
            "name": _("Name"),
            "fullname": _("Fullname"),
            "email": _("Email"),
            "created_at": _("Date created"),
            "updated_at": _("Date modified"),
        }
        order_criteria = dict(ORDER_CRITERIA)
        q = {"sort": _sort, "order": _order}
        user_roles = dict(USER_ROLES)

        allowed_sorts = {"name", "fullname", "email", "created_at", "updated_at"}
        if _sort not in allowed_sorts:
            _sort = "created_at"
            q["sort"] = _sort

        if _order not in {"asc", "desc"}:
            _order = "desc"
            q["order"] = _order

        stmt = (
            select(User)
            .join(companies_stars)
            .filter(company.id == companies_stars.c.company_id)
        )
        if _order == "asc":
            stmt = stmt.order_by(sort_column(User, _sort).asc(), User.id)
        else:
            stmt = stmt.order_by(sort_column(User, _sort).desc(), User.id)

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "company_more_stars",
            company_id=company.id,
            slug=company.slug,
            _query={
                **q,
                "page": page + 1,
            },
        )
        return {
            "q": q,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "company": company,
            "title": company.name,
            "roles": user_roles,
            "company_pills": self.pills(company),
        }

    @view_config(
        route_name="company_add_tag",
        renderer="company_add_tag.mako",
        permission="edit",
    )
    def add_tag(self):
        _ = self.request.translate
        form = TagLinkForm(self.request.POST, request=self.request)
        company = self.request.context.company

        if self.request.method == "POST" and form.validate():
            created_tag = False
            tag = self.request.dbsession.execute(
                select(Tag).filter_by(name=form.name.data)
            ).scalar_one_or_none()
            if not tag:
                tag = Tag(form.name.data)
                tag.created_by = self.request.identity
                created_tag = True
            if tag not in company.tags:
                company.tags.append(tag)
                if created_tag:
                    self.request.dbsession.flush()
                    clear_selected_rows(
                        self.request,
                        selected_tags,
                        selected_tags.c.tag_id,
                        [tag.id],
                    )
                log.info(
                    _("The user %s has added a tag to the company")
                    % self.request.identity.name
                )
                self.request.session.flash(_("success:Added to the database"))
            next_url = self.request.route_url(
                "company_tags", company_id=company.id, slug=company.slug
            )
            return HTTPSeeOther(location=next_url)
        return {
            "heading": _("Add a tag"),
            "form": form,
            "company": company,
            "company_pills": self.pills(company),
        }

    @view_config(
        route_name="company_add_contact",
        renderer="company_add_contact.mako",
        permission="edit",
    )
    def add_contact(self):
        _ = self.request.translate
        form = ContactForm(self.request.POST, request=self.request)
        company = self.request.context.company

        if self.request.method == "POST" and form.validate():
            contact = Contact(
                name=form.name.data,
                role=form.role.data,
                phone=form.phone.data,
                email=form.email.data,
                color=form.color.data,
            )
            contact.created_by = self.request.identity
            if contact not in company.contacts:
                company.contacts.append(contact)
                self.request.dbsession.flush()
                clear_selected_rows(
                    self.request,
                    selected_contacts,
                    selected_contacts.c.contact_id,
                    [contact.id],
                )
                log.info(
                    _("The user %s has added a contact to the company")
                    % self.request.identity.name
                )
                self.request.session.flash(_("success:Added to the database"))
            next_url = self.request.route_url(
                "company_contacts", company_id=company.id, slug=company.slug
            )
            return HTTPSeeOther(location=next_url)
        return {
            "heading": _("Add a contact"),
            "form": form,
            "company": company,
            "company_pills": self.pills(company),
        }

    @view_config(
        route_name="company_add_comment",
        renderer="company_add_comment.mako",
        permission="edit",
    )
    def company_add_comment(self):
        _ = self.request.translate
        company = self.request.context.company
        form = CommentForm(self.request.POST, request=self.request)
        if self.request.method == "POST" and form.validate():
            comment = Comment(comment=form.comment.data)
            comment.created_by = self.request.identity
            company.comments.append(comment)
            log.info(_("The user %s added a comment") % self.request.identity.name)
            self.request.session.flash(_("success:Added to the database"))
            next_url = self.request.route_url(
                "company_comments", company_id=company.id, slug=company.slug
            )
            return HTTPSeeOther(location=next_url)
        return {
            "heading": _("Add a comment"),
            "form": form,
            "company": company,
            "company_pills": self.pills(company),
        }

    @view_config(
        route_name="company_comments",
        renderer="company_comments.mako",
        permission="view",
    )
    @view_config(
        route_name="company_more_comments",
        renderer="comment_more.mako",
        permission="view",
    )
    def comments(self):
        _ = self.request.translate
        company = self.request.context.company
        page = int(self.request.params.get("page", 1))
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = {
            "created_at": _("Date created"),
            "updated_at": _("Date modified"),
        }
        order_criteria = dict(ORDER_CRITERIA)
        q = {"sort": _sort, "order": _order}

        allowed_sorts = {"created_at", "updated_at"}
        if _sort not in allowed_sorts:
            _sort = "created_at"
            q["sort"] = _sort

        if _order not in {"asc", "desc"}:
            _order = "desc"
            q["order"] = _order

        stmt = select(Comment).filter(Comment.company_id == company.id)
        if _order == "asc":
            stmt = stmt.order_by(sort_column(Comment, _sort).asc(), Comment.id)
        else:
            stmt = stmt.order_by(sort_column(Comment, _sort).desc(), Comment.id)

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "company_more_comments",
            company_id=company.id,
            slug=company.slug,
            _query={
                **q,
                "page": page + 1,
            },
        )

        return {
            "q": q,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "company": company,
            "title": company.name,
            "company_pills": self.pills(company),
        }

    @view_config(
        route_name="company_similar",
        renderer="company_similar.mako",
        permission="view",
    )
    @view_config(
        route_name="company_more_similar",
        renderer="company_more.mako",
        permission="view",
    )
    def similar(self):
        _ = self.request.translate
        company = self.request.context.company
        page = int(self.request.params.get("page", 1))
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = [
            value for value in self.request.params.getall("subdivision") if value
        ]
        _sort = self.request.params.get("sort", "shared_tags")
        _order = self.request.params.get("order", "desc")
        colors = dict(COLORS)
        order_criteria = dict(ORDER_CRITERIA)
        sort_criteria = {"shared_tags": _("Tags"), **dict(SORT_CRITERIA_COMPANIES)}
        q = {}

        allowed_sorts = set(sort_criteria.keys())
        if _sort not in allowed_sorts:
            _sort = "shared_tags"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        # Compute similar companies through association-table self-join.
        # This avoids correlated subqueries over tags that are expensive on large datasets.
        base_tags = companies_tags.alias("base_tags")
        other_tags = companies_tags.alias("other_tags")
        similarity = (
            select(
                other_tags.c.company_id.label("company_id"),
                func.count(func.distinct(base_tags.c.tag_id)).label("shared_tags"),
            )
            .select_from(
                base_tags.join(other_tags, base_tags.c.tag_id == other_tags.c.tag_id)
            )
            .where(
                base_tags.c.company_id == company.id,
                other_tags.c.company_id != company.id,
            )
            .group_by(other_tags.c.company_id)
            .subquery()
        )

        stmt = select(Company).join(similarity, similarity.c.company_id == Company.id)

        if color:
            stmt = stmt.filter(Company.color == color)
            q["color"] = color

        if country:
            stmt = stmt.filter(Company.country == country)
            q["country"] = country

        if subdivision:
            stmt = stmt.filter(Company.subdivision.in_(subdivision))
            q["subdivision"] = list(subdivision)

        q["sort"] = _sort
        q["order"] = _order

        if _sort == "shared_tags":
            if _order == "asc":
                stmt = stmt.order_by(similarity.c.shared_tags.asc(), Company.id)
            else:
                stmt = stmt.order_by(similarity.c.shared_tags.desc(), Company.id)
        elif _sort == "stars":
            if _order == "asc":
                stmt = (
                    stmt.join(companies_stars)
                    .group_by(Company.id)
                    .order_by(
                        func.count(companies_stars.c.company_id).asc(), Company.id
                    )
                )
            else:
                stmt = (
                    stmt.join(companies_stars)
                    .group_by(Company.id)
                    .order_by(
                        func.count(companies_stars.c.company_id).desc(), Company.id
                    )
                )
        elif _sort == "comments":
            if _order == "asc":
                stmt = (
                    stmt.join(Company.comments)
                    .group_by(Company.id)
                    .order_by(func.count(Company.comments).asc())
                )
            else:
                stmt = (
                    stmt.join(Company.comments)
                    .group_by(Company.id)
                    .order_by(func.count(Company.comments).desc())
                )
        elif _order == "asc":
            stmt = stmt.order_by(sort_column(Company, _sort).asc(), Company.id)
        else:
            stmt = stmt.order_by(sort_column(Company, _sort).desc(), Company.id)

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_companies
            )

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        shared_tag_counts = {}
        shared_tag_labels = {}
        if paginator:
            similar_ids = [item.id for item in paginator]
            shared_rows = self.request.dbsession.execute(
                select(similarity.c.company_id, similarity.c.shared_tags).where(
                    similarity.c.company_id.in_(similar_ids)
                )
            ).all()
            shared_tag_counts = {
                company_id: int(shared_tags or 0)
                for company_id, shared_tags in shared_rows
            }

            shared_tag_name_rows = self.request.dbsession.execute(
                select(other_tags.c.company_id, Tag.name)
                .select_from(
                    base_tags.join(
                        other_tags,
                        base_tags.c.tag_id == other_tags.c.tag_id,
                    ).join(Tag, Tag.id == base_tags.c.tag_id)
                )
                .where(
                    base_tags.c.company_id == company.id,
                    other_tags.c.company_id.in_(similar_ids),
                )
                .distinct()
            ).all()

            tag_names_by_company = {}
            for similar_company_id, tag_name in shared_tag_name_rows:
                if not tag_name:
                    continue
                tag_names_by_company.setdefault(similar_company_id, set()).add(tag_name)

            shared_tag_labels = {
                similar_company_id: ", ".join(sorted(names, key=normalize_ci_value))
                for similar_company_id, names in tag_names_by_company.items()
            }

        next_page = self.request.route_url(
            "company_more_similar",
            company_id=company.id,
            slug=company.slug,
            colors=colors,
            _query={
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = CompanyFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "company": company,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "show_shared_tags": True,
            "shared_tag_counts": shared_tag_counts,
            "shared_tag_labels": shared_tag_labels,
            "title": company.name,
            "company_pills": self.pills(company),
            "form": form,
        }

    @view_config(
        route_name="company_add", renderer="company_form.mako", permission="edit"
    )
    def add(self):
        _ = self.request.translate
        form = CompanyForm(self.request.POST, request=self.request)
        countries = dict(select_countries())
        tags = self._normalized_tags()

        if self.request.method == "POST" and form.validate():
            website = form.website.data
            if form.shorten_website.data:
                website = shorten_url_to_hostname(website)
            company = Company(
                name=form.name.data,
                street=form.street.data,
                postcode=form.postcode.data,
                city=form.city.data,
                subdivision=form.subdivision.data,
                country=form.country.data,
                website=website,
                color=form.color.data,
                NIP=form.NIP.data,
                REGON=form.REGON.data,
                KRS=form.KRS.data,
                court=form.court.data,
            )
            loc = location(
                street=form.street.data,
                city=form.city.data,
                # state=getattr(
                #     pycountry.subdivisions.get(code=form.subdivision.data), "name", ""
                # ),
                country=countries.get(form.country.data),
                postalcode=form.postcode.data,
            )
            if loc is not None:
                company.latitude = loc["lat"]
                company.longitude = loc["lon"]

            company.created_by = self.request.identity
            self.request.dbsession.add(company)
            self.request.dbsession.flush()
            clear_selected_rows(
                self.request,
                selected_companies,
                selected_companies.c.company_id,
                [company.id],
            )
            clear_selected_rows(
                self.request,
                companies_stars,
                companies_stars.c.company_id,
                [company.id],
            )

            for tag_name in tags:
                tag = self.request.dbsession.execute(
                    select(Tag).filter_by(name=tag_name)
                ).scalar_one_or_none()
                if not tag:
                    tag = Tag(name=tag_name)
                    tag.created_by = self.request.identity
                if tag not in company.tags:
                    company.tags.append(tag)

            self.request.session.flash(_("success:Added to the database"))
            self.request.session.flash(_("info:Add tags and contacts"))
            log.info(_("The user %s has added a company") % self.request.identity.name)
            next_url = self.request.route_url(
                "company_view", company_id=company.id, slug=company.slug
            )
            return HTTPSeeOther(location=next_url)

        if self.request.query_string:
            form.name.data = self.request.params.get("name", None)
            form.street.data = self.request.params.get("street", None)
            form.postcode.data = self.request.params.get("postcode", None)
            form.city.data = self.request.params.get("city", None)
            form.country.data = self.request.params.get("country", None)
            form.subdivision.data = self.request.params.get("subdivision", None)
            form.website.data = self.request.params.get("website", None)
            form.color.data = self.request.params.get("color", None)
            form.NIP.data = self.request.params.get("NIP", None)
            form.REGON.data = self.request.params.get("REGON", None)
            form.KRS.data = self.request.params.get("KRS", None)

        return {"heading": _("Add a company"), "form": form, "tags": tags}

    @view_config(
        route_name="company_website_autofill",
        renderer="json",
        permission="edit",
    )
    def website_autofill(self):
        website = self.request.params.get("website", "")
        return {"fields": company_autofill_from_website(website)}

    @view_config(
        route_name="company_add_tag_input",
        renderer="company_tag_input_row.mako",
        permission="edit",
    )
    @view_config(
        route_name="company_search_tag_input",
        renderer="company_tag_input_row.mako",
        permission="view",
    )
    def add_tag_input(self):
        route_name = self.request.matched_route.name
        remove_route = (
            "company_search_tag_input_remove"
            if route_name == "company_search_tag_input"
            else "company_add_tag_input_remove"
        )
        return {
            "row_id": uuid4().hex,
            "value": "",
            "remove_route": remove_route,
        }

    @view_config(
        route_name="company_add_tag_input_remove",
        renderer="string",
        permission="edit",
    )
    @view_config(
        route_name="company_search_tag_input_remove",
        renderer="string",
        permission="view",
    )
    def add_tag_input_remove(self):
        return ""

    @view_config(
        route_name="company_edit", renderer="company_form.mako", permission="edit"
    )
    def edit(self):
        _ = self.request.translate
        company = self.request.context.company
        form = CompanyForm(self.request.POST, company, request=self.request)
        countries = dict(select_countries())

        if self.request.method == "POST" and form.validate():
            from ..utils.website_autofill import shorten_url_to_hostname

            form.populate_obj(company)
            if form.shorten_website.data:
                company.website = shorten_url_to_hostname(form.website.data)
            loc = location(
                street=form.street.data,
                city=form.city.data,
                subdivision=getattr(
                    pycountry.subdivisions.get(code=form.subdivision.data), "name", ""
                ),
                country=countries.get(form.country.data),
                postalcode=form.postcode.data,
            )
            if loc is not None:
                company.latitude = loc["lat"]
                company.longitude = loc["lon"]

            company.updated_by = self.request.identity
            self.request.session.flash(_("success:Changes have been saved"))
            next_url = self.request.route_url(
                "company_view", company_id=company.id, slug=company.slug
            )
            log.info(
                _("The user %s changed the company details")
                % self.request.identity.name
            )
            return HTTPSeeOther(location=next_url)
        return {"heading": _("Edit company details"), "form": form}

    @view_config(route_name="company_delete", request_method="POST", permission="edit")
    def delete(self):
        _ = self.request.translate
        company = self.request.context.company
        contact_ids = (
            self.request.dbsession.execute(
                select(Contact.id).where(Contact.company_id == company.id)
            )
            .scalars()
            .all()
        )
        clear_selected_rows(
            self.request,
            companies_stars,
            companies_stars.c.company_id,
            [company.id],
        )
        clear_selected_rows(
            self.request,
            selected_contacts,
            selected_contacts.c.contact_id,
            contact_ids,
        )
        clear_selected_rows(
            self.request,
            selected_companies,
            selected_companies.c.company_id,
            [company.id],
        )
        self.request.dbsession.delete(company)
        self.request.session.flash(_("success:Removed from the database"))
        log.info(_("The user %s deleted the company") % self.request.identity.name)
        next_url = self.request.route_url("home")
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="company_del_row",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def del_row(self):
        _ = self.request.translate
        company = self.request.context.company
        contact_ids = (
            self.request.dbsession.execute(
                select(Contact.id).where(Contact.company_id == company.id)
            )
            .scalars()
            .all()
        )
        clear_selected_rows(
            self.request,
            selected_contacts,
            selected_contacts.c.contact_id,
            contact_ids,
        )
        clear_selected_rows(
            self.request,
            selected_companies,
            selected_companies.c.company_id,
            [company.id],
        )
        clear_selected_rows(
            self.request,
            companies_stars,
            companies_stars.c.company_id,
            [company.id],
        )
        self.request.dbsession.delete(company)
        log.info(_("The user %s deleted the company") % self.request.identity.name)
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": "companyEvent"}
        return ""

    @view_config(
        route_name="company_star",
        request_method="POST",
        renderer="string",
        permission="view",
    )
    def star(self):
        company = self.request.context.company
        companies_stars = self.request.identity.companies_stars

        if company in companies_stars:
            companies_stars.remove(company)
            self.request.response.headers = {"HX-Trigger": "starCompanyEvent"}
            return '<i class="bi bi-star"></i>'
        else:
            companies_stars.append(company)
            self.request.response.headers = {"HX-Trigger": "starCompanyEvent"}
            return '<i class="bi bi-star-fill"></i>'

    @view_config(
        route_name="company_check",
        request_method="POST",
        renderer="json",
        permission="view",
    )
    def check(self):
        company_id = self.request.context.company.id
        set_select_all_state(self.request, False)
        checked = toggle_selected_item(
            self.request,
            selected_companies,
            selected_companies.c.company_id,
            company_id,
        )
        return {"checked": checked}

    @view_config(
        route_name="company_select",
        renderer="company_datalist.mako",
        request_method="GET",
    )
    def select(self):
        name = self.request.params.get("name")
        companies = []
        if name:
            companies = self.request.dbsession.execute(
                select(Company).filter(
                    normalize_ci_expression(Company.name).like(
                        "%" + normalize_ci_value(name) + "%"
                    )
                )
            ).scalars()
        return {"companies": companies}

    @view_config(
        route_name="company_search",
        renderer="company_form.mako",
        permission="view",
    )
    def search(self):
        _ = self.request.translate
        form = CompanySearchForm(self.request.POST)
        tags = self._normalized_tags()
        q = {}
        for fieldname, value in form.data.items():
            if value:
                q[fieldname] = value

        if tags:
            q["tag"] = tags

        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "company_all",
                    _query=q,
                )
            )
        return {"heading": _("Find a company"), "form": form, "tags": tags}

    @view_config(
        route_name="unlink_tag_company",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def unlink_tag(self):
        _ = self.request.translate
        company_id = int(self.request.matchdict["company_id"])
        tag_id = int(self.request.matchdict["tag_id"])

        company = self.request.dbsession.execute(
            select(Company).filter_by(id=company_id)
        ).scalar_one_or_none()
        if not company:
            raise HTTPNotFound

        tag = self.request.dbsession.execute(
            select(Tag).filter_by(id=tag_id)
        ).scalar_one_or_none()
        if not tag:
            raise HTTPNotFound

        company.tags.remove(tag)
        log.info(
            _("The user %s unlinked the tag from the company")
            % self.request.identity.name
        )
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": "tagEvent"}
        return ""

    @view_config(
        route_name="company_add_project",
        renderer="company_activity_form.mako",
        permission="edit",
    )
    def add_project(self):
        _ = self.request.translate
        form = ProjectActivityForm(self.request.POST, request=self.request)
        company = self.request.context.company

        if self.request.method == "POST" and form.validate():
            project = self.request.dbsession.execute(
                select(Project).filter_by(name=form.name.data)
            ).scalar_one_or_none()

            if project:
                exist = self.request.dbsession.execute(
                    select(Activity).filter_by(
                        company_id=company.id, project_id=project.id
                    )
                ).scalar_one_or_none()

                if not exist:
                    with self.request.dbsession.no_autoflush:
                        a = Activity(stage=form.stage.data, role=form.role.data)
                        a.project = project
                        company.projects.append(a)
                        log.info(
                            _("The user %s added the project to the company")
                            % self.request.identity.name
                        )
                        self.request.session.flash(_("success:Added to the database"))
            next_url = self.request.route_url(
                "company_projects", company_id=company.id, slug=company.slug
            )
            return HTTPSeeOther(location=next_url)
        return {
            "heading": _("Add a project"),
            "form": form,
            "company": company,
            "company_pills": self.pills(company),
        }

    @view_config(
        route_name="company_activity_edit",
        renderer="activity_form.mako",
        permission="edit",
    )
    def company_activity_edit(self):
        _ = self.request.translate

        company_id = int(self.request.matchdict["company_id"])
        project_id = int(self.request.matchdict["project_id"])

        company = self.request.dbsession.execute(
            select(Company).filter_by(id=company_id)
        ).scalar_one_or_none()

        if not company:
            raise HTTPNotFound

        project = self.request.dbsession.execute(
            select(Project).filter_by(id=project_id)
        ).scalar_one_or_none()

        if not project:
            raise HTTPNotFound

        assoc = self.request.dbsession.execute(
            select(Activity).filter_by(company_id=company.id, project_id=project.id)
        ).scalar()

        form = ActivityForm(self.request.POST, assoc, request=self.request)

        if self.request.method == "POST" and form.validate():
            form.populate_obj(assoc)

            self.request.session.flash(_("success:Changes have been saved"))
            next_url = self.request.route_url(
                "project_companies", project_id=project.id, slug=project.slug
            )
            log.info(
                _("The user %s changed the activity details")
                % self.request.identity.name
            )
            return HTTPSeeOther(location=next_url)
        return {
            "heading": _("Edit activity details"),
            "form": form,
            "company": company,
            "project": project,
        }

    @view_config(
        route_name="activity_unlink",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def activity_unlink(self):
        _ = self.request.translate

        company_id = int(self.request.matchdict["company_id"])
        project_id = int(self.request.matchdict["project_id"])

        company = self.request.dbsession.execute(
            select(Company).filter_by(id=company_id)
        ).scalar_one_or_none()

        if not company:
            raise HTTPNotFound

        project = self.request.dbsession.execute(
            select(Project).filter_by(id=project_id)
        ).scalar_one_or_none()

        if not project:
            raise HTTPNotFound

        assoc = self.request.dbsession.execute(
            select(Activity).filter_by(company_id=company.id, project_id=project.id)
        ).scalar()

        self.request.dbsession.delete(assoc)
        log.info(
            _("The user %s unlinked the company from the project")
            % self.request.identity.name
        )
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": "assocEvent"}
        return ""
