import logging
from sqlalchemy import (
    select,
    func,
)
from sqlalchemy import and_

from pyramid.csrf import new_csrf_token
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
    recomended,
    companies_comments,
    companies_projects,
)
from ..forms import (
    CompanyForm,
    CompanySearchForm,
)
from ..paginator import get_paginator
from ..forms.select import (
    STATES,
    COLORS,
    COURTS,
    DROPDOWN_EXT_SORT,
    DROPDOWN_ORDER,
)


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
                tag = Tag(name[:50])
                tag.created_by = self.request.identity
            if tag not in company.tags:
                company.tags.append(tag)
                log.info(
                    f"Użytkownik {self.request.identity.name} dodał tag {tag.name} do firmy {company.name}"
                )
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
            person = Person(name=name[:100], position=position[:100], phone=phone[:50], email=email[:50])
            person.created_by = self.request.identity
            if person not in company.people:
                company.people.append(person)
                log.info(
                    f"Użytkownik {self.request.identity.name} dodał osobę {person.name} do firmy {company.name}"
                )
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
    def projects(self):
        company = self.request.context.company
        return dict(
            company=company,
            projects=[],  # require to render project_datalist.mako included in current template
        )

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
                    "company_results",
                    _query={
                        "name": form.name.data,
                        "street": form.street.data,
                        "postcode": form.postcode.data,
                        "city": form.city.data,
                        "state": form.state.data,
                        "WWW": form.WWW.data,
                        "NIP": form.NIP.data,
                        "REGON": form.REGON.data,
                        "KRS": form.KRS.data,
                        "court": form.court.data,
                        "color": form.color.data,
                    },
                )
            )
        return dict(
            heading="Znajdź firmę",
            form=form,
        )

    @view_config(
        route_name="company_results",
        renderer="company_table.mako",
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
        postcode = self.request.params.get("postcode")
        city = self.request.params.get("city")
        state = self.request.params.get("state")
        WWW = self.request.params.get("WWW")
        NIP = self.request.params.get("NIP")
        REGON = self.request.params.get("REGON")
        KRS = self.request.params.get("KRS")
        court = self.request.params.get("court")
        color = self.request.params.get("color")
        page = int(self.request.params.get("page", 1))
        states = dict(STATES)
        stmt = (
            select(Company)
            .filter(Company.name.ilike("%" + name + "%"))
            .filter(Company.street.ilike("%" + street + "%"))
            .filter(Company.postcode.ilike("%" + postcode + "%"))
            .filter(Company.city.ilike("%" + city + "%"))
            .filter(Company.state.ilike("%" + state + "%"))
            .filter(Company.WWW.ilike("%" + WWW + "%"))
            .filter(Company.NIP.ilike("%" + NIP + "%"))
            .filter(Company.REGON.ilike("%" + REGON + "%"))
            .filter(Company.KRS.ilike("%" + KRS + "%"))
            .filter(Company.court.ilike("%" + court + "%"))
            .filter(Company.color.ilike("%" + color + "%"))
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
                "postcode": postcode,
                "city": city,
                "state": state,
                "WWW": WWW,
                "NIP": NIP,
                "REGON": REGON,
                "KRS": KRS,
                "court": court,
                "color": color,
                "page": page + 1,
            },
        )

        return dict(
            paginator=paginator,
            next_page=next_page,
            states=states,
        )

    @view_config(
        route_name="delete_tag",
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
        route_name="person_delete_from_company",
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

    @view_config(
        route_name="add_project",
        renderer="project_list.mako",
        request_method="POST",
        permission="edit",
    )
    def add_project(self):
        new_csrf_token(self.request)
        company = self.request.context.company
        name = self.request.POST.get("name")
        if name:
            project = self.request.dbsession.execute(
                select(Project).filter_by(name=name)
            ).scalar_one_or_none()
            if project not in company.projects:
                company.projects.append(project)
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        return {"company": company}

    @view_config(
        route_name="delete_project",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def delete_project(self):
        new_csrf_token(self.request)
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

        company_name = company.name
        project_name = project.name

        company.projects.remove(project)
        log.info(
            f"Użytkownik {self.request.identity.name} usunął firmę {company_name} z projektu {project_name}"
        )
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        return ""
