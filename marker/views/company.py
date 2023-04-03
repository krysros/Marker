import logging

import pycountry
from pyramid.httpexceptions import HTTPNotFound, HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import and_, func, select

from ..dropdown import Dd, Dropdown
from ..forms import CompanyForm, CompanySearchForm
from ..forms.select import (
    COLORS,
    COMPANY_ROLES,
    COURTS,
    ORDER_CRITERIA,
    SORT_CRITERIA_COMPANIES,
    STAGES,
    USER_ROLES,
    select_countries,
)
from ..geo import location
from ..models import (
    Comment,
    CompaniesProjects,
    Company,
    Contact,
    Project,
    Tag,
    User,
    recommended,
)
from ..paginator import get_paginator

log = logging.getLogger(__name__)


class CompanyView:
    def __init__(self, request):
        self.request = request

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
        subdivision = self.request.params.get("subdivision", None)
        country = self.request.params.get("country", None)
        link = self.request.params.get("link", None)
        NIP = self.request.params.get("NIP", None)
        REGON = self.request.params.get("REGON", None)
        KRS = self.request.params.get("KRS", None)
        court = self.request.params.get("court", None)
        color = self.request.params.get("color", None)
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        colors = dict(COLORS)
        sort_criteria = dict(SORT_CRITERIA_COMPANIES)
        order_criteria = dict(ORDER_CRITERIA)
        stmt = select(Company)

        if name:
            stmt = stmt.filter(Company.name.ilike("%" + name + "%"))

        if street:
            stmt = stmt.filter(Company.street.ilike("%" + street + "%"))

        if postcode:
            stmt = stmt.filter(Company.postcode.ilike("%" + postcode + "%"))

        if city:
            stmt = stmt.filter(Company.city.ilike("%" + city + "%"))

        if link:
            stmt = stmt.filter(Company.link.ilike("%" + link + "%"))

        if NIP:
            stmt = stmt.filter(Company.NIP.ilike("%" + NIP + "%"))

        if REGON:
            stmt = stmt.filter(Company.REGON.ilike("%" + REGON + "%"))

        if KRS:
            stmt = stmt.filter(Company.KRS.ilike("%" + KRS + "%"))

        if subdivision:
            stmt = stmt.filter(Company.subdivision == subdivision)

        if country:
            stmt = stmt.filter(Company.country == country)

        if court:
            stmt = stmt.filter(Company.court == court)

        if color:
            stmt = stmt.filter(Company.color == color)

        if _sort == "recommended":
            if _order == "asc":
                stmt = (
                    stmt.join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).asc(), Company.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).desc(), Company.id)
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

        dd_sort = Dropdown(self.request, sort_criteria, Dd.SORT, _filter, _sort, _order)
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, _filter, _sort, _order
        )

        search_query = {
            "name": name,
            "street": street,
            "postcode": postcode,
            "city": city,
            "subdivision": subdivision,
            "country": country,
            "link": link,
            "NIP": NIP,
            "REGON": REGON,
            "KRS": KRS,
            "court": court,
            "color": color,
        }

        next_page = self.request.route_url(
            "company_more",
            _query={
                **search_query,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
                "page": page + 1,
            },
        )

        # Recreate the search form to display the search criteria
        form = CompanySearchForm(**search_query)

        return {
            "search_query": search_query,
            "form": form,
            "next_page": next_page,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "colors": colors,
            "counter": counter,
        }

    @view_config(
        route_name="company_count",
        renderer="json",
        permission="view",
    )
    def count(self):
        return self.request.dbsession.execute(
            select(func.count()).select_from(select(Company))
        ).scalar()

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
        subdivision = self.request.params.get("subdivision", None)
        country = self.request.params.get("country", None)
        link = self.request.params.get("link", None)
        NIP = self.request.params.get("NIP", None)
        REGON = self.request.params.get("REGON", None)
        KRS = self.request.params.get("KRS", None)
        court = self.request.params.get("court", None)
        color = self.request.params.get("color", None)

        search_query = {
            "name": name,
            "street": street,
            "postcode": postcode,
            "city": city,
            "subdivision": subdivision,
            "country": country,
            "link": link,
            "NIP": NIP,
            "REGON": REGON,
            "KRS": KRS,
            "court": court,
            "color": color,
        }

        url = self.request.route_url("company_json", _query=search_query)
        return {"url": url, "search_query": search_query}

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
        link = self.request.params.get("link", None)
        NIP = self.request.params.get("NIP", None)
        REGON = self.request.params.get("REGON", None)
        KRS = self.request.params.get("KRS", None)
        court = self.request.params.get("court", None)
        color = self.request.params.get("color", None)

        stmt = select(Company)

        if name:
            stmt = stmt.filter(Company.name.ilike("%" + name + "%"))

        if street:
            stmt = stmt.filter(Company.street.ilike("%" + street + "%"))

        if postcode:
            stmt = stmt.filter(Company.postcode.ilike("%" + postcode + "%"))

        if city:
            stmt = stmt.filter(Company.city.ilike("%" + city + "%"))

        if link:
            stmt = stmt.filter(Company.link.ilike("%" + link + "%"))

        if NIP:
            stmt = stmt.filter(Company.NIP.ilike("%" + NIP + "%"))

        if REGON:
            stmt = stmt.filter(Company.REGON.ilike("%" + REGON + "%"))

        if KRS:
            stmt = stmt.filter(Company.KRS.ilike("%" + KRS + "%"))

        if subdivision:
            stmt = stmt.filter(Company.subdivision == subdivision)

        if country:
            stmt = stmt.filter(Company.country == country)

        if court:
            stmt = stmt.filter(Company.court == court)

        if color:
            stmt = stmt.filter(Company.color == color)

        companies = self.request.dbsession.execute(stmt).scalars()

        res = [
            {
                "id": company.id,
                "name": company.name,
                "street": company.street,
                "postcode": company.postcode,
                "city": company.city,
                "subdivision": company.subdivision,
                "country": company.country,
                "latitude": company.latitude,
                "longitude": company.longitude,
                "link": company.link,
                "NIP": company.NIP,
                "REGON": company.REGON,
                "KRS": company.KRS,
                "court": company.court,
                "color": company.color,
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
        route_name="company_count_recommended",
        renderer="json",
        permission="view",
    )
    def count_recommended(self):
        company = self.request.context.company
        return company.count_recommended

    @view_config(
        route_name="company_count_similar",
        renderer="json",
        permission="view",
    )
    def count_similar(self):
        company = self.request.context.company
        return company.count_similar

    @view_config(
        route_name="company_recommended",
        renderer="company_recommended.mako",
        permission="view",
    )
    @view_config(
        route_name="company_more_recommended",
        renderer="user_more.mako",
        permission="view",
    )
    def recommended(self):
        company = self.request.context.company
        page = int(self.request.params.get("page", 1))
        user_roles = dict(USER_ROLES)
        stmt = (
            select(User)
            .join(recommended)
            .filter(company.id == recommended.c.company_id)
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "company_more_recommended",
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
        }

    @view_config(
        route_name="company_add_tag",
        renderer="tag_row_company.mako",
        request_method="POST",
        permission="edit",
    )
    def add_tag(self):
        _ = self.request.translate
        company = self.request.context.company
        name = self.request.POST.get("name")
        new_tag = None
        if name:
            tag = self.request.dbsession.execute(
                select(Tag).filter_by(name=name)
            ).scalar_one_or_none()
            if not tag:
                tag = Tag(name)
                tag.created_by = self.request.identity
            if tag not in company.tags:
                company.tags.append(tag)
                new_tag = tag
                log.info(
                    _("The user %s has added a tag to the company")
                    % self.request.identity.name
                )
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "tagEvent"}
        return {"company": company, "tag": new_tag}

    @view_config(
        route_name="company_add_contact",
        renderer="contact_row.mako",
        request_method="POST",
        permission="edit",
    )
    def add_contact(self):
        _ = self.request.translate
        company = self.request.context.company
        contact = None
        name = self.request.POST.get("name")
        role = self.request.POST.get("role")
        phone = self.request.POST.get("phone")
        email = self.request.POST.get("email")
        if name:
            contact = Contact(name, role, phone, email)
            contact.created_by = self.request.identity
            if contact not in company.contacts:
                company.contacts.append(contact)
                log.info(
                    _("The user %s has added a contact to the company")
                    % self.request.identity.name
                )
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "contactEvent"}
        return {"contact": contact}

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
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", None)
        _order = self.request.params.get("order", None)
        colors = dict(COLORS)

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

        if _filter:
            stmt = stmt.filter(Company.color == _filter)

        if _order == "asc":
            stmt = stmt.order_by(getattr(Company, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Company, _sort).desc())

        search_query = {}

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
                **search_query,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
                "page": page + 1,
            },
        )

        dd_filter = Dropdown(self.request, colors, Dd.FILTER, _filter, _sort, _order)

        return {
            "search_query": search_query,
            "company": company,
            "dd_filter": dd_filter,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "title": company.name,
        }

    @view_config(
        route_name="company_add", renderer="company_form.mako", permission="edit"
    )
    def add(self):
        _ = self.request.translate
        form = CompanyForm(self.request.POST, request=self.request)
        countries = dict(select_countries())
        if self.request.method == "POST" and form.validate():
            company = Company(
                name=form.name.data,
                street=form.street.data,
                postcode=form.postcode.data,
                city=form.city.data,
                subdivision=form.subdivision.data,
                country=form.country.data,
                link=form.link.data,
                NIP=form.NIP.data,
                REGON=form.REGON.data,
                KRS=form.KRS.data,
                court=form.court.data,
                color=form.color.data,
            )
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
        return {"heading": _("Add a company"), "form": form}

    @view_config(
        route_name="company_edit", renderer="company_form.mako", permission="edit"
    )
    def edit(self):
        _ = self.request.translate
        company = self.request.context.company
        form = CompanyForm(self.request.POST, company, request=self.request)
        countries = dict(select_countries())

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
        return {"heading": _("Edit company details"), "form": form}

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
        route_name="company_recommend",
        request_method="POST",
        renderer="string",
        permission="view",
    )
    def recommend(self):
        company = self.request.context.company
        recommended = self.request.identity.recommended

        if company in recommended:
            recommended.remove(company)
            self.request.response.headers = {"HX-Trigger": "recommendEvent"}
            return '<i class="bi bi-hand-thumbs-up"></i>'
        else:
            recommended.append(company)
            self.request.response.headers = {"HX-Trigger": "recommendEvent"}
            return '<i class="bi bi-hand-thumbs-up-fill"></i>'

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
        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "company_all",
                    _query={
                        "name": form.name.data,
                        "street": form.street.data,
                        "postcode": form.postcode.data,
                        "city": form.city.data,
                        "subdivision": form.subdivision.data,
                        "country": form.country.data,
                        "link": form.link.data,
                        "NIP": form.NIP.data,
                        "REGON": form.REGON.data,
                        "KRS": form.KRS.data,
                        "court": form.court.data,
                        "color": form.color.data,
                    },
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
        renderer="project_assoc.mako",
        request_method="POST",
        permission="edit",
    )
    def add_project(self):
        _ = self.request.translate
        company = self.request.context.company
        name = self.request.POST.get("name")
        stage = self.request.POST.get("stage")
        role = self.request.POST.get("role")
        stages = dict(STAGES)
        company_roles = dict(COMPANY_ROLES)
        if name:
            project = self.request.dbsession.execute(
                select(Project).filter_by(name=name)
            ).scalar_one_or_none()

            if project:
                exist = self.request.dbsession.execute(
                    select(CompaniesProjects).filter_by(
                        company_id=company.id, project_id=project.id
                    )
                ).scalar_one_or_none()

                if not exist:
                    a = CompaniesProjects(stage=stage, role=role)
                    a.project = project
                    company.projects.append(a)
                    log.info(
                        _("The user %s added the project to the company")
                        % self.request.identity.name
                    )
                # If you want to use the id of a newly created object
                # in the middle of a transaction, you must call dbsession.flush()
                self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "projectCompanyEvent"}
        return {"company": company, "stages": stages, "company_roles": company_roles}

    @view_config(
        route_name="unlink_company_project",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def unlink_company_project(self):
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
            select(CompaniesProjects).filter_by(
                company_id=company.id, project_id=project.id
            )
        ).scalar()

        self.request.dbsession.delete(assoc)
        log.info(
            _("The user %s unlinked the company from the project")
            % self.request.identity.name
        )
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": "projectCompanyEvent"}
        return ""
