import logging
from sqlalchemy import (
    select,
    func,
)
from sqlalchemy import and_

from pyramid.csrf import new_csrf_token
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther, HTTPNotFound

from ..models import (
    Company,
    Comment,
    Person,
    Tag,
    Project,
    User,
    recomended,
    companies_comments,
    companies_projects,
)
from ..forms import CompanyForm
from ..paginator import get_paginator
from ..forms.select import (
    STATES,
    COLORS,
    COURTS,
    DROPDOWN_EXT_SORT,
    DROPDOWN_ORDER,
)
from ..export import export_vcard


log = logging.getLogger(__name__)


class CompanyView(object):
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
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        colors = dict(COLORS)
        states = dict(STATES)
        dropdown_sort = dict(DROPDOWN_EXT_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        stmt = select(Company)

        if filter in list(colors):
            stmt = stmt.filter(Company.color == filter)

        if order == "asc":
            stmt = stmt.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Company, sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "company_more",
            _query={
                "filter": filter,
                "sort": sort,
                "order": order,
                "page": page + 1,
            },
        )

        return dict(
            next_page=next_page,
            filter=filter,
            sort=sort,
            order=order,
            paginator=paginator,
            states=states,
            colors=colors,
            dropdown_sort=dropdown_sort,
            dropdown_order=dropdown_order,
        )

    @view_config(
        route_name="company_view",
        renderer="company_view.mako",
        permission="view",
    )
    def view(self):
        company = self.request.context.company
        states = dict(STATES)
        courts = dict(COURTS)

        # Counters
        c_comments = self.request.dbsession.scalar(
            select(func.count())
            .select_from(Comment)
            .join(companies_comments)
            .filter(company.id == companies_comments.c.company_id)
        )
        c_recomended = self.request.dbsession.scalar(
            select(func.count())
            .select_from(User)
            .join(recomended)
            .filter(company.id == recomended.c.company_id)
        )
        c_projects = self.request.dbsession.scalar(
            select(func.count())
            .select_from(Project)
            .join(companies_projects)
            .filter(company.id == companies_projects.c.company_id)
        )
        c_similar = self.request.dbsession.scalar(
            select(func.count())
            .select_from(Company)
            .join(Tag, Company.tags)
            .filter(
                and_(
                    Tag.companies.any(Company.id == company.id),
                    Company.id != company.id,
                )
            )
        )

        return dict(
            c_comments=c_comments,
            c_recomended=c_recomended,
            c_projects=c_projects,
            c_similar=c_similar,
            company=company,
            states=states,
            courts=courts,
            title=company.name,
            tags=[],  # require to render tag_datalist.mako included in current template
        )

    @view_config(
        route_name="company_recomended",
        renderer="company_recomended.mako",
        permission="view",
    )
    @view_config(
        route_name="company_recomended_more",
        renderer="user_more.mako",
        permission="view",
    )
    def recomended(self):
        company = self.request.context.company
        page = int(self.request.params.get("page", 1))
        stmt = (
            select(User).join(recomended).filter(company.id == recomended.c.company_id)
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "company_recomended_more",
            company_id=company.id,
            slug=company.slug,
            _query={"page": page + 1},
        )
        return {
            "paginator": paginator,
            "next_page": next_page,
            "company": company,
        }

    @view_config(
        route_name="company_tags",
        renderer="company_tags.mako",
        request_method="POST",
        permission="edit",
    )
    def add_tag(self):
        new_csrf_token(self.request)
        company = self.request.context.company
        name = self.request.POST.get("name")
        if name:
            tag = self.request.dbsession.execute(
                select(Tag).filter_by(name=name)
            ).scalar_one_or_none()
            if not tag:
                tag = Tag(name)
            if tag not in company.tags:
                company.tags.append(tag)
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        return {"company": company}

    @view_config(
        route_name="company_people",
        renderer="company_people.mako",
        request_method="POST",
        permission="edit",
    )
    def add_person(self):
        new_csrf_token(self.request)
        company = self.request.context.company
        name = self.request.POST.get("name")
        position = self.request.POST.get("position")
        phone = self.request.POST.get("phone")
        email = self.request.POST.get("email")
        if name:
            person = Person(name=name, position=position, phone=phone, email=email)
            if person not in company.people:
                company.people.append(person)
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        return {"company": company}

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
            .join(companies_comments)
            .filter(company.id == companies_comments.c.company_id)
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
        }

    @view_config(
        route_name="company_projects",
        renderer="company_projects.mako",
        permission="view",
    )
    @view_config(
        route_name="company_projects_more",
        renderer="project_more.mako",
        permission="view",
    )
    def projects(self):
        company = self.request.context.company
        page = int(self.request.params.get("page", 1))
        states = dict(STATES)
        stmt = (
            select(Project)
            .join(companies_projects)
            .filter(company.id == companies_projects.c.company_id)
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "company_projects_more",
            company_id=company.id,
            slug=company.slug,
            _query={"page": page + 1},
        )
        return {
            "paginator": paginator,
            "next_page": next_page,
            "company": company,
            "states": states,
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
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        states = dict(STATES)
        dropdown_sort = dict(DROPDOWN_EXT_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)

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

        if filter in list(states):
            stmt = stmt.filter(Company.state == filter)

        if order == "asc":
            stmt = stmt.order_by(getattr(Company, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Company, sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "company_similar_more",
            company_id=company.id,
            slug=company.slug,
            _query={
                "filter": filter,
                "sort": sort,
                "order": order,
                "states": states,
                "page": page + 1,
            },
        )

        return dict(
            company=company,
            filter=filter,
            sort=sort,
            order=order,
            paginator=paginator,
            next_page=next_page,
            states=states,
            dropdown_sort=dropdown_sort,
            dropdown_order=dropdown_order,
        )

    @view_config(
        route_name="company_add", renderer="company_form.mako", permission="edit"
    )
    def add(self):
        form = CompanyForm(self.request.POST)

        if self.request.method == "POST" and form.validate():
            company = Company(
                name=form.name.data,
                street=form.street.data,
                postcode=form.postcode.data,
                city=form.city.data,
                state=form.state.data,
                WWW=form.WWW.data,
                NIP=form.NIP.data,
                REGON=form.REGON.data,
                KRS=form.KRS.data,
                court=form.court.data,
                color=form.color.data,
            )
            company.created_by = self.request.identity
            self.request.dbsession.add(company)
            self.request.session.flash("success:Dodano do bazy danych")
            log.info(
                f"Użytkownik {self.request.identity.name} dodał firmę {company.name}"
            )
            next_url = self.request.route_url("company_all")
            return HTTPSeeOther(location=next_url)

        return dict(
            heading="Dodaj firmę",
            form=form,
        )

    @view_config(
        route_name="company_edit", renderer="company_form.mako", permission="edit"
    )
    def edit(self):
        company = self.request.context.company
        form = CompanyForm(self.request.POST, company)
        if self.request.method == "POST" and form.validate():
            form.populate_obj(company)
            company.updated_by = self.request.identity
            self.request.session.flash("success:Zmiany zostały zapisane")
            next_url = self.request.route_url(
                "company_view", company_id=company.id, slug=company.slug
            )
            log.info(
                f"Użytkownik {self.request.identity.name} zmienił dane firmy {company.name}"
            )
            return HTTPSeeOther(location=next_url)

        return dict(
            heading="Edytuj dane firmy",
            form=form,
        )

    @view_config(route_name="company_delete", request_method="POST", permission="edit")
    def delete(self):
        company = self.request.context.company
        company_name = company.name
        self.request.dbsession.delete(company)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(f"Użytkownik {self.request.identity.name} usunął firmę {company_name}")
        next_url = self.request.route_url("home")
        return HTTPSeeOther(location=next_url)

    @view_config(
        route_name="company_recommend",
        request_method="POST",
        renderer="string",
        permission="view",
    )
    def recommend(self):
        company = self.request.context.company
        recomended = self.request.identity.recomended

        if company in recomended:
            recomended.remove(company)
            return '<i class="bi bi-hand-thumbs-up"></i>'
        else:
            recomended.append(company)
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
        company = self.request.params.get("company")
        companies = []
        if company:
            companies = self.request.dbsession.execute(
                select(Company).filter(Company.name.ilike("%" + company + "%"))
            ).scalars()
        return {"companies": companies}

    @view_config(
        route_name="company_search",
        renderer="company_search.mako",
        permission="view",
    )
    def company_search(self):
        states = dict(STATES)
        return {"states": states}

    @view_config(
        route_name="company_results",
        renderer="company_results.mako",
        permission="view",
    )
    @view_config(
        route_name="company_results_more",
        renderer="company_more.mako",
        permission="view",
    )
    def company_results(self):
        name = self.request.params.get("name")
        street = self.request.params.get("street")
        city = self.request.params.get("city")
        state = self.request.params.get("state")
        WWW = self.request.params.get("WWW")
        NIP = self.request.params.get("NIP")
        REGON = self.request.params.get("REGON")
        KRS = self.request.params.get("KRS")
        page = int(self.request.params.get("page", 1))
        states = dict(STATES)
        stmt = (
            select(Company)
            .filter(Company.name.ilike("%" + name + "%"))
            .filter(Company.street.ilike("%" + street + "%"))
            .filter(Company.city.ilike("%" + city + "%"))
            .filter(Company.state.ilike("%" + state + "%"))
            .filter(Company.WWW.ilike("%" + WWW + "%"))
            .filter(Company.NIP.ilike("%" + NIP + "%"))
            .filter(Company.REGON.ilike("%" + REGON + "%"))
            .filter(Company.KRS.ilike("%" + KRS + "%"))
            .order_by(Company.name)
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "company_results_more",
            _query={
                "name": name,
                "street": street,
                "city": city,
                "state": state,
                "WWW": WWW,
                "NIP": NIP,
                "REGON": REGON,
                "KRS": KRS,
                "page": page + 1,
            },
        )

        return dict(
            paginator=paginator,
            next_page=next_page,
            states=states,
        )

    @view_config(
        route_name="person_search",
        renderer="person_search.mako",
        permission="view",
    )
    def person_search(self):
        return {}

    @view_config(
        route_name="person_results",
        renderer="person_results.mako",
        permission="view",
    )
    @view_config(
        route_name="person_results_more",
        renderer="person_more.mako",
        permission="view",
    )
    def person_results(self):
        name = self.request.params.get("name")
        position = self.request.params.get("position")
        phone = self.request.params.get("phone")
        email = self.request.params.get("email")
        page = int(self.request.params.get("page", 1))
        stmt = (
            select(Person)
            .filter(Person.name.ilike("%" + name + "%"))
            .filter(Person.position.ilike("%" + position + "%"))
            .filter(Person.phone.ilike("%" + phone + "%"))
            .filter(Person.email.ilike("%" + email + "%"))
            .order_by(Person.name)
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "person_results_more",
            _query={
                "name": name,
                "position": position,
                "phone": phone,
                "email": email,
                "page": page + 1,
            },
        )
        return {"paginator": paginator, "next_page": next_page}

    @view_config(route_name="person_vcard", request_method="POST", permission="view")
    def vcard(self):
        person = self.request.context.person
        response = export_vcard(person)
        return response

    @view_config(
        route_name="delete_tag_from_company",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def delete_tag(self):
        new_csrf_token(self.request)
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

        company_name = company.name
        tag_name = tag.name

        company.tags.remove(tag)
        log.info(
            f"Użytkownik {self.request.identity.name} usunął tag {tag_name} z firmy {company_name}"
        )
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        return ""

    @view_config(
        route_name="person_delete",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def delete_person(self):
        new_csrf_token(self.request)
        person = self.request.context.person
        person_name = person.name
        self.request.dbsession.delete(person)
        log.info(f"Użytkownik {self.request.identity.name} usunął osobę {person_name}")
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        return ""
