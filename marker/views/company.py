import logging
from sqlalchemy import (
    select,
    func,
)
from sqlalchemy import and_

from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPSeeOther,
    HTTPNotFound,
)

from ..models import (
    Company,
    Comment,
    Person,
    Tag,
    Project,
    User,
    CompaniesProjects,
    recommended,
)
from ..forms import (
    CompanyForm,
    CompanySearchForm,
)
from ..paginator import get_paginator
from ..forms.select import (
    COUNTRIES,
    STATES,
    COLORS,
    COURTS,
    DROPDOWN_SORT_COMPANIES,
    DROPDOWN_ORDER,
    COMPANY_ROLES,
    STAGES,
)
from ..geo import location
from ..dropdown import Dropdown, Dd

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
        state = self.request.params.get("state", None)
        country = self.request.params.get("country", None)
        link = self.request.params.get("link", None)
        NIP = self.request.params.get("NIP", None)
        REGON = self.request.params.get("REGON", None)
        KRS = self.request.params.get("KRS", None)
        court = self.request.params.get("court", None)
        color = self.request.params.get("color", None)
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        colors = dict(COLORS)
        states = dict(STATES)
        dropdown_sort = dict(DROPDOWN_SORT_COMPANIES)
        dropdown_order = dict(DROPDOWN_ORDER)
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

        if state:
            stmt = stmt.filter(Company.state == state)

        if country:
            stmt = stmt.filter(Company.country == country)

        if court:
            stmt = stmt.filter(Company.court == court)

        if color:
            stmt = stmt.filter(Company.color == color)

        if sort == "recommended":
            if order == "asc":
                stmt = (
                    stmt.join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).asc(), Company.id)
                )
            elif order == "desc":
                stmt = (
                    stmt.join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).desc(), Company.id)
                )
        else:
            if order == "asc":
                stmt = stmt.order_by(getattr(Company, sort).asc(), Company.id)
            elif order == "desc":
                stmt = stmt.order_by(getattr(Company, sort).desc(), Company.id)

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        dd_sort = Dropdown(
            items=dropdown_sort, typ=Dd.SORT, _filter=filter, _sort=sort, _order=order
        )
        dd_order = Dropdown(
            items=dropdown_order, typ=Dd.ORDER, _filter=filter, _sort=sort, _order=order
        )

        search_query = {
            "name": name,
            "street": street,
            "postcode": postcode,
            "city": city,
            "state": state,
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
            _query={**search_query, "page": page + 1},
        )

        return {
            "search_query": search_query,
            "next_page": next_page,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "states": states,
            "colors": colors,
            "counter": counter,
        }

    @view_config(
        route_name="company_view",
        renderer="company_view.mako",
        permission="view",
    )
    def view(self):
        company = self.request.context.company
        states = dict(STATES)
        courts = dict(COURTS)
        countries = dict(COUNTRIES)

        return {
            "company": company,
            "states": states,
            "courts": courts,
            "countries": countries,
            "title": company.name,
        }

    @view_config(
        route_name="company_persons",
        renderer="company_persons.mako",
        permission="view",
    )
    def persons(self):
        company = self.request.context.company
        return {
            "company": company,
            "title": company.name,
        }

    @view_config(
        route_name="company_tags",
        renderer="company_tags.mako",
        permission="view",
    )
    def tags(self):
        company = self.request.context.company
        return {
            "company": company,
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
        state = self.request.params.get("state", None)
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
            "state": state,
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
        state = self.request.params.get("state", None)
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

        if state:
            stmt = stmt.filter(Company.state == state)

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
                "state": company.state,
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
        route_name="count_company_tags",
        renderer="json",
        permission="view",
    )
    def count_company_tags(self):
        company = self.request.context.company
        return company.count_tags

    @view_config(
        route_name="count_company_projects",
        renderer="json",
        permission="view",
    )
    def count_company_projects(self):
        company = self.request.context.company
        return company.count_projects

    @view_config(
        route_name="count_company_persons",
        renderer="json",
        permission="view",
    )
    def count_company_persons(self):
        company = self.request.context.company
        return company.count_persons

    @view_config(
        route_name="count_company_comments",
        renderer="json",
        permission="view",
    )
    def count_company_comments(self):
        company = self.request.context.company
        return company.count_comments

    @view_config(
        route_name="count_company_recommended",
        renderer="json",
        permission="view",
    )
    def count_company_recommended(self):
        company = self.request.context.company
        return company.count_recommended

    @view_config(
        route_name="count_similar_companies",
        renderer="json",
        permission="view",
    )
    def count_similar_companies(self):
        company = self.request.context.company
        return company.count_similar

    @view_config(
        route_name="company_recommended",
        renderer="company_recommended.mako",
        permission="view",
    )
    @view_config(
        route_name="company_recommended_more",
        renderer="user_more.mako",
        permission="view",
    )
    def recommended(self):
        company = self.request.context.company
        page = int(self.request.params.get("page", 1))
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
            "company_recommended_more",
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
        route_name="add_tag_to_company",
        renderer="tag_row_company.mako",
        request_method="POST",
        permission="edit",
    )
    def add_tag(self):
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
                log.info(f"Użytkownik {self.request.identity.name} dodał tag do firmy")
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "tagCompanyEvent"}
        return {"company": company, "tag": new_tag}

    @view_config(
        route_name="add_person_to_company",
        renderer="person_row.mako",
        request_method="POST",
        permission="edit",
    )
    def add_person(self):
        company = self.request.context.company
        person = None
        name = self.request.POST.get("name")
        position = self.request.POST.get("position")
        phone = self.request.POST.get("phone")
        email = self.request.POST.get("email")
        if name:
            person = Person(name, position, phone, email)
            person.created_by = self.request.identity
            if person not in company.people:
                company.people.append(person)
                log.info(
                    f"Użytkownik {self.request.identity.name} dodał osobę do firmy"
                )
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "personCompanyEvent"}
        return {"person": person}

    @view_config(
        route_name="company_comments",
        renderer="company_comments.mako",
        permission="view",
    )
    @view_config(
        route_name="company_comments_more",
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
            "company_comments_more",
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
        route_name="company_projects",
        renderer="company_projects.mako",
        permission="view",
    )
    def projects(self):
        company = self.request.context.company
        stages = dict(STAGES)
        company_roles = dict(COMPANY_ROLES)
        return {
            "company": company,
            "stages": stages,
            "company_roles": company_roles,
            "title": company.name,
        }

    @view_config(
        route_name="company_similar",
        renderer="company_similar.mako",
        permission="view",
    )
    @view_config(
        route_name="company_similar_more",
        renderer="company_more.mako",
        permission="view",
    )
    def similar(self):
        company = self.request.context.company
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", None)
        order = self.request.params.get("order", None)
        colors = dict(COLORS)
        states = dict(STATES)

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

        if filter:
            stmt = stmt.filter(Company.color == filter)

        if order == "asc":
            stmt = stmt.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Company, sort).desc())

        search_query = {}

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "company_similar_more",
            company_id=company.id,
            slug=company.slug,
            colors=colors,
            _query={
                **search_query,
                "filter": filter,
                "sort": sort,
                "order": order,
                "page": page + 1,
            },
        )

        dd_filter = Dropdown(
            items=colors, typ=Dd.FILTER, _filter=filter, _sort=sort, _order=order
        )

        return {
            "search_query": search_query,
            "company": company,
            "dd_filter": dd_filter,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "states": states,
            "title": company.name,
        }

    @view_config(
        route_name="company_add", renderer="company_form.mako", permission="edit"
    )
    def add(self):
        form = CompanyForm(self.request.POST, dbsession=self.request.dbsession)
        states = dict(STATES)
        countries = dict(COUNTRIES)

        if self.request.method == "POST" and form.validate():
            company = Company(
                name=form.name.data,
                street=form.street.data,
                postcode=form.postcode.data,
                city=form.city.data,
                state=form.state.data,
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
                state=states.get(form.state.data),
                country=countries.get(form.country.data),
                postalcode=form.postcode.data,
            )
            if loc is not None:
                company.latitude = loc["lat"]
                company.longitude = loc["lon"]

            company.created_by = self.request.identity
            self.request.dbsession.add(company)
            self.request.session.flash("success:Dodano do bazy danych")
            log.info(f"Użytkownik {self.request.identity.name} dodał firmę")
            next_url = self.request.route_url("company_all")
            return HTTPSeeOther(location=next_url)
        return {"heading": "Dodaj firmę", "form": form}

    @view_config(
        route_name="company_edit", renderer="company_form.mako", permission="edit"
    )
    def edit(self):
        company = self.request.context.company
        form = CompanyForm(self.request.POST, company, dbsession=self.request.dbsession)
        states = dict(STATES)
        countries = dict(COUNTRIES)

        if self.request.method == "POST" and form.validate():
            form.populate_obj(company)
            loc = location(
                street=form.street.data,
                city=form.city.data,
                state=states.get(form.state.data),
                country=countries.get(form.country.data),
                postalcode=form.postcode.data,
            )
            if loc is not None:
                company.latitude = loc["lat"]
                company.longitude = loc["lon"]

            company.updated_by = self.request.identity
            self.request.session.flash("success:Zmiany zostały zapisane")
            next_url = self.request.route_url(
                "company_view", company_id=company.id, slug=company.slug
            )
            log.info(f"Użytkownik {self.request.identity.name} zmienił dane firmy")
            return HTTPSeeOther(location=next_url)
        return {"heading": "Edytuj dane firmy", "form": form}

    @view_config(route_name="company_delete", request_method="POST", permission="edit")
    def delete(self):
        company = self.request.context.company
        self.request.dbsession.delete(company)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(f"Użytkownik {self.request.identity.name} usunął firmę")
        next_url = self.request.route_url("home")
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

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
            self.request.response.headers = {"HX-Trigger": "recommendedCompanyEvent"}
            return '<i class="bi bi-hand-thumbs-up"></i>'
        else:
            recommended.append(company)
            self.request.response.headers = {"HX-Trigger": "recommendedCompanyEvent"}
            return '<i class="bi bi-hand-thumbs-up-fill"></i>'

    @view_config(
        route_name="company_check",
        request_method="POST",
        renderer="json",
        permission="view",
    )
    def mark(self):
        company = self.request.context.company
        checked = self.request.identity.checked

        if company in checked:
            checked.remove(company)
            return {"checked": False}
        else:
            checked.append(company)
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
    def company_search(self):
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
                        "state": form.state.data,
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
        return {"heading": "Znajdź firmę", "form": form}

    @view_config(
        route_name="unlink_tag_from_company",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def unlink_tag(self):
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
        log.info(f"Użytkownik {self.request.identity.name} odpiął tag od firmy")
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": "tagCompanyEvent"}
        return ""

    @view_config(
        route_name="add_project_to_company",
        renderer="project_list_companies.mako",
        request_method="POST",
        permission="edit",
    )
    def add_project(self):
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

            exist = self.request.dbsession.execute(
                select(CompaniesProjects).filter_by(project_id=project.id)
            ).scalar_one_or_none()

            if not exist:
                a = CompaniesProjects(stage=stage, role=role)
                a.project = project
                company.projects.append(a)
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "projectCompanyEvent"}
        return {"company": company, "stages": stages, "company_roles": company_roles}

    @view_config(
        route_name="unlink_project",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def unlink_project(self):
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
        log.info(f"Użytkownik {self.request.identity.name} odpiął firmę od projektu")
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": "projectCompanyEvent"}
        return ""
