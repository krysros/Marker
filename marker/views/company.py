import re
import logging
from operator import mul
from sqlalchemy import (
    select,
    func,
)
from sqlalchemy import and_

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther

import deform
from deform.schema import CSRFSchema
import colander

from ..models import (
    Company,
    Comment,
    Person,
    Branch,
    Investment,
    User,
    upvotes,
    companies_comments,
    companies_investments,
)

from ..paginator import get_paginator
from .select import (
    VOIVODESHIPS,
    CATEGORIES,
    COURTS,
)
from ..export import export_vcard


log = logging.getLogger(__name__)


def strip_whitespace(v):
    """Removes whitespace, newlines, and tabs from the beginning/end of a string."""
    return v.strip(" \t\n\r") if v is not colander.null else v


def remove_multiple_spaces(v):
    """Replaces multiple spaces with a single space."""
    return re.sub(" +", " ", v) if v is not colander.null else v


def remove_dashes_and_spaces(v):
    """Removes dashes and spaces from a string."""
    return v.replace("-", "").replace(" ", "") if v is not colander.null else v


def remove_mailto(v):
    """Removes "mailto:" from a string."""
    if v is not colander.null and v.startswith("mailto:"):
        return v[7:]
    else:
        return v


def extract_postcode(city):
    # Remove spaces at the beginning and at the end of the string
    city = city.strip()
    # Replace em dash, en dash, minus sign, hyphen-minus with a hypen
    city = (
        city.replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2212", "-")
        .replace("\u002D", "-")
    )
    # Extract postcode and city
    p = re.compile(r"\d{2}\s*-\s*\d{3}")
    postcode = p.findall(city)
    if postcode:
        postcode = postcode[0]
        city = city.replace(postcode, "").strip()
        postcode = postcode.replace("\t", "").replace(" ", "")
    else:
        postcode = ""
    return postcode, city


class CompanyView(object):
    def __init__(self, request):
        self.request = request

    @property
    def company_form(self):
        def check_name(node, value):
            exists = self.request.dbsession.execute(
                select(Company).filter_by(name=value)
            ).scalar_one_or_none()
            current_id = self.request.matchdict.get("company_id", None)
            if current_id:
                current_id = int(current_id)
            if exists and current_id != exists.id:
                raise colander.Invalid(node, "Ta nazwa firmy jest już zajęta")

        def validate_nip(node, value):
            if len(value) != 10 or not value.isdigit():
                raise colander.Invalid(
                    node, "Numer NIP powinien się składać z 10 cyfr"
                )

            digits = list(map(int, value))
            weights = (6, 5, 7, 2, 3, 4, 5, 6, 7)
            check_sum = sum(map(mul, digits[0:9], weights)) % 11
            if check_sum != digits[9]:
                raise colander.Invalid(node, "Nieprawidłowy numer NIP")

        def _check_sum_9(digits):
            weights9 = (8, 9, 2, 3, 4, 5, 6, 7)
            check_sum = sum(map(mul, digits[0:8], weights9)) % 11
            if check_sum == 10:
                check_sum = 0
            if check_sum == digits[8]:
                return True
            else:
                return False

        def _check_sum_14(digits):
            weights14 = (2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8)
            check_sum = sum(map(mul, digits[0:13], weights14)) % 11
            if check_sum == 10:
                check_sum = 0
            if check_sum == digits[13]:
                return True
            else:
                return False

        def validate_regon(node, value):
            if len(value) != 9 and len(value) != 14 or not value.isdigit():
                raise colander.Invalid(
                    node, "Numer REGON powinien się składać z 9 lub 14 cyfr"
                )
            digits = list(map(int, value))

            if len(value) == 9:
                valid = _check_sum_9(digits)
            else:
                valid = _check_sum_9(digits) and _check_sum_14(digits)

            if not valid:
                raise colander.Invalid(node, "Nieprawidłowy numer REGON")

        def validate_krs(node, value):
            if len(value) != 10 or not value.isdigit():
                raise colander.Invalid(
                    node, "Numer KRS powinien się składać z 10 cyfr"
                )

        widget = deform.widget.AutocompleteInputWidget(
            values=self.request.route_url("branch_select"),
        )

        class Branches(colander.SequenceSchema):
            name = colander.SchemaNode(
                colander.String(),
                title="Branża",
                widget=widget,
                validator=colander.Length(min=3, max=50),
            )

        class Persons(colander.Schema):
            fullname = colander.SchemaNode(
                colander.String(),
                title="Imię i nazwisko",
                validator=colander.Length(max=50),
            )
            position = colander.SchemaNode(
                colander.String(),
                title="Stanowisko",
                missing="",
                validator=colander.Length(max=50),
            )
            phone = colander.SchemaNode(
                colander.String(),
                title="Telefon",
                missing="",
                validator=colander.Length(max=50),
            )
            email = colander.SchemaNode(
                colander.String(),
                title="Email",
                missing="",
                preparer=[strip_whitespace, remove_mailto],
                validator=colander.Email(),
            )

        class People(colander.SequenceSchema):
            person = Persons(title="Nowy kontakt")

        class Schema(CSRFSchema):
            name = colander.SchemaNode(
                colander.String(),
                title="Nazwa firmy",
                validator=colander.All(
                    colander.Length(min=3, max=100), check_name
                ),
            )
            street = colander.SchemaNode(
                colander.String(),
                title="Ulica",
                missing="",
                validator=colander.Length(max=100),
            )
            city = colander.SchemaNode(
                colander.String(),
                title="Miasto",
                missing="",
                validator=colander.Length(max=100),
            )
            voivodeship = colander.SchemaNode(
                colander.String(),
                title="Województwo",
                missing="",
                widget=deform.widget.SelectWidget(values=VOIVODESHIPS),
            )
            phone = colander.SchemaNode(
                colander.String(),
                title="Telefon",
                missing="",
                validator=colander.Length(max=50),
            )
            email = colander.SchemaNode(
                colander.String(),
                title="Email",
                missing="",
                preparer=[strip_whitespace, remove_mailto],
                validator=colander.Email(),
            )
            www = colander.SchemaNode(
                colander.String(),
                title="WWW",
                missing="",
                validator=colander.Length(max=50),
            )
            nip = colander.SchemaNode(
                colander.String(),
                title="NIP",
                missing="",
                preparer=[
                    strip_whitespace,
                    remove_multiple_spaces,
                    remove_dashes_and_spaces,
                ],
                validator=validate_nip,
            )
            regon = colander.SchemaNode(
                colander.String(),
                title="REGON",
                missing="",
                preparer=[
                    strip_whitespace,
                    remove_multiple_spaces,
                    remove_dashes_and_spaces,
                ],
                validator=validate_regon,
            )
            krs = colander.SchemaNode(
                colander.String(),
                title="KRS",
                missing="",
                preparer=[
                    strip_whitespace,
                    remove_multiple_spaces,
                    remove_dashes_and_spaces,
                ],
                validator=validate_krs,
            )
            court = colander.SchemaNode(
                colander.String(),
                title="Sąd",
                missing="",
                widget=deform.widget.SelectWidget(values=COURTS),
            )
            category = colander.SchemaNode(
                colander.String(),
                title="Kategoria",
                missing="",
                widget=deform.widget.SelectWidget(values=CATEGORIES),
            )
            branches = Branches(title="Branże")
            people = People(title="Osoby do kontaktu")

        schema = Schema().bind(request=self.request)
        submit_btn = deform.form.Button(name="submit", title="Zapisz")
        form = deform.Form(schema, buttons=(submit_btn,))
        form["branches"].widget = deform.widget.SequenceWidget(min_len=1)
        return form

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
        voivodeships = dict(VOIVODESHIPS)
        stmt = select(Company)

        for k, _ in CATEGORIES:
            if filter == k:
                stmt = stmt.filter(Company.category == k)

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
            voivodeships=voivodeships,
        )

    @view_config(
        route_name="company_view",
        renderer="company_view.mako",
        permission="view",
    )
    def view(self):
        company = self.request.context.company
        voivodeships = dict(VOIVODESHIPS)

        # Counters
        c_comments = self.request.dbsession.scalar(
            select(func.count())
            .select_from(Comment)
            .join(companies_comments)
            .filter(company.id == companies_comments.c.company_id)
        )
        c_upvotes = self.request.dbsession.scalar(
            select(func.count())
            .select_from(User)
            .join(upvotes)
            .filter(company.id == upvotes.c.company_id)
        )
        c_investments = self.request.dbsession.scalar(
            select(func.count())
            .select_from(Investment)
            .join(companies_investments)
            .filter(company.id == companies_investments.c.company_id)
        )
        c_similar = self.request.dbsession.scalar(
            select(func.count())
            .select_from(Company)
            .join(Branch, Company.branches)
            .filter(
                and_(
                    Branch.companies.any(Company.id == company.id),
                    Company.id != company.id,
                )
            )
        )

        return dict(
            c_comments=c_comments,
            c_upvotes=c_upvotes,
            c_investments=c_investments,
            c_similar=c_similar,
            company=company,
            voivodeships=voivodeships,
            title=company.name,
        )

    @view_config(
        route_name="company_upvotes",
        renderer="company_upvotes.mako",
        permission="view",
    )
    @view_config(
        route_name="company_upvotes_more",
        renderer="user_more.mako",
        permission="view",
    )
    def upvotes(self):
        company = self.request.context.company
        page = int(self.request.params.get("page", 1))
        stmt = (
            select(User)
            .join(upvotes)
            .filter(company.id == upvotes.c.company_id)
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "company_upvotes_more",
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
        route_name="company_investments",
        renderer="company_investments.mako",
        permission="view",
    )
    @view_config(
        route_name="company_investments_more",
        renderer="investment_more.mako",
        permission="view",
    )
    def investments(self):
        company = self.request.context.company
        page = int(self.request.params.get("page", 1))
        stmt = (
            select(Investment)
            .join(companies_investments)
            .filter(company.id == companies_investments.c.company_id)
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "company_investments_more",
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
        voivodeships = dict(VOIVODESHIPS)

        stmt = (
            select(Company)
            .join(Branch, Company.branches)
            .filter(
                and_(
                    Branch.companies.any(Company.id == company.id),
                    Company.id != company.id,
                )
            )
            .group_by(Company)
            .order_by(
                func.count(
                    Branch.companies.any(Company.id == company.id)
                ).desc()
            )
        )

        if filter in list(voivodeships):
            stmt = stmt.filter(Company.voivodeship == filter)

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
                "voivodeships": voivodeships,
                "page": page + 1,
            },
        )

        return dict(
            company=company,
            filter=filter,
            paginator=paginator,
            next_page=next_page,
            voivodeships=voivodeships,
        )

    def _get_branches(self, appstruct):
        branches = []
        for b in appstruct["branches"]:
            branch = self.request.dbsession.execute(
                select(Branch).filter_by(name=b)
            ).scalar_one_or_none()
            if not branch:
                branch = Branch(name=b)
            if branch not in branches:
                branches.append(branch)
        return branches

    def _get_people(self, appstruct):
        people = []
        for p in appstruct["people"]:
            person = Person(
                fullname=p["fullname"],
                position=p["position"],
                phone=p["phone"],
                email=p["email"],
            )
            people.append(person)
        return people

    @view_config(
        route_name="company_add", renderer="form.mako", permission="edit"
    )
    def add(self):
        form = self.company_form
        appstruct = {}
        rendered_form = None

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                rendered_form = e.render()
            else:
                postcode, city = extract_postcode(appstruct["city"])
                company = Company(
                    name=appstruct["name"],
                    street=appstruct["street"],
                    postcode=postcode,
                    city=city,
                    voivodeship=appstruct["voivodeship"],
                    phone=appstruct["phone"],
                    email=appstruct["email"],
                    www=appstruct["www"],
                    nip=appstruct["nip"],
                    regon=appstruct["regon"],
                    krs=appstruct["krs"],
                    court=appstruct["court"],
                    category=appstruct["category"],
                    branches=self._get_branches(appstruct),
                    people=self._get_people(appstruct),
                )
                company.created_by = self.request.identity
                self.request.dbsession.add(company)
                self.request.session.flash("success:Dodano do bazy danych")
                log.info(
                    f"Użytkownik {self.request.identity.username} dodał firmę {company.name}"
                )
                next_url = self.request.route_url("company_all")
                return HTTPSeeOther(location=next_url)

        if rendered_form is None:
            rendered_form = form.render(appstruct=appstruct)
        reqts = form.get_widget_resources()

        return dict(
            heading="Dodaj firmę",
            rendered_form=rendered_form,
            css_links=reqts["css"],
            js_links=reqts["js"],
        )

    @view_config(
        route_name="company_edit", renderer="form.mako", permission="edit"
    )
    def edit(self):
        company = self.request.context.company
        form = self.company_form
        rendered_form = None

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                rendered_form = e.render()
            else:
                postcode, city = extract_postcode(appstruct["city"])
                company.name = appstruct["name"]
                company.street = appstruct["street"]
                company.postcode = postcode
                company.city = city
                company.voivodeship = appstruct["voivodeship"]
                company.phone = appstruct["phone"]
                company.email = appstruct["email"]
                company.www = appstruct["www"]
                company.nip = appstruct["nip"]
                company.regon = appstruct["regon"]
                company.krs = appstruct["krs"]
                company.court = appstruct["court"]
                company.category = appstruct["category"]
                company.branches = self._get_branches(appstruct)
                company.people = self._get_people(appstruct)
                company.updated_by = self.request.identity
                self.request.session.flash("success:Zmiany zostały zapisane")
                next_url = self.request.route_url(
                    "company_view", company_id=company.id, slug=company.slug
                )
                log.info(
                    f"Użytkownik {self.request.identity.username} zmienił dane firmy {company.name}"
                )
                return HTTPSeeOther(location=next_url)

        branches = []
        for b in company.branches:
            branches.append(b.name)

        people = []
        for p in company.people:
            people.append(
                {
                    "fullname": p.fullname,
                    "position": p.position,
                    "phone": p.phone,
                    "email": p.email,
                }
            )

        appstruct = dict(
            name=company.name,
            street=company.street,
            city=f"{company.postcode} {company.city}"
            if company.postcode
            else company.city,
            voivodeship=company.voivodeship,
            phone=company.phone,
            email=company.email,
            www=company.www,
            nip=company.nip,
            regon=company.regon,
            krs=company.krs,
            court=company.court,
            category=company.category,
            branches=branches,
            people=people,
        )

        if rendered_form is None:
            rendered_form = form.render(appstruct=appstruct)
        reqts = form.get_widget_resources()

        return dict(
            heading="Edytuj dane firmy",
            rendered_form=rendered_form,
            css_links=reqts["css"],
            js_links=reqts["js"],
        )

    @view_config(
        route_name="company_delete", request_method="POST", permission="edit"
    )
    def delete(self):
        company = self.request.context.company
        company_id = company.id
        company_name = company.name
        self.request.dbsession.delete(company)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(
            f"Użytkownik {self.request.identity.username} usunął firmę {company_name}"
        )
        next_url = self.request.route_url("home")
        return HTTPSeeOther(location=next_url)

    @view_config(
        route_name="company_upvote",
        request_method="POST",
        renderer="string",
        permission="view",
    )
    def upvote(self):
        company = self.request.context.company
        upvoted = self.request.identity.upvotes

        if company in upvoted:
            upvoted.remove(company)
            return '<span class="fa fa-thumbs-o-up fa-lg"></span>'
        else:
            upvoted.append(company)
            return '<span class="fa fa-thumbs-up fa-lg"></span>'

    @view_config(
        route_name="company_mark",
        request_method="POST",
        renderer="json",
        permission="view",
    )
    def mark(self):
        company = self.request.context.company
        marked = self.request.identity.marker

        if company in marked:
            marked.remove(company)
            return {"marked": False}
        else:
            marked.append(company)
            return {"marked": True}

    @view_config(
        route_name="company_select",
        request_method="GET",
        renderer="json",
    )
    def select(self):
        term = self.request.params.get("term")
        items = self.request.dbsession.execute(
            select(Company).filter(Company.name.ilike("%" + term + "%"))
        ).scalars()
        data = [i.name for i in items]
        return data

    @view_config(
        route_name="company_search",
        renderer="company_search.mako",
        permission="view",
    )
    def company_search(self):
        voivodeships = dict(VOIVODESHIPS)
        return {"voivodeships": voivodeships}

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
        voivodeship = self.request.params.get("voivodeship")
        phone = self.request.params.get("phone")
        email = self.request.params.get("email")
        www = self.request.params.get("www")
        nip = self.request.params.get("nip")
        regon = self.request.params.get("regon")
        krs = self.request.params.get("krs")
        page = int(self.request.params.get("page", 1))
        voivodeships = dict(VOIVODESHIPS)
        stmt = (
            select(Company)
            .filter(Company.name.ilike("%" + name + "%"))
            .filter(Company.street.ilike("%" + street + "%"))
            .filter(Company.city.ilike("%" + city + "%"))
            .filter(Company.voivodeship.ilike("%" + voivodeship + "%"))
            .filter(Company.phone.ilike("%" + phone + "%"))
            .filter(Company.email.ilike("%" + email + "%"))
            .filter(Company.www.ilike("%" + www + "%"))
            .filter(Company.nip.ilike("%" + nip + "%"))
            .filter(Company.regon.ilike("%" + regon + "%"))
            .filter(Company.krs.ilike("%" + krs + "%"))
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
                "voivodeship": voivodeship,
                "phone": phone,
                "email": email,
                "www": www,
                "nip": nip,
                "regon": regon,
                "krs": krs,
                "page": page + 1,
            },
        )

        return dict(
            paginator=paginator,
            next_page=next_page,
            voivodeships=voivodeships,
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
        fullname = self.request.params.get("fullname")
        position = self.request.params.get("position")
        phone = self.request.params.get("phone")
        email = self.request.params.get("email")
        page = int(self.request.params.get("page", 1))
        stmt = (
            select(Person)
            .filter(Person.fullname.ilike("%" + fullname + "%"))
            .filter(Person.position.ilike("%" + position + "%"))
            .filter(Person.phone.ilike("%" + phone + "%"))
            .filter(Person.email.ilike("%" + email + "%"))
            .order_by(Person.fullname)
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "person_results_more",
            _query={
                "fullname": fullname,
                "position": position,
                "phone": phone,
                "email": email,
                "page": page + 1,
            },
        )
        return {"paginator": paginator, "next_page": next_page}

    @view_config(
        route_name="person_vcard", request_method="POST", permission="view"
    )
    def vcard(self):
        person = self.request.context.person
        response = export_vcard(person)
        return response
