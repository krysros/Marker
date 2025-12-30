import logging

import pycountry
from pyramid.httpexceptions import HTTPNotFound, HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import and_, func, select

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
    SORT_CRITERIA_COMPANIES,
    STAGES,
    USER_ROLES,
    select_countries,
    select_subdivisions,
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
)
from ..utils.geo import location
from ..utils.paginator import get_paginator
from . import Filter

log = logging.getLogger(__name__)


class CompanyView:
    def __init__(self, request):
        self.request = request

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
    def all(self):
        page = int(self.request.params.get("page", 1))
        name = self.request.params.get("name", None)
        street = self.request.params.get("street", None)
        postcode = self.request.params.get("postcode", None)
        city = self.request.params.get("city", None)
        subdivision = self.request.params.getall("subdivision")
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

        if name:
            stmt = stmt.filter(Company.name.ilike("%" + name + "%"))
            q["name"] = name

        if street:
            stmt = stmt.filter(Company.street.ilike("%" + street + "%"))
            q["street"] = street

        if postcode:
            stmt = stmt.filter(Company.postcode.ilike("%" + postcode + "%"))
            q["postcode"] = postcode

        if city:
            stmt = stmt.filter(Company.city.ilike("%" + city + "%"))
            q["city"] = city

        if website:
            stmt = stmt.filter(Company.website.ilike("%" + website + "%"))
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
                    .group_by(Company)
                    .order_by(
                        func.count(companies_stars.c.company_id).asc(), Company.id
                    )
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(companies_stars)
                    .group_by(Company)
                    .order_by(
                        func.count(companies_stars.c.company_id).desc(), Company.id
                    )
                )
        elif _sort == "comments":
            if _order == "asc":
                stmt = (
                    stmt.join(Company.comments)
                    .group_by(Company)
                    .order_by(func.count(Company.comments).asc())
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(Company.comments)
                    .group_by(Company)
                    .order_by(func.count(Company.comments).desc())
                )
        else:
            if _order == "asc":
                stmt = stmt.order_by(getattr(Company, _sort).asc(), Company.id)
            elif _order == "desc":
                stmt = stmt.order_by(getattr(Company, _sort).desc(), Company.id)

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        obj = Filter(**q)
        form = CompanyFilterForm(self.request.GET, obj, request=self.request)

        next_page = self.request.route_url(
            "company_more",
            _query={
                **q,
                "page": page + 1,
            },
        )

        return {
            "q": q,
            "next_page": next_page,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "counter": counter,
            "colors": colors,
            "form": form,
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
        courts = dict(COURTS)
        countries = dict(select_countries())
        stages = dict(STAGES)
        company_roles = dict(COMPANY_ROLES)

        return {
            "company": company,
            "courts": courts,
            "countries": countries,
            "stages": stages,
            "company_roles": company_roles,
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
        subdivision = self.request.params.getall("subdivision")
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
            stmt = stmt.filter(Company.name.ilike("%" + name + "%"))
            q["name"] = name

        if street:
            stmt = stmt.filter(Company.street.ilike("%" + street + "%"))
            q["street"] = street

        if postcode:
            stmt = stmt.filter(Company.postcode.ilike("%" + postcode + "%"))
            q["postcode"] = postcode

        if city:
            stmt = stmt.filter(Company.city.ilike("%" + city + "%"))
            q["city"] = city

        if website:
            stmt = stmt.filter(Company.website.ilike("%" + website + "%"))
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
                    .group_by(Company)
                    .order_by(
                        func.count(companies_stars.c.company_id).asc(), Company.id
                    )
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(companies_stars)
                    .group_by(Company)
                    .order_by(
                        func.count(companies_stars.c.company_id).desc(), Company.id
                    )
                )
        else:
            if _order == "asc":
                stmt = stmt.order_by(getattr(Company, _sort).asc(), Company.id)
            elif _order == "desc":
                stmt = stmt.order_by(getattr(Company, _sort).desc(), Company.id)

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
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
            stmt = stmt.filter(Company.name.ilike("%" + name + "%"))

        if street:
            stmt = stmt.filter(Company.street.ilike("%" + street + "%"))

        if postcode:
            stmt = stmt.filter(Company.postcode.ilike("%" + postcode + "%"))

        if city:
            stmt = stmt.filter(Company.city.ilike("%" + city + "%"))

        if website:
            stmt = stmt.filter(Company.website.ilike("%" + website + "%"))

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
        company = self.request.context.company
        page = int(self.request.params.get("page", 1))
        user_roles = dict(USER_ROLES)
        stmt = (
            select(User)
            .join(companies_stars)
            .filter(company.id == companies_stars.c.company_id)
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "company_more_stars",
            company_id=company.id,
            slug=company.slug,
            _query={"page": page + 1},
        )
        return {
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
            tag = self.request.dbsession.execute(
                select(Tag).filter_by(name=form.name.data)
            ).scalar_one_or_none()
            if not tag:
                tag = Tag(form.name.data)
                tag.created_by = self.request.identity
            if tag not in company.tags:
                company.tags.append(tag)
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
            )
            contact.created_by = self.request.identity
            if contact not in company.contacts:
                company.contacts.append(contact)
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
        stmt = (
            select(Comment)
            .filter(Comment.company_id == company.id)
            .order_by(Comment.created_at.desc())
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "company_more_comments",
            company_id=company.id,
            slug=company.slug,
            _query={"page": page + 1},
        )

        return {
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
        company = self.request.context.company
        page = int(self.request.params.get("page", 1))
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        colors = dict(COLORS)
        q = {}

        stmt = (
            select(Company)
            .join(Tag, Company.tags)
            .filter(
                and_(
                    Tag.companies.any(Company.id == company.id),
                    Company.id != company.id,
                )
            )
            .group_by(Company)
            .order_by(func.count(Tag.companies.any(Company.id == company.id)).desc())
        )

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

        if _order == "asc":
            stmt = stmt.order_by(getattr(Company, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Company, _sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

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
        subdivisions = dict(select_subdivisions(form.country.data))
        if self.request.method == "POST" and form.validate():
            company = Company(
                name=form.name.data,
                street=form.street.data,
                postcode=form.postcode.data,
                city=form.city.data,
                subdivision=form.subdivision.data,
                country=form.country.data,
                website=form.website.data,
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
            self.request.session.flash(_("success:Added to the database"))
            self.request.session.flash(_("info:Add tags and contacts"))
            log.info(_("The user %s has added a company") % self.request.identity.name)
            next_url = self.request.route_url(
                "company_view", company_id=company.id, slug=company.slug
            )
            return HTTPSeeOther(location=next_url)
        return {"heading": _("Add a company"), "form": form, "subdivisions": subdivisions}

    @view_config(
        route_name="company_edit", renderer="company_form.mako", permission="edit"
    )
    def edit(self):
        _ = self.request.translate
        company = self.request.context.company
        form = CompanyForm(self.request.POST, company, request=self.request)
        countries = dict(select_countries())
        subdivisions = dict(select_subdivisions(form.country.data))
        if self.request.method == "POST" and form.validate():
            form.populate_obj(company)
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
        return {"heading": _("Edit company details"), "form": form, "subdivisions": subdivisions}

    @view_config(route_name="company_delete", request_method="POST", permission="edit")
    def delete(self):
        _ = self.request.translate
        company = self.request.context.company
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
        company = self.request.context.company
        selected_companies = self.request.identity.selected_companies

        if company in selected_companies:
            selected_companies.remove(company)
            return {"checked": False}
        else:
            selected_companies.append(company)
            return {"checked": True}

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
                select(Company).filter(Company.name.ilike("%" + name + "%"))
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
        q = {}
        for fieldname, value in form.data.items():
            if value:
                q[fieldname] = value

        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "company_all",
                    _query=q,
                )
            )
        return {"heading": _("Find a company"), "form": form}

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
