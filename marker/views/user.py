import datetime
import logging

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import delete, false, func, or_, select

from ..forms import (
    CommentFilterForm,
    CompanyFilterForm,
    ContactFilterForm,
    ProjectFilterForm,
    UserFilterForm,
    UserForm,
    UserSearchForm,
)
from ..forms.ts import TranslationString as _
from ..forms.select import (
    CATEGORIES,
    COLORS,
    ORDER_CRITERIA,
    PROJECT_DELIVERY_METHODS,
    SORT_CRITERIA,
    SORT_CRITERIA_COMPANIES,
    SORT_CRITERIA_CONTACTS,
    SORT_CRITERIA_EXT,
    SORT_CRITERIA_PROJECTS,
    STAGES,
    STATUS,
    USER_ROLES,
)
from ..models import (
    Comment,
    Company,
    Contact,
    Project,
    Tag,
    User,
    companies_stars,
    companies_tags,
    projects_stars,
    projects_tags,
    selected_companies,
    selected_contacts,
    selected_projects,
    selected_tags,
)
from ..utils.export import response_xlsx
from ..utils.paginator import get_paginator
from . import (
    Filter,
    clear_selected_rows,
    contains_ci,
    handle_bulk_selection,
    is_bulk_select_request,
    normalize_ci_expression,
    normalize_ci_value,
    polish_sort_expression,
    sort_column,
)

log = logging.getLogger(__name__)


class UserView:
    def __init__(self, request):
        self.request = request
        self.count_companies = 0
        self.count_projects = 0
        self.count_tags = 0
        self.count_contacts = 0
        self.count_comments = 0

    def _is_truthy(self, value):
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        return str(value).strip().lower() in {"1", "true", "on", "yes"}

    def _delete_user_with_data_requested(self):
        return self._is_truthy(self.request.params.get("delete_with_data"))

    def _delete_user_created_data(self, user):
        dbsession = self.request.dbsession

        companies_to_delete = (
            dbsession.execute(select(Company).where(Company.creator_id == user.id))
            .scalars()
            .all()
        )
        projects_to_delete = (
            dbsession.execute(select(Project).where(Project.creator_id == user.id))
            .scalars()
            .all()
        )

        company_ids = [company.id for company in companies_to_delete]
        project_ids = [project.id for project in projects_to_delete]

        created_contact_ids = (
            dbsession.execute(select(Contact.id).where(Contact.creator_id == user.id))
            .scalars()
            .all()
        )
        created_tag_ids = (
            dbsession.execute(select(Tag.id).where(Tag.creator_id == user.id))
            .scalars()
            .all()
        )
        created_comment_ids = (
            dbsession.execute(select(Comment.id).where(Comment.creator_id == user.id))
            .scalars()
            .all()
        )

        company_contact_ids = []
        project_contact_ids = []

        if company_ids:
            company_contact_ids = (
                dbsession.execute(
                    select(Contact.id).where(Contact.company_id.in_(company_ids))
                )
                .scalars()
                .all()
            )

        if project_ids:
            project_contact_ids = (
                dbsession.execute(
                    select(Contact.id).where(Contact.project_id.in_(project_ids))
                )
                .scalars()
                .all()
            )

        contact_ids_to_delete = list(
            {
                *created_contact_ids,
                *company_contact_ids,
                *project_contact_ids,
            }
        )

        clear_selected_rows(
            self.request,
            selected_contacts,
            selected_contacts.c.contact_id,
            contact_ids_to_delete,
        )
        clear_selected_rows(
            self.request,
            selected_companies,
            selected_companies.c.company_id,
            company_ids,
        )
        clear_selected_rows(
            self.request,
            selected_projects,
            selected_projects.c.project_id,
            project_ids,
        )
        clear_selected_rows(
            self.request,
            selected_tags,
            selected_tags.c.tag_id,
            created_tag_ids,
        )
        clear_selected_rows(
            self.request,
            companies_stars,
            companies_stars.c.company_id,
            company_ids,
        )
        clear_selected_rows(
            self.request,
            projects_stars,
            projects_stars.c.project_id,
            project_ids,
        )

        for company in companies_to_delete:
            dbsession.delete(company)

        for project in projects_to_delete:
            dbsession.delete(project)

        dbsession.flush()

        if created_tag_ids:
            dbsession.execute(delete(Tag).where(Tag.id.in_(created_tag_ids)))

        if created_contact_ids:
            dbsession.execute(
                delete(Contact).where(Contact.id.in_(created_contact_ids))
            )

        if created_comment_ids:
            dbsession.execute(
                delete(Comment).where(Comment.id.in_(created_comment_ids))
            )

    def pills(self, user):
        _ = self.request.translate
        return [
            {
                "title": _("User"),
                "icon": "person-circle",
                "url": self.request.route_url("user_view", username=user.name),
                "count": None,
            },
            {
                "title": _("Companies"),
                "icon": "buildings",
                "url": self.request.route_url("user_companies", username=user.name),
                "count": self.request.route_url(
                    "user_count_companies", username=user.name
                ),
                "event": "userEvent",
                "init_value": self.count_companies,
            },
            {
                "title": _("Projects"),
                "icon": "briefcase",
                "url": self.request.route_url("user_projects", username=user.name),
                "count": self.request.route_url(
                    "user_count_projects", username=user.name
                ),
                "event": "userEvent",
                "init_value": self.count_projects,
            },
            {
                "title": _("Tags"),
                "icon": "tags",
                "url": self.request.route_url("user_tags", username=user.name),
                "count": self.request.route_url("user_count_tags", username=user.name),
                "event": "userEvent",
                "init_value": self.count_tags,
            },
            {
                "title": _("Contacts"),
                "icon": "people",
                "url": self.request.route_url("user_contacts", username=user.name),
                "count": self.request.route_url(
                    "user_count_contacts", username=user.name
                ),
                "event": "userEvent",
                "init_value": self.count_contacts,
            },
            {
                "title": _("Comments"),
                "icon": "chat-left-text",
                "url": self.request.route_url("user_comments", username=user.name),
                "count": self.request.route_url(
                    "user_count_comments", username=user.name
                ),
                "event": "userEvent",
                "init_value": self.count_comments,
            },
        ]

    def _contact_export_header(self):
        _ = self.request.translate
        return [
            _("Contact name"),
            _("Contact role"),
            _("Contact phone"),
            _("Contact email"),
        ]

    def _company_export_header(self):
        _ = self.request.translate
        return [
            *self._contact_export_header(),
            _("Company name"),
            _("Company street"),
            _("Company post code"),
            _("Company city"),
            _("Company subdivision"),
            _("Company country"),
            _("Company website"),
            _("Company NIP"),
            _("Company REGON"),
            _("Company KRS"),
            _("Company court"),
            _("Tags"),
        ]

    def _project_export_header(self):
        _ = self.request.translate
        return [
            *self._contact_export_header(),
            _("Project name"),
            _("Project street"),
            _("Project post code"),
            _("Project city"),
            _("Project subdivision"),
            _("Project country"),
            _("Project website"),
            _("Project deadline"),
            _("Project stage"),
            _("Project delivery method"),
            _("Tags"),
        ]

    def _tag_export_header(self, category="companies"):
        _ = self.request.translate
        if category == "projects":
            return [
                *self._contact_export_header(),
                _("Tag"),
                _("Project name"),
                _("Project street"),
                _("Project post code"),
                _("Project city"),
                _("Project subdivision"),
                _("Project country"),
                _("Project website"),
                _("Project deadline"),
                _("Project stage"),
                _("Project delivery method"),
                _("Tags"),
            ]

        return [
            *self._contact_export_header(),
            _("Tag"),
            _("Company name"),
            _("Company street"),
            _("Company post code"),
            _("Company city"),
            _("Company subdivision"),
            _("Company country"),
            _("Company website"),
            _("Company NIP"),
            _("Company REGON"),
            _("Company KRS"),
            _("Company court"),
            _("Tags"),
        ]

    def _tags_as_string(self, tags):
        names = [tag.name for tag in tags if getattr(tag, "name", None)]
        return " ::: ".join(sorted(names))

    def _contact_row_values(self, contact):
        return [
            contact.name,
            contact.role,
            contact.phone,
            contact.email,
        ]

    def _resolve_row_color(self, object_color, contact_color=None):
        return contact_color or object_color or ""

    def _filter_tags_by_category(self, stmt, category, q=None):
        normalized_category = category if category in {"companies", "projects"} else ""
        if normalized_category == "projects":
            stmt = stmt.filter(Tag.projects.any())
        elif normalized_category == "companies":
            stmt = stmt.filter(Tag.companies.any())

        if q is not None and normalized_category:
            q["category"] = normalized_category

        return stmt, normalized_category

    def _company_row_values(self, company):
        return [
            company.name,
            company.street,
            company.postcode,
            company.city,
            company.subdivision,
            company.country,
            company.website,
            company.NIP,
            company.REGON,
            company.KRS,
            company.court,
        ]

    def _project_row_values(self, project):
        return [
            project.name,
            project.street,
            project.postcode,
            project.city,
            project.subdivision,
            project.country,
            project.website,
            project.deadline,
            project.stage,
            project.delivery_method,
        ]

    def _selected_contacts_export_header(self, category):
        if category == "projects":
            return self._project_export_header()
        return self._company_export_header()

    def _selected_contacts_export_rows(self, contacts, category):
        rows = []
        row_colors = []
        is_projects = category == "projects"

        for contact in contacts:
            linked_object = contact.project if is_projects else contact.company

            if linked_object:
                if is_projects:
                    base_values = self._project_row_values(linked_object)
                else:
                    base_values = self._company_row_values(linked_object)
                tags_value = self._tags_as_string(linked_object.tags)
                object_color = linked_object.color
            else:
                base_values = [""] * (10 if is_projects else 11)
                tags_value = ""
                object_color = ""

            rows.append(
                [
                    *self._contact_row_values(contact),
                    *base_values,
                    tags_value,
                ]
            )
            row_colors.append(self._resolve_row_color(object_color, contact.color))

        return rows, row_colors

    def _rows_for_objects_with_contacts(self, objects, get_base_values):
        rows = []
        row_colors = []

        for obj in objects:
            base_values = get_base_values(obj)
            tags_value = self._tags_as_string(obj.tags)
            contacts = list(obj.contacts)

            if not contacts:
                rows.append(["", "", "", "", *base_values, tags_value])
                row_colors.append(self._resolve_row_color(obj.color))
                continue

            for contact in contacts:
                rows.append(
                    [
                        *self._contact_row_values(contact),
                        *base_values,
                        tags_value,
                    ]
                )
                row_colors.append(self._resolve_row_color(obj.color, contact.color))

        return rows, row_colors

    def _company_export_rows(self, companies):
        return self._rows_for_objects_with_contacts(companies, self._company_row_values)

    def _project_export_rows(self, projects):
        return self._rows_for_objects_with_contacts(projects, self._project_row_values)

    def _tag_export_rows(self, tags, category="companies"):
        rows = []
        row_colors = []
        empty_contact = ["", "", "", ""]

        for tag in tags:
            if category == "projects":
                for project in tag.projects:
                    project_values = self._project_row_values(project)
                    tags_value = self._tags_as_string(project.tags)
                    contacts = list(project.contacts)

                    if not contacts:
                        rows.append(
                            [
                                *empty_contact,
                                tag.name,
                                *project_values,
                                tags_value,
                            ]
                        )
                        row_colors.append(self._resolve_row_color(project.color))
                        continue

                    for contact in contacts:
                        rows.append(
                            [
                                *self._contact_row_values(contact),
                                tag.name,
                                *project_values,
                                tags_value,
                            ]
                        )
                        row_colors.append(
                            self._resolve_row_color(project.color, contact.color)
                        )

                if not tag.projects:
                    rows.append(
                        [
                            *empty_contact,
                            tag.name,
                            *([""] * 10),
                            "",
                        ]
                    )
                    row_colors.append("")
                continue

            for company in tag.companies:
                company_values = self._company_row_values(company)
                tags_value = self._tags_as_string(company.tags)
                contacts = list(company.contacts)

                if not contacts:
                    rows.append(
                        [
                            *empty_contact,
                            tag.name,
                            *company_values,
                            tags_value,
                        ]
                    )
                    row_colors.append(self._resolve_row_color(company.color))
                    continue

                for contact in contacts:
                    rows.append(
                        [
                            *self._contact_row_values(contact),
                            tag.name,
                            *company_values,
                            tags_value,
                        ]
                    )
                    row_colors.append(
                        self._resolve_row_color(company.color, contact.color)
                    )

            if not tag.companies:
                rows.append(
                    [
                        *empty_contact,
                        tag.name,
                        *([""] * 11),
                        "",
                    ]
                )
                row_colors.append("")
        return rows, row_colors

    @view_config(route_name="user_all", renderer="user_all.mako", permission="view")
    @view_config(route_name="user_more", renderer="user_more.mako", permission="view")
    def all(self):
        page = int(self.request.params.get("page", 1))
        name = self.request.params.get("name", None)
        fullname = self.request.params.get("fullname", None)
        email = self.request.params.get("email", None)
        role = self.request.params.get("role", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        roles = dict(USER_ROLES)
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        q = {}

        allowed_sorts = set(sort_criteria)
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = select(User)

        if name:
            stmt = stmt.filter(contains_ci(User.name, name))
            q["name"] = name

        if fullname:
            stmt = stmt.filter(contains_ci(User.fullname, fullname))
            q["fullname"] = fullname

        if email:
            stmt = stmt.filter(contains_ci(User.email, email))
            q["email"] = email

        if role:
            stmt = stmt.filter(contains_ci(User.role, role))
            q["role"] = role

        q["sort"] = _sort
        q["order"] = _order

        if _order == "asc":
            stmt = stmt.order_by(sort_column(User, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(sort_column(User, _sort).desc())

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.subquery())
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more",
            _query={
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = UserFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "roles": roles,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "form": form,
        }

    @view_config(route_name="user_view", renderer="user_view.mako", permission="view")
    def view(self):
        user = self.request.context.user
        self.count_companies = user.count_companies
        self.count_projects = user.count_projects
        self.count_tags = user.count_tags
        self.count_contacts = user.count_contacts
        self.count_comments = user.count_comments
        return {
            "user": user,
            "title": user.fullname,
            "user_pills": self.pills(user),
        }

    @view_config(
        route_name="user_comments",
        renderer="user_comments.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_comments",
        renderer="comment_more.mako",
        permission="view",
    )
    def comments(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        category = self.request.params.get("category", "")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        order_criteria = dict(ORDER_CRITERIA)
        categories = dict(CATEGORIES)
        q = {}

        _sort = "created_at"
        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = select(Comment).filter(Comment.created_by == user)

        if category == "companies":
            stmt = stmt.filter(Comment.company)
            q["category"] = category
        elif category == "projects":
            stmt = stmt.filter(Comment.project)
            q["category"] = category

        if _order == "asc":
            stmt = stmt.order_by(Comment.created_at.asc())
        elif _order == "desc":
            stmt = stmt.order_by(Comment.created_at.desc())

        q["sort"] = _sort
        q["order"] = _order

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        self.count_companies = user.count_companies
        self.count_projects = user.count_projects
        self.count_tags = user.count_tags
        self.count_contacts = user.count_contacts
        self.count_comments = counter

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "user_more_comments",
            username=user.name,
            _query={**q, "page": page + 1},
        )

        obj = Filter(**q)
        form = CommentFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "user": user,
            "paginator": paginator,
            "order_criteria": order_criteria,
            "categories": categories,
            "next_page": next_page,
            "title": user.fullname,
            "user_pills": self.pills(user),
            "form": form,
        }

    @view_config(
        route_name="user_tags",
        renderer="user_tags.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_tags",
        renderer="tag_more.mako",
        permission="view",
    )
    def tags(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        category = self.request.params.get("category", "")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA)
        sort_criteria["name"] = self.request.translate("Tag")
        order_criteria = dict(ORDER_CRITERIA)
        categories = dict(CATEGORIES)
        q = {}

        allowed_sorts = set(sort_criteria)
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        q["sort"] = _sort
        q["order"] = _order

        stmt = select(Tag).filter(Tag.created_by == user)
        stmt, category = self._filter_tags_by_category(stmt, category, q=q)

        if _order == "asc":
            stmt = stmt.order_by(sort_column(Tag, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(sort_column(Tag, _sort).desc())

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_tags
            )

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        self.count_companies = user.count_companies
        self.count_projects = user.count_projects
        self.count_tags = counter
        self.count_contacts = user.count_contacts
        self.count_comments = user.count_comments

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more_tags",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        return {
            "q": q,
            "user": user,
            "paginator": paginator,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "categories": categories,
            "next_page": next_page,
            "title": user.fullname,
            "user_pills": self.pills(user),
        }

    @view_config(
        route_name="user_export_tags",
        permission="view",
    )
    def export_tags(self):
        _ = self.request.translate
        user = self.request.context.user
        category = self.request.params.get("category", "companies")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")

        allowed_sorts = {"name", "created_at", "updated_at"}
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = select(Tag).filter(Tag.created_by == user)
        stmt, category = self._filter_tags_by_category(stmt, category)

        if _order == "asc":
            stmt = stmt.order_by(sort_column(Tag, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(sort_column(Tag, _sort).desc())

        tags = self.request.dbsession.execute(stmt).scalars().all()
        rows, row_colors = self._tag_export_rows(tags, category=category)
        header_row = self._tag_export_header(category=category)
        response = response_xlsx(rows, header_row, row_colors=row_colors)
        log.info(
            _("The user %s exported the data of selected tags")
            % self.request.identity.name
        )
        return response

    @view_config(
        route_name="user_companies",
        renderer="user_companies.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_companies",
        renderer="company_more.mako",
        permission="view",
    )
    def companies(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        name = self.request.params.get("name", None)
        street = self.request.params.get("street", None)
        postcode = self.request.params.get("postcode", None)
        city = self.request.params.get("city", None)
        subdivision = self.request.params.getall("subdivision")
        country = self.request.params.get("country", None)
        website = self.request.params.get("website", None)
        color = self.request.params.get("color", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA_COMPANIES)
        sort_criteria["name"] = self.request.translate("Company")
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        q = {}

        allowed_sorts = {
            "name",
            "city",
            "subdivision",
            "country",
            "created_at",
            "updated_at",
            "stars",
            "comments",
        }
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = select(Company).filter(Company.created_by == user)

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
                    .order_by(func.count(Company.comments).asc(), Company.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(Company.comments)
                    .group_by(Company)
                    .order_by(func.count(Company.comments).desc(), Company.id)
                )
        else:
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Company, _sort).asc(), Company.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Company, _sort).desc(), Company.id)

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_companies
            )

        q["sort"] = _sort
        q["order"] = _order

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        self.count_companies = counter
        self.count_projects = user.count_projects
        self.count_tags = user.count_tags
        self.count_contacts = user.count_contacts
        self.count_comments = user.count_comments

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more_companies",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = CompanyFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "colors": colors,
            "paginator": paginator,
            "next_page": next_page,
            "title": user.fullname,
            "user_pills": self.pills(user),
            "form": form,
        }

    @view_config(
        route_name="user_export_companies",
        permission="view",
    )
    def export_companies(self):
        _ = self.request.translate
        user = self.request.context.user
        name = self.request.params.get("name", None)
        street = self.request.params.get("street", None)
        postcode = self.request.params.get("postcode", None)
        city = self.request.params.get("city", None)
        subdivision = self.request.params.getall("subdivision")
        country = self.request.params.get("country", None)
        website = self.request.params.get("website", None)
        color = self.request.params.get("color", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")

        allowed_sorts = {
            "name",
            "city",
            "subdivision",
            "country",
            "created_at",
            "updated_at",
            "stars",
            "comments",
        }
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = select(Company).filter(Company.created_by == user)

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
            stmt = stmt.filter(Company.subdivision.in_(subdivision))

        if country:
            stmt = stmt.filter(Company.country == country)

        if color:
            stmt = stmt.filter(Company.color == color)

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
                    .order_by(func.count(Company.comments).asc(), Company.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(Company.comments)
                    .group_by(Company)
                    .order_by(func.count(Company.comments).desc(), Company.id)
                )
        else:
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Company, _sort).asc(), Company.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Company, _sort).desc(), Company.id)

        companies = self.request.dbsession.execute(stmt).scalars().all()
        rows, row_colors = self._company_export_rows(companies)
        header_row = self._company_export_header()
        response = response_xlsx(rows, header_row, row_colors=row_colors)
        log.info(
            _("The user %s exported the data of selected companies")
            % self.request.identity.name
        )
        return response

    @view_config(
        route_name="user_projects",
        renderer="user_projects.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_projects",
        renderer="project_more.mako",
        permission="view",
    )
    def projects(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        name = self.request.params.get("name", None)
        street = self.request.params.get("street", None)
        postcode = self.request.params.get("postcode", None)
        city = self.request.params.get("city", None)
        subdivision = self.request.params.getall("subdivision")
        country = self.request.params.get("country", None)
        website = self.request.params.get("website", None)
        color = self.request.params.get("color", None)
        deadline = self.request.params.get("deadline", None)
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        order_criteria = dict(ORDER_CRITERIA)
        sort_criteria = dict(SORT_CRITERIA_PROJECTS)
        sort_criteria["name"] = self.request.translate("Project")
        colors = dict(COLORS)
        statuses = dict(STATUS)
        stages = dict(STAGES)
        project_delivery_methods = dict(PROJECT_DELIVERY_METHODS)
        now = datetime.datetime.now()
        q = {}

        allowed_sorts = {
            "name",
            "city",
            "subdivision",
            "country",
            "created_at",
            "updated_at",
            "stars",
            "comments",
        }
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = select(Project).filter(Project.created_by == user)

        if name:
            normalized_name = normalize_ci_value(name)
            stmt = stmt.filter(
                normalize_ci_expression(Project.name).like("%" + normalized_name + "%")
            )
            q["name"] = name

        if street:
            stmt = stmt.filter(contains_ci(Project.street, street))
            q["street"] = street

        if postcode:
            stmt = stmt.filter(contains_ci(Project.postcode, postcode))
            q["postcode"] = postcode

        if city:
            stmt = stmt.filter(contains_ci(Project.city, city))
            q["city"] = city

        if website:
            stmt = stmt.filter(contains_ci(Project.website, website))
            q["website"] = website

        if subdivision:
            stmt = stmt.filter(Project.subdivision.in_(subdivision))
            q["subdivision"] = list(subdivision)

        if country:
            stmt = stmt.filter(Project.country == country)
            q["country"] = country

        if color:
            stmt = stmt.filter(Project.color == color)
            q["color"] = color

        if stage:
            stmt = stmt.filter(Project.stage == stage)
            q["stage"] = stage

        if delivery_method:
            stmt = stmt.filter(Project.delivery_method == delivery_method)
            q["delivery_method"] = delivery_method

        if deadline:
            deadline_dt = datetime.datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
            stmt = stmt.filter(Project.deadline <= deadline_dt)
            q["deadline"] = deadline

        if status == "in_progress":
            stmt = stmt.filter(Project.deadline > now)
            q["status"] = status
        elif status == "completed":
            stmt = stmt.filter(Project.deadline < now)
            q["status"] = status

        if _sort == "stars":
            if _order == "asc":
                stmt = (
                    stmt.join(projects_stars)
                    .group_by(Project)
                    .order_by(func.count(projects_stars.c.project_id).asc(), Project.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(projects_stars)
                    .group_by(Project)
                    .order_by(
                        func.count(projects_stars.c.project_id).desc(), Project.id
                    )
                )
        elif _sort == "comments":
            if _order == "asc":
                stmt = (
                    stmt.join(Project.comments)
                    .group_by(Project)
                    .order_by(func.count(Project.comments).asc(), Project.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(Project.comments)
                    .group_by(Project)
                    .order_by(func.count(Project.comments).desc(), Project.id)
                )
        else:
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Project, _sort).asc(), Project.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Project, _sort).desc(), Project.id)

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_projects
            )

        q["sort"] = _sort
        q["order"] = _order

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        self.count_companies = user.count_companies
        self.count_projects = counter
        self.count_tags = user.count_tags
        self.count_contacts = user.count_contacts
        self.count_comments = user.count_comments

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more_projects",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = ProjectFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "colors": colors,
            "statuses": statuses,
            "stages": stages,
            "project_delivery_methods": project_delivery_methods,
            "paginator": paginator,
            "next_page": next_page,
            "title": user.fullname,
            "user_pills": self.pills(user),
            "form": form,
        }

    @view_config(
        route_name="user_export_projects",
        permission="view",
    )
    def export_projects(self):
        _ = self.request.translate
        user = self.request.context.user
        name = self.request.params.get("name", None)
        street = self.request.params.get("street", None)
        postcode = self.request.params.get("postcode", None)
        city = self.request.params.get("city", None)
        subdivision = self.request.params.getall("subdivision")
        country = self.request.params.get("country", None)
        website = self.request.params.get("website", None)
        color = self.request.params.get("color", None)
        deadline = self.request.params.get("deadline", None)
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()

        allowed_sorts = {
            "name",
            "city",
            "subdivision",
            "country",
            "created_at",
            "updated_at",
            "stars",
            "comments",
        }
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = select(Project).filter(Project.created_by == user)

        if name:
            normalized_name = normalize_ci_value(name)
            stmt = stmt.filter(
                normalize_ci_expression(Project.name).like("%" + normalized_name + "%")
            )

        if street:
            stmt = stmt.filter(contains_ci(Project.street, street))

        if postcode:
            stmt = stmt.filter(contains_ci(Project.postcode, postcode))

        if city:
            stmt = stmt.filter(contains_ci(Project.city, city))

        if website:
            stmt = stmt.filter(contains_ci(Project.website, website))

        if subdivision:
            stmt = stmt.filter(Project.subdivision.in_(subdivision))

        if country:
            stmt = stmt.filter(Project.country == country)

        if color:
            stmt = stmt.filter(Project.color == color)

        if stage:
            stmt = stmt.filter(Project.stage == stage)

        if delivery_method:
            stmt = stmt.filter(Project.delivery_method == delivery_method)

        if deadline:
            deadline_dt = datetime.datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
            stmt = stmt.filter(Project.deadline <= deadline_dt)

        if status == "in_progress":
            stmt = stmt.filter(Project.deadline > now)
        elif status == "completed":
            stmt = stmt.filter(Project.deadline < now)

        if _sort == "stars":
            if _order == "asc":
                stmt = (
                    stmt.join(projects_stars)
                    .group_by(Project)
                    .order_by(func.count(projects_stars.c.project_id).asc(), Project.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(projects_stars)
                    .group_by(Project)
                    .order_by(
                        func.count(projects_stars.c.project_id).desc(), Project.id
                    )
                )
        elif _sort == "comments":
            if _order == "asc":
                stmt = (
                    stmt.join(Project.comments)
                    .group_by(Project)
                    .order_by(func.count(Project.comments).asc(), Project.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.join(Project.comments)
                    .group_by(Project)
                    .order_by(func.count(Project.comments).desc(), Project.id)
                )
        else:
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Project, _sort).asc(), Project.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Project, _sort).desc(), Project.id)

        projects = self.request.dbsession.execute(stmt).scalars().all()
        rows, row_colors = self._project_export_rows(projects)
        header_row = self._project_export_header()
        response = response_xlsx(rows, header_row, row_colors=row_colors)
        log.info(
            _("The user %s exported the data of selected projects")
            % self.request.identity.name
        )
        return response

    @view_config(
        route_name="user_contacts",
        renderer="user_contacts.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_contacts",
        renderer="contact_more.mako",
        permission="view",
    )
    def contacts(self):
        user = self.request.context.user
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
        sort_criteria["name"] = self.request.translate("Name")
        order_criteria = dict(ORDER_CRITERIA)
        categories = dict(CATEGORIES)
        q = {}

        allowed_sorts = set(sort_criteria)
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = select(Contact).filter(Contact.created_by == user)

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

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_contacts
            )

        if _sort in {"country", "subdivision"}:
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
                    stmt = stmt.order_by(func.lower(relation_sort).asc(), Contact.id)
                elif _order == "desc":
                    stmt = stmt.order_by(func.lower(relation_sort).desc(), Contact.id)
        else:
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Contact, _sort).asc(), Contact.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Contact, _sort).desc(), Contact.id)

        q["sort"] = _sort
        q["order"] = _order

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        self.count_companies = user.count_companies
        self.count_projects = user.count_projects
        self.count_tags = user.count_tags
        self.count_contacts = counter
        self.count_comments = user.count_comments

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more_contacts",
            username=user.name,
            _query={**q, "page": page + 1},
        )

        obj = Filter(**q)
        form = ContactFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "categories": categories,
            "paginator": paginator,
            "next_page": next_page,
            "title": user.fullname,
            "user_pills": self.pills(user),
            "form": form,
        }

    @view_config(
        route_name="user_export_contacts",
        permission="view",
    )
    def export_contacts(self):
        _ = self.request.translate
        user = self.request.context.user
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

        allowed_sorts = {
            "name",
            "role",
            "country",
            "subdivision",
            "color",
            "created_at",
            "updated_at",
        }
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = select(Contact).filter(Contact.created_by == user)

        if name:
            stmt = stmt.filter(contains_ci(Contact.name, name))

        if role:
            stmt = stmt.filter(contains_ci(Contact.role, role))

        if phone:
            stmt = stmt.filter(contains_ci(Contact.phone, phone))

        if email:
            stmt = stmt.filter(contains_ci(Contact.email, email))

        if category == "projects":
            stmt = stmt.filter(Contact.project)
            if country:
                stmt = stmt.filter(Contact.project.has(Project.country == country))
            if subdivision:
                stmt = stmt.filter(
                    Contact.project.has(Project.subdivision.in_(subdivision))
                )
        else:
            category = "companies"
            stmt = stmt.filter(Contact.company)
            if country:
                stmt = stmt.filter(Contact.company.has(Company.country == country))
            if subdivision:
                stmt = stmt.filter(
                    Contact.company.has(Company.subdivision.in_(subdivision))
                )

        if color:
            stmt = stmt.filter(Contact.color == color)

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
        else:
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Contact, _sort).asc(), Contact.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Contact, _sort).desc(), Contact.id)

        contacts = self.request.dbsession.execute(stmt).scalars().all()
        rows, row_colors = self._selected_contacts_export_rows(contacts, category)
        header_row = self._selected_contacts_export_header(category)
        response = response_xlsx(rows, header_row, row_colors=row_colors)

        log.info(
            _("The user %s exported the data of selected contacts")
            % self.request.identity.name
        )
        return response

    @view_config(route_name="user_add", renderer="user_form.mako", permission="admin")
    def add(self):
        _ = self.request.translate
        form = UserForm(self.request.POST, request=self.request)
        if self.request.method == "POST" and form.validate():
            user = User(
                name=form.name.data,
                fullname=form.fullname.data,
                email=form.email.data,
                role=form.role.data,
                password=form.password.data,
            )
            self.request.dbsession.add(user)
            self.request.session.flash(_("success:Added to the database"))
            log.info(_("The user %s has added a user") % self.request.identity.name)
            next_url = self.request.route_url("user_all")
            return HTTPSeeOther(location=next_url)
        return {"heading": _("Add user"), "form": form}

    @view_config(route_name="user_edit", renderer="user_form.mako", permission="admin")
    def edit(self):
        _ = self.request.translate
        user = self.request.context.user
        form = UserForm(
            self.request.POST,
            user,
            request=self.request,
        )
        if self.request.method == "POST" and form.validate():
            form.populate_obj(user)
            self.request.session.flash(_("success:Changes have been saved"))
            log.info(
                _("The user %s has changed the user's data")
                % self.request.identity.name
            )
            next_url = self.request.route_url("user_all")
            return HTTPSeeOther(location=next_url)
        return {"heading": _("Edit user details"), "form": form}

    @view_config(route_name="user_delete", request_method="POST", permission="admin")
    def delete(self):
        _ = self.request.translate
        user = self.request.context.user
        with_data = self._delete_user_with_data_requested()

        if with_data:
            self._delete_user_created_data(user)

        self.request.dbsession.delete(user)

        if with_data:
            self.request.session.flash(
                _("success:Removed user account with all added data from the database")
            )
            log.info(
                _("The user %s deleted the user with all added data")
                % self.request.identity.name
            )
        else:
            self.request.session.flash(_("success:Removed from the database"))
            log.info(_("The user %s deleted the user") % self.request.identity.name)

        next_url = self.request.route_url("home")
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="user_search",
        renderer="user_search.mako",
        permission="view",
    )
    def search(self):
        _ = self.request.translate
        form = UserSearchForm(self.request.POST)
        q = {}
        for fieldname, value in form.data.items():
            if value:
                q[fieldname] = value

        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "user_all",
                    _query=q,
                )
            )
        return {"heading": _("Find a user"), "form": form}

    @view_config(
        route_name="user_selected_companies",
        renderer="user_selected_companies.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_selected_companies",
        renderer="company_more.mako",
        permission="view",
    )
    def selected_companies(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA_EXT)
        sort_criteria["name"] = self.request.translate("Company")
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        q = {}

        allowed_sorts = {
            "name",
            "city",
            "subdivision",
            "country",
            "created_at",
            "updated_at",
        }
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = (
            select(Company)
            .join(selected_companies)
            .filter(user.id == selected_companies.c.user_id)
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

        if _order == "asc":
            stmt = stmt.order_by(sort_column(Company, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(sort_column(Company, _sort).desc())

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_companies
            )

        q["sort"] = _sort
        q["order"] = _order

        obj = Filter(**q)
        form = CompanyFilterForm(self.request.GET, obj, request=self.request)

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more_selected_companies",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "counter": counter,
            "form": form,
        }

    @view_config(
        route_name="user_json_selected_companies",
        renderer="json",
        permission="view",
    )
    def json_selected_companies(self):
        user = self.request.context.user
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        stmt = (
            select(Company)
            .join(selected_companies)
            .filter(user.id == selected_companies.c.user_id)
        )

        if color:
            stmt = stmt.filter(Company.color == color)

        if country:
            stmt = stmt.filter(Company.country == country)

        if subdivision:
            stmt = stmt.filter(Company.subdivision.in_(subdivision))

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
        route_name="user_map_selected_companies",
        renderer="user_map_selected_companies.mako",
        permission="view",
    )
    def map_selected_companies(self):
        user = self.request.context.user
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        q = {}

        allowed_sorts = {
            "name",
            "city",
            "subdivision",
            "country",
            "created_at",
            "updated_at",
        }
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = (
            select(Company)
            .join(selected_companies)
            .filter(user.id == selected_companies.c.user_id)
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

        if _order == "asc":
            stmt = stmt.order_by(sort_column(Company, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(sort_column(Company, _sort).desc())

        q["sort"] = _sort
        q["order"] = _order

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        url = self.request.route_url(
            "user_json_selected_companies", username=user.name, _query=q
        )
        return {"user": user, "url": url, "q": q, "counter": counter}

    @view_config(
        route_name="user_export_selected_companies",
        permission="view",
    )
    def export_selected_companies(self):
        _ = self.request.translate
        user = self.request.context.user
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")

        allowed_sorts = {
            "name",
            "city",
            "subdivision",
            "country",
            "created_at",
            "updated_at",
        }
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = (
            select(Company)
            .join(selected_companies)
            .filter(user.id == selected_companies.c.user_id)
        )

        if _order == "asc":
            stmt = stmt.order_by(sort_column(Company, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(sort_column(Company, _sort).desc())

        companies = self.request.dbsession.execute(stmt).scalars().all()
        rows, row_colors = self._company_export_rows(companies)

        header_row = self._company_export_header()
        response = response_xlsx(rows, header_row, row_colors=row_colors)
        log.info(
            _("The user %s exported the data of selected companies")
            % self.request.identity.name
        )
        return response

    @view_config(
        route_name="user_selected_projects",
        renderer="user_selected_projects.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_selected_projects",
        renderer="project_more.mako",
        permission="view",
    )
    def selected_projects(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        sort_criteria = dict(SORT_CRITERIA_PROJECTS)
        sort_criteria["name"] = self.request.translate("Project")
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        q = {}

        allowed_sorts = {
            "name",
            "city",
            "subdivision",
            "country",
            "created_at",
            "updated_at",
        }
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = (
            select(Project)
            .join(selected_projects)
            .filter(user.id == selected_projects.c.user_id)
        )

        if status == "in_progress":
            stmt = stmt.filter(Project.deadline > now)
            q["status"] = status
        elif status == "completed":
            stmt = stmt.filter(Project.deadline < now)
            q["status"] = status

        if color:
            stmt = stmt.filter(Project.color == color)
            q["color"] = color

        if country:
            stmt = stmt.filter(Project.country == country)
            q["country"] = country

        if subdivision:
            stmt = stmt.filter(Project.subdivision.in_(subdivision))
            q["subdivision"] = list(subdivision)

        if stage:
            stmt = stmt.filter(Project.stage == stage)
            q["stage"] = stage

        if delivery_method:
            stmt = stmt.filter(Project.delivery_method == delivery_method)
            q["delivery_method"] = delivery_method

        if _order == "asc":
            stmt = stmt.order_by(sort_column(Project, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(sort_column(Project, _sort).desc())

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_projects
            )

        q["sort"] = _sort
        q["order"] = _order

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more_selected_projects",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = ProjectFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "counter": counter,
            "form": form,
        }

    @view_config(
        route_name="user_json_selected_projects",
        renderer="json",
        permission="view",
    )
    def json_selected_projects(self):
        user = self.request.context.user
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        now = datetime.datetime.now()

        stmt = (
            select(Project)
            .join(selected_projects)
            .filter(user.id == selected_projects.c.user_id)
        )

        if status == "in_progress":
            stmt = stmt.filter(Project.deadline > now)

        elif status == "completed":
            stmt = stmt.filter(Project.deadline < now)

        if color:
            stmt = stmt.filter(Project.color == color)

        if country:
            stmt = stmt.filter(Project.country == country)

        if subdivision:
            stmt = stmt.filter(Project.subdivision.in_(subdivision))

        if stage:
            stmt = stmt.filter(Project.stage == stage)

        if delivery_method:
            stmt = stmt.filter(Project.delivery_method == delivery_method)

        projects = self.request.dbsession.execute(stmt).scalars()

        res = [
            {
                "id": project.id,
                "name": project.name,
                "street": project.street,
                "city": project.city,
                "country": project.country,
                "latitude": project.latitude,
                "longitude": project.longitude,
                "color": project.color,
                "url": self.request.route_url(
                    "project_view", project_id=project.id, slug=project.slug
                ),
            }
            for project in projects
        ]
        return res

    @view_config(
        route_name="user_map_selected_projects",
        renderer="user_map_selected_projects.mako",
        permission="view",
    )
    def map_selected_projects(self):
        user = self.request.context.user
        stage = self.request.params.get("stage", None)
        status = self.request.params.get("status", None)
        delivery_method = self.request.params.get("delivery_method", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()
        q = {}

        allowed_sorts = {
            "name",
            "city",
            "subdivision",
            "country",
            "created_at",
            "updated_at",
        }
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = (
            select(Project)
            .join(selected_projects)
            .filter(user.id == selected_projects.c.user_id)
        )

        if status == "in_progress":
            stmt = stmt.filter(Project.deadline > now)
            q["status"] = status
        elif status == "completed":
            stmt = stmt.filter(Project.deadline < now)
            q["status"] = status

        if color:
            stmt = stmt.filter(Project.color == color)
            q["color"] = color

        if country:
            stmt = stmt.filter(Project.country == country)
            q["country"] = country

        if subdivision:
            stmt = stmt.filter(Project.subdivision.in_(subdivision))
            q["subdivision"] = list(subdivision)

        if stage:
            stmt = stmt.filter(Project.stage == stage)
            q["stage"] = stage

        if delivery_method:
            stmt = stmt.filter(Project.delivery_method == delivery_method)
            q["delivery_method"] = delivery_method

        if _order == "asc":
            stmt = stmt.order_by(sort_column(Project, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(sort_column(Project, _sort).desc())

        q["sort"] = _sort
        q["order"] = _order

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        url = self.request.route_url(
            "user_json_selected_projects", username=user.name, _query=q
        )
        return {"user": user, "url": url, "q": q, "counter": counter}

    @view_config(
        route_name="user_export_selected_projects",
        permission="view",
    )
    def export_selected_projects(self):
        _ = self.request.translate
        user = self.request.context.user
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")

        allowed_sorts = {
            "name",
            "city",
            "subdivision",
            "country",
            "created_at",
            "updated_at",
        }
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = (
            select(Project)
            .join(selected_projects)
            .filter(user.id == selected_projects.c.user_id)
        )

        if _order == "asc":
            stmt = stmt.order_by(sort_column(Project, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(sort_column(Project, _sort).desc())

        projects = self.request.dbsession.execute(stmt).scalars().all()
        rows, row_colors = self._project_export_rows(projects)

        header_row = self._project_export_header()
        response = response_xlsx(rows, header_row, row_colors=row_colors)
        log.info(
            _("The user %s exported the data of selected projects")
            % self.request.identity.name
        )
        return response

    @view_config(
        route_name="user_selected_tags",
        renderer="user_selected_tags.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_selected_tags",
        renderer="tag_more.mako",
        permission="view",
    )
    def selected_tags(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        category = self.request.params.get("category", "")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA)
        sort_criteria["name"] = self.request.translate("Tag")
        order_criteria = dict(ORDER_CRITERIA)
        categories = dict(CATEGORIES)
        q = {}

        allowed_sorts = set(sort_criteria)
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        q["sort"] = _sort
        q["order"] = _order

        stmt = (
            select(Tag).join(selected_tags).filter(user.id == selected_tags.c.user_id)
        )

        if category in {"companies", "projects"}:
            stmt, category = self._filter_tags_by_category(stmt, category, q=q)

        if _order == "asc":
            stmt = stmt.order_by(sort_column(Tag, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(sort_column(Tag, _sort).desc())

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_tags
            )

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.subquery())
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more_selected_tags",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "categories": categories,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
        }

    @view_config(
        route_name="user_export_selected_tags",
        permission="view",
    )
    def export_selected_tags(self):
        _ = self.request.translate
        user = self.request.context.user
        category = self.request.params.get("category", "companies")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")

        allowed_sorts = {"name", "created_at", "updated_at"}
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = (
            select(Tag).join(selected_tags).filter(user.id == selected_tags.c.user_id)
        )

        stmt, category = self._filter_tags_by_category(stmt, category)

        if _order == "asc":
            stmt = stmt.order_by(sort_column(Tag, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(sort_column(Tag, _sort).desc())

        tags = self.request.dbsession.execute(stmt).scalars().all()
        rows, row_colors = self._tag_export_rows(tags, category=category)

        header_row = self._tag_export_header(category=category)
        response = response_xlsx(rows, header_row, row_colors=row_colors)
        log.info(
            _("The user %s exported the data of selected tags")
            % self.request.identity.name
        )
        return response

    def _selected_related_contacts(self, scope, more_route):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        name = self.request.params.get("name", None)
        role = self.request.params.get("role", None)
        phone = self.request.params.get("phone", None)
        email = self.request.params.get("email", None)
        subdivision = self.request.params.getall("subdivision")
        country = self.request.params.get("country", None)
        color = self.request.params.get("color", None)
        requested_category = self.request.params.get("category", "")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA_CONTACTS)
        order_criteria = dict(ORDER_CRITERIA)
        q = {}

        allowed_sorts = set(sort_criteria)
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        q["sort"] = _sort
        q["order"] = _order

        if scope == "companies":
            category = requested_category
            effective_category = category or "companies"
            stmt = (
                select(Contact)
                .join(Company, Contact.company_id == Company.id)
                .join(selected_companies, selected_companies.c.company_id == Company.id)
                .filter(selected_companies.c.user_id == user.id)
            )
            if category == "projects":
                stmt = stmt.filter(false())
        elif scope == "projects":
            category = requested_category
            effective_category = category or "projects"
            stmt = (
                select(Contact)
                .join(Project, Contact.project_id == Project.id)
                .join(selected_projects, selected_projects.c.project_id == Project.id)
                .filter(selected_projects.c.user_id == user.id)
            )
            if category == "companies":
                stmt = stmt.filter(false())
        else:
            category = requested_category
            effective_category = category
            selected_tag_ids = (
                select(selected_tags.c.tag_id)
                .where(selected_tags.c.user_id == user.id)
                .scalar_subquery()
            )
            stmt = select(Contact).distinct().filter(
                or_(
                    Contact.company.has(Company.tags.any(Tag.id.in_(selected_tag_ids))),
                    Contact.project.has(Project.tags.any(Tag.id.in_(selected_tag_ids))),
                )
            )

        if category:
            q["category"] = category

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

        if effective_category == "companies":
            stmt = stmt.filter(Contact.company)
            if country:
                stmt = stmt.filter(Contact.company.has(Company.country == country))
                q["country"] = country
            if subdivision:
                stmt = stmt.filter(Contact.company.has(Company.subdivision.in_(subdivision)))
                q["subdivision"] = list(subdivision)
        elif effective_category == "projects":
            stmt = stmt.filter(Contact.project)
            if country:
                stmt = stmt.filter(Contact.project.has(Project.country == country))
                q["country"] = country
            if subdivision:
                stmt = stmt.filter(Contact.project.has(Project.subdivision.in_(subdivision)))
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

        if _sort in {"country", "subdivision"}:
            company_relation_sort = (
                select(getattr(Company, _sort))
                .where(Company.id == Contact.company_id)
                .scalar_subquery()
            )
            project_relation_sort = (
                select(getattr(Project, _sort))
                .where(Project.id == Contact.project_id)
                .scalar_subquery()
            )
            if effective_category == "projects":
                relation_sort = polish_sort_expression(project_relation_sort)
                if _order == "asc":
                    stmt = stmt.order_by(relation_sort.asc(), Contact.id)
                elif _order == "desc":
                    stmt = stmt.order_by(relation_sort.desc(), Contact.id)
            elif effective_category == "companies":
                relation_sort = polish_sort_expression(company_relation_sort)
                if _order == "asc":
                    stmt = stmt.order_by(relation_sort.asc(), Contact.id)
                elif _order == "desc":
                    stmt = stmt.order_by(relation_sort.desc(), Contact.id)
            else:
                relation_sort = polish_sort_expression(
                    func.coalesce(project_relation_sort, company_relation_sort)
                )
                if _order == "asc":
                    stmt = stmt.order_by(relation_sort.asc(), Contact.id)
                elif _order == "desc":
                    stmt = stmt.order_by(relation_sort.desc(), Contact.id)
        else:
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Contact, _sort).asc(), Contact.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Contact, _sort).desc(), Contact.id)

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_contacts
            )

        obj = Filter(**q)
        form = ContactFilterForm(self.request.GET, obj, request=self.request)

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.subquery())
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            more_route,
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "form": form,
        }

    @view_config(
        route_name="user_selected_companies_contacts",
        renderer="user_selected_related_contacts.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_selected_companies_contacts",
        renderer="contact_more.mako",
        permission="view",
    )
    def selected_companies_contacts(self):
        response = self._selected_related_contacts(
            scope="companies", more_route="user_more_selected_companies_contacts"
        )
        if isinstance(response, dict):
            response["heading"] = self.request.translate(
                _("Contacts assigned to selected companies")
            )
            response["switch_url"] = self.request.route_url(
                "user_selected_companies", username=response["user"].name
            )
            response["switch_icon"] = "buildings"
        return response

    @view_config(
        route_name="user_selected_projects_contacts",
        renderer="user_selected_related_contacts.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_selected_projects_contacts",
        renderer="contact_more.mako",
        permission="view",
    )
    def selected_projects_contacts(self):
        response = self._selected_related_contacts(
            scope="projects", more_route="user_more_selected_projects_contacts"
        )
        if isinstance(response, dict):
            response["heading"] = self.request.translate(
                _("Contacts assigned to selected projects")
            )
            response["switch_url"] = self.request.route_url(
                "user_selected_projects", username=response["user"].name
            )
            response["switch_icon"] = "briefcase"
        return response

    @view_config(
        route_name="user_selected_tags_contacts",
        renderer="user_selected_related_contacts.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_selected_tags_contacts",
        renderer="contact_more.mako",
        permission="view",
    )
    def selected_tags_contacts(self):
        response = self._selected_related_contacts(
            scope="tags", more_route="user_more_selected_tags_contacts"
        )
        if isinstance(response, dict):
            response["heading"] = self.request.translate(
                _("Contacts assigned to selected tags")
            )
            response["switch_url"] = self.request.route_url(
                "user_selected_tags", username=response["user"].name
            )
            response["switch_icon"] = "tags"
        return response

    @view_config(
        route_name="user_selected_contacts",
        renderer="user_selected_contacts.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_selected_contacts",
        renderer="contact_more.mako",
        permission="view",
    )
    def selected_contacts(self):
        user = self.request.context.user
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
        q = {}

        allowed_sorts = set(sort_criteria)
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        q["sort"] = _sort
        q["order"] = _order

        stmt = (
            select(Contact)
            .join(selected_contacts)
            .filter(user.id == selected_contacts.c.user_id)
        )

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

        if _sort in {"country", "subdivision"}:
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
                    stmt = stmt.order_by(func.lower(relation_sort).asc(), Contact.id)
                elif _order == "desc":
                    stmt = stmt.order_by(func.lower(relation_sort).desc(), Contact.id)
        else:
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Contact, _sort).asc(), Contact.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Contact, _sort).desc(), Contact.id)

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_contacts
            )

        q["sort"] = _sort
        q["order"] = _order

        obj = Filter(**q)
        form = ContactFilterForm(self.request.GET, obj, request=self.request)

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "user_more_selected_contacts",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "form": form,
        }

    @view_config(
        route_name="user_export_selected_contacts",
        permission="view",
    )
    def export_selected_contacts(self):
        _ = self.request.translate
        user = self.request.context.user
        name = self.request.params.get("name", None)
        role = self.request.params.get("role", None)
        phone = self.request.params.get("phone", None)
        email = self.request.params.get("email", None)
        subdivision = self.request.params.getall("subdivision")
        country = self.request.params.get("country", None)
        color = self.request.params.get("color", None)
        _category = self.request.params.get("category", "companies")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")

        allowed_sorts = {
            "name",
            "role",
            "country",
            "subdivision",
            "color",
            "created_at",
            "updated_at",
        }
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = (
            select(Contact)
            .join(selected_contacts)
            .filter(user.id == selected_contacts.c.user_id)
        )

        if name:
            stmt = stmt.filter(contains_ci(Contact.name, name))

        if role:
            stmt = stmt.filter(contains_ci(Contact.role, role))

        if phone:
            stmt = stmt.filter(contains_ci(Contact.phone, phone))

        if email:
            stmt = stmt.filter(contains_ci(Contact.email, email))

        if _category == "companies":
            stmt = stmt.filter(Contact.company)
            if country:
                stmt = stmt.filter(Contact.company.has(Company.country == country))
            if subdivision:
                stmt = stmt.filter(
                    Contact.company.has(Company.subdivision.in_(subdivision))
                )
        elif _category == "projects":
            stmt = stmt.filter(Contact.project)
            if country:
                stmt = stmt.filter(Contact.project.has(Project.country == country))
            if subdivision:
                stmt = stmt.filter(
                    Contact.project.has(Project.subdivision.in_(subdivision))
                )

        if color:
            stmt = stmt.filter(Contact.color == color)

        category = "projects" if _category == "projects" else "companies"

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
        else:
            if _order == "asc":
                stmt = stmt.order_by(sort_column(Contact, _sort).asc(), Contact.id)
            elif _order == "desc":
                stmt = stmt.order_by(sort_column(Contact, _sort).desc(), Contact.id)

        contacts = self.request.dbsession.execute(stmt).scalars().all()
        rows, row_colors = self._selected_contacts_export_rows(contacts, category)
        header_row = self._selected_contacts_export_header(category)
        response = response_xlsx(rows, header_row, row_colors=row_colors)

        log.info(
            _("The user %s exported the data of selected contacts")
            % self.request.identity.name
        )
        return response

    @view_config(
        route_name="user_delete_selected_companies",
        request_method="POST",
        permission="edit",
    )
    def delete_selected_companies(self):
        _ = self.request.translate
        user = self.request.context.user
        companies_to_delete = list(user.selected_companies)

        for company in companies_to_delete:
            contact_ids = (
                self.request.dbsession.execute(
                    select(Contact.id).where(Contact.company_id == company.id)
                )
                .scalars()
                .all()
            )
            stmt_1 = delete(companies_stars).where(
                companies_stars.c.company_id == company.id
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
            self.request.dbsession.execute(stmt_1)
            self.request.dbsession.delete(company)

        self.request.session.flash(_("success:Selected companies deleted"))
        log.info(
            _("The user %s deleted selected companies") % self.request.identity.name
        )
        next_url = self.request.route_url("user_selected_companies", username=user.name)
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="user_delete_selected_projects",
        request_method="POST",
        permission="edit",
    )
    def delete_selected_projects(self):
        _ = self.request.translate
        user = self.request.context.user
        projects_to_delete = list(user.selected_projects)

        for project in projects_to_delete:
            contact_ids = (
                self.request.dbsession.execute(
                    select(Contact.id).where(Contact.project_id == project.id)
                )
                .scalars()
                .all()
            )
            stmt_1 = delete(projects_stars).where(
                projects_stars.c.project_id == project.id
            )
            clear_selected_rows(
                self.request,
                selected_contacts,
                selected_contacts.c.contact_id,
                contact_ids,
            )
            clear_selected_rows(
                self.request,
                selected_projects,
                selected_projects.c.project_id,
                [project.id],
            )
            self.request.dbsession.execute(stmt_1)
            self.request.dbsession.delete(project)

        self.request.session.flash(_("success:Selected projects deleted"))
        log.info(
            _("The user %s deleted selected projects") % self.request.identity.name
        )
        next_url = self.request.route_url("user_selected_projects", username=user.name)
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="user_delete_selected_contacts",
        request_method="POST",
        permission="edit",
    )
    def delete_selected_contacts(self):
        _ = self.request.translate
        user = self.request.context.user
        selected_ids = [contact.id for contact in user.selected_contacts]

        clear_selected_rows(
            self.request,
            selected_contacts,
            selected_contacts.c.contact_id,
            selected_ids,
        )

        if selected_ids:
            stmt = delete(Contact).where(Contact.id.in_(selected_ids))
            self.request.dbsession.execute(stmt)
        self.request.session.flash(_("success:Selected contacts deleted"))
        log.info(
            _("The user %s deleted selected contacts") % self.request.identity.name
        )
        next_url = self.request.route_url("user_selected_contacts", username=user.name)
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="user_delete_selected_tags",
        request_method="POST",
        permission="edit",
    )
    def delete_selected_tags(self):
        _ = self.request.translate
        user = self.request.context.user
        selected_ids = [tag.id for tag in user.selected_tags]

        clear_selected_rows(
            self.request,
            selected_tags,
            selected_tags.c.tag_id,
            selected_ids,
        )

        if selected_ids:
            self.request.dbsession.execute(
                delete(companies_tags).where(companies_tags.c.tag_id.in_(selected_ids))
            )
            self.request.dbsession.execute(
                delete(projects_tags).where(projects_tags.c.tag_id.in_(selected_ids))
            )
            self.request.dbsession.execute(delete(Tag).where(Tag.id.in_(selected_ids)))
        self.request.session.flash(_("success:Selected tags deleted"))
        log.info(_("The user %s deleted selected tags") % self.request.identity.name)
        next_url = self.request.route_url("user_selected_tags", username=user.name)
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="user_merge_selected_tags",
        request_method="POST",
        permission="edit",
    )
    def merge_selected_tags(self):
        _ = self.request.translate
        user = self.request.context.user
        new_name = self.request.params.get("merge_tag_name", None)

        if not new_name or not user.selected_tags:
            self.request.session.flash(
                _("warning:Please provide a name and select tags")
            )
            next_url = self.request.route_url("user_selected_tags", username=user.name)
            response = self.request.response
            response.headers = {"HX-Redirect": next_url}
            response.status_code = 303
            return response

        # Get all selected tag IDs and collect companies/projects BEFORE deletions
        selected_ids = [tag.id for tag in user.selected_tags]
        companies_to_add = set()
        projects_to_add = set()

        for tag in user.selected_tags:
            companies_to_add.update(tag.companies)
            projects_to_add.update(tag.projects)

        # Check if a tag with the new name already exists (created by this user)
        existing_tag = self.request.dbsession.execute(
            select(Tag).filter(Tag.name == new_name, Tag.creator_id == user.id)
        ).scalar()

        if existing_tag:
            # Merge into existing tag with that name
            target_tag = existing_tag
            # Remove target tag from selected IDs so we don't delete its associations
            ids_to_delete = [
                tag_id for tag_id in selected_ids if tag_id != target_tag.id
            ]
        else:
            # Create a new tag with the given name
            target_tag = Tag(name=new_name)
            target_tag.created_by = user
            self.request.dbsession.add(target_tag)
            self.request.dbsession.flush()  # Ensure it gets an ID
            ids_to_delete = selected_ids

        # Remove associations from selected_tags table for tags to be deleted
        if ids_to_delete:
            stmt = delete(selected_tags).where(
                selected_tags.c.tag_id.in_(ids_to_delete)
            )
            self.request.dbsession.execute(stmt)

            # Remove associations from companies_tags and projects_tags for tags to be deleted
            stmt = delete(companies_tags).where(
                companies_tags.c.tag_id.in_(ids_to_delete)
            )
            self.request.dbsession.execute(stmt)

            stmt = delete(projects_tags).where(
                projects_tags.c.tag_id.in_(ids_to_delete)
            )
            self.request.dbsession.execute(stmt)

        # Add companies and projects to target tag (if not already there)
        for company in companies_to_add:
            if company not in target_tag.companies:
                target_tag.companies.append(company)

        for project in projects_to_add:
            if project not in target_tag.projects:
                target_tag.projects.append(project)

        # Delete the old tags (but not the target tag)
        for tag in user.selected_tags:
            if tag.id != target_tag.id:
                stmt = delete(Tag).where(Tag.id == tag.id)
                self.request.dbsession.execute(stmt)

        # Clear selection
        user.selected_tags = []

        self.request.session.flash(_("success:Selected tags merged"))
        log.info(
            _("The user %s merged selected tags to '%s'")
            % (self.request.identity.name, new_name)
        )
        next_url = self.request.route_url("user_selected_tags", username=user.name)
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="user_companies_stars",
        renderer="user_companies_stars.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_companies_stars",
        renderer="company_more.mako",
        permission="view",
    )
    def companies_stars(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA_EXT)
        sort_criteria["name"] = self.request.translate("Company")
        order_criteria = dict(ORDER_CRITERIA)
        colors = dict(COLORS)
        q = {}

        allowed_sorts = set(sort_criteria)
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = (
            select(Company)
            .join(companies_stars)
            .filter(user.id == companies_stars.c.user_id)
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
            stmt = stmt.order_by(sort_column(Company, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(sort_column(Company, _sort).desc())

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_companies
            )

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        next_page = self.request.route_url(
            "user_more_companies_stars",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = CompanyFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "colors": colors,
            "counter": counter,
            "form": form,
        }

    @view_config(
        route_name="user_export_companies_stars",
        permission="view",
    )
    def export_companies_stars(self):
        _ = self.request.translate
        user = self.request.context.user
        color = self.request.params.get("color", None)
        subdivision = self.request.params.getall("subdivision")
        country = self.request.params.get("country", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")

        allowed_sorts = {
            "name",
            "city",
            "subdivision",
            "country",
            "created_at",
            "updated_at",
        }
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = (
            select(Company)
            .join(companies_stars)
            .filter(user.id == companies_stars.c.user_id)
        )

        if color:
            stmt = stmt.filter(Company.color == color)

        if subdivision:
            stmt = stmt.filter(Company.subdivision.in_(subdivision))

        if country:
            stmt = stmt.filter(Company.country == country)

        if _order == "asc":
            stmt = stmt.order_by(sort_column(Company, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(sort_column(Company, _sort).desc())

        companies = self.request.dbsession.execute(stmt).scalars().all()
        rows, row_colors = self._company_export_rows(companies)

        header_row = self._company_export_header()
        response = response_xlsx(rows, header_row, row_colors=row_colors)
        log.info(
            _("The user %s exported the data of companies with a star")
            % self.request.identity.name
        )
        return response

    @view_config(
        route_name="user_clear_companies_stars",
        request_method="POST",
        permission="view",
    )
    def clear_companies_stars(self):
        _ = self.request.translate
        user = self.request.context.user
        user.companies_stars = []
        log.info(
            _("The user %s cleared companies with a star") % self.request.identity.name
        )
        next_url = self.request.route_url("user_companies_stars", username=user.name)
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="user_json_companies_stars",
        renderer="json",
        permission="view",
    )
    def json_companies_stars(self):
        user = self.request.context.user
        stmt = (
            select(Company)
            .join(companies_stars)
            .filter(user.id == companies_stars.c.user_id)
        )
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
        route_name="user_map_companies_stars",
        renderer="user_map_companies_stars.mako",
        permission="view",
    )
    def map_companies_stars(self):
        user = self.request.context.user
        stmt = (
            select(Company)
            .join(companies_stars)
            .filter(user.id == companies_stars.c.user_id)
        )
        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()
        url = self.request.route_url("user_json_companies_stars", username=user.name)
        return {"user": user, "url": url, "counter": counter}

    @view_config(
        route_name="user_projects_stars",
        renderer="user_projects_stars.mako",
        permission="view",
    )
    @view_config(
        route_name="user_more_projects_stars",
        renderer="project_more.mako",
        permission="view",
    )
    def projects_stars(self):
        user = self.request.context.user
        page = int(self.request.params.get("page", 1))
        status = self.request.params.get("status", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA_EXT)
        sort_criteria["name"] = self.request.translate("Project")
        order_criteria = dict(ORDER_CRITERIA)
        project_delivery_methods = dict(PROJECT_DELIVERY_METHODS)
        now = datetime.datetime.now()
        q = {}

        allowed_sorts = set(sort_criteria)
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = (
            select(Project)
            .join(projects_stars)
            .filter(user.id == projects_stars.c.user_id)
        )

        if status == "in_progress":
            stmt = stmt.filter(Project.deadline > now)
            q["status"] = status
        elif status == "completed":
            stmt = stmt.filter(Project.deadline < now)
            q["status"] = status

        if color:
            stmt = stmt.filter(Project.color == color)
            q["color"] = color

        if country:
            stmt = stmt.filter(Project.country == country)
            q["country"] = country

        if subdivision:
            stmt = stmt.filter(Project.subdivision.in_(subdivision))
            q["subdivision"] = list(subdivision)

        q["sort"] = _sort
        q["order"] = _order

        if _order == "asc":
            stmt = stmt.order_by(sort_column(Project, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(sort_column(Project, _sort).desc())

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_projects
            )

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        next_page = self.request.route_url(
            "user_more_projects_stars",
            username=user.name,
            _query={
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = ProjectFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "user": user,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "project_delivery_methods": project_delivery_methods,
            "form": form,
        }

    @view_config(
        route_name="user_export_projects_stars",
        permission="view",
    )
    def export_projects_stars(self):
        _ = self.request.translate
        user = self.request.context.user
        status = self.request.params.get("status", None)
        color = self.request.params.get("color", None)
        country = self.request.params.get("country", None)
        subdivision = self.request.params.getall("subdivision")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        now = datetime.datetime.now()

        allowed_sorts = {
            "name",
            "city",
            "subdivision",
            "country",
            "created_at",
            "updated_at",
        }
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = (
            select(Project)
            .join(projects_stars)
            .filter(user.id == projects_stars.c.user_id)
        )

        if status == "in_progress":
            stmt = stmt.filter(Project.deadline > now)
        elif status == "completed":
            stmt = stmt.filter(Project.deadline < now)

        if color:
            stmt = stmt.filter(Project.color == color)

        if country:
            stmt = stmt.filter(Project.country == country)

        if subdivision:
            stmt = stmt.filter(Project.subdivision.in_(subdivision))

        if _order == "asc":
            stmt = stmt.order_by(sort_column(Project, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(sort_column(Project, _sort).desc())

        projects = self.request.dbsession.execute(stmt).scalars().all()
        rows, row_colors = self._project_export_rows(projects)

        header_row = self._project_export_header()
        response = response_xlsx(rows, header_row, row_colors=row_colors)
        log.info(
            _("The user %s exported the data of projects with a star")
            % self.request.identity.name
        )
        return response

    @view_config(
        route_name="user_clear_projects_stars",
        request_method="POST",
        permission="view",
    )
    def clear_projects_stars(self):
        _ = self.request.translate
        user = self.request.context.user
        user.projects_stars = []
        log.info(
            _("The user %s cleared projects with a star") % self.request.identity.name
        )
        next_url = self.request.route_url("user_projects_stars", username=user.name)
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="user_json_projects_stars",
        renderer="json",
        permission="view",
    )
    def json_projects_stars(self):
        user = self.request.context.user
        stmt = (
            select(Project)
            .join(projects_stars)
            .filter(user.id == projects_stars.c.user_id)
        )
        projects = self.request.dbsession.execute(stmt).scalars()
        res = [
            {
                "id": project.id,
                "name": project.name,
                "street": project.street,
                "city": project.city,
                "country": project.country,
                "latitude": project.latitude,
                "longitude": project.longitude,
                "color": project.color,
                "url": self.request.route_url(
                    "project_view", project_id=project.id, slug=project.slug
                ),
            }
            for project in projects
        ]
        return res

    @view_config(
        route_name="user_map_projects_stars",
        renderer="user_map_projects_stars.mako",
        permission="view",
    )
    def map_projects_stars(self):
        user = self.request.context.user
        stmt = (
            select(Project)
            .join(projects_stars)
            .filter(user.id == projects_stars.c.user_id)
        )
        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()
        url = self.request.route_url("user_json_projects_stars", username=user.name)
        return {"user": user, "url": url, "counter": counter}

    @view_config(
        route_name="user_count_companies",
        renderer="json",
        permission="view",
    )
    def count_companies(self):
        user = self.request.context.user
        return user.count_companies

    @view_config(
        route_name="user_count_projects",
        renderer="json",
        permission="view",
    )
    def count_projects(self):
        user = self.request.context.user
        return user.count_projects

    @view_config(
        route_name="user_count_tags",
        renderer="json",
        permission="view",
    )
    def count_tags(self):
        user = self.request.context.user
        return user.count_tags

    @view_config(
        route_name="user_count_contacts",
        renderer="json",
        permission="view",
    )
    def count_contacts(self):
        user = self.request.context.user
        return user.count_contacts

    @view_config(
        route_name="user_count_comments",
        renderer="json",
        permission="view",
    )
    def count_comments(self):
        user = self.request.context.user
        return user.count_comments

    @view_config(
        route_name="user_map_companies",
        renderer="user_map_companies.mako",
        permission="view",
    )
    def map_companies(self):
        user = self.request.context.user
        url = self.request.route_url("user_json_companies", username=user.name)
        return {"user": user, "url": url, "user_pills": self.pills(user)}

    @view_config(
        route_name="user_map_projects",
        renderer="user_map_projects.mako",
        permission="view",
    )
    def map_projects(self):
        user = self.request.context.user
        url = self.request.route_url("user_json_projects", username=user.name)
        return {"user": user, "url": url, "user_pills": self.pills(user)}

    @view_config(
        route_name="user_json_companies",
        renderer="json",
        permission="view",
    )
    def json_companies(self):
        user = self.request.context.user

        # Bounding box parameters for lazy loading
        north = self.request.params.get("north", None)
        south = self.request.params.get("south", None)
        east = self.request.params.get("east", None)
        west = self.request.params.get("west", None)

        stmt = select(Company).filter(Company.created_by == user)

        # Filter by bounding box if provided
        if north and south and east and west:
            try:
                north = float(north)
                south = float(south)
                east = float(east)
                west = float(west)
                stmt = stmt.filter(Company.latitude.between(south, north))
                stmt = stmt.filter(Company.longitude.between(west, east))
            except (ValueError, TypeError):
                pass  # Invalid coordinates, ignore filtering

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
        route_name="user_json_projects",
        renderer="json",
        permission="view",
    )
    def json_projects(self):
        user = self.request.context.user

        # Bounding box parameters for lazy loading
        north = self.request.params.get("north", None)
        south = self.request.params.get("south", None)
        east = self.request.params.get("east", None)
        west = self.request.params.get("west", None)

        stmt = select(Project).filter(Project.created_by == user)

        # Filter by bounding box if provided
        if north and south and east and west:
            try:
                north = float(north)
                south = float(south)
                east = float(east)
                west = float(west)
                stmt = stmt.filter(Project.latitude.between(south, north))
                stmt = stmt.filter(Project.longitude.between(west, east))
            except (ValueError, TypeError):
                pass  # Invalid coordinates, ignore filtering

        projects = self.request.dbsession.execute(stmt).scalars()
        res = [
            {
                "id": project.id,
                "name": project.name,
                "street": project.street,
                "city": project.city,
                "country": project.country,
                "latitude": project.latitude,
                "longitude": project.longitude,
                "color": project.color,
                "url": self.request.route_url(
                    "project_view", project_id=project.id, slug=project.slug
                ),
            }
            for project in projects
        ]
        return res

