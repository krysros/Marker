import logging

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import func, select

from ..forms import TagForm, TagSearchForm
from ..forms.select import (
    COLORS,
    ORDER_CRITERIA,
    SORT_CRITERIA,
    SORT_CRITERIA_COMPANIES,
    SORT_CRITERIA_PROJECTS,
)
from ..models import Company, Project, Tag, recommended, watched
from ..utils.dropdown import Dd, Dropdown
from ..utils.export import response_xlsx
from ..utils.paginator import get_paginator

log = logging.getLogger(__name__)


class TagView:
    def __init__(self, request):
        self.request = request

    def pills(self, tag):
        _ = self.request.translate
        return [
            {
                "title": _("Tag"),
                "icon": "tag",
                "url": self.request.route_url("tag_view", tag_id=tag.id, slug=tag.slug),
                "count": None,
            },
            {
                "title": _("Companies"),
                "icon": "buildings",
                "url": self.request.route_url(
                    "tag_companies", tag_id=tag.id, slug=tag.slug
                ),
                "count": self.request.route_url(
                    "tag_count_companies", tag_id=tag.id, slug=tag.slug
                ),
                "event": "tagEvent",
                "init_value": tag.count_companies,
            },
            {
                "title": _("Projects"),
                "icon": "briefcase",
                "url": self.request.route_url(
                    "tag_projects", tag_id=tag.id, slug=tag.slug
                ),
                "count": self.request.route_url(
                    "tag_count_projects", tag_id=tag.id, slug=tag.slug
                ),
                "event": "tagEvent",
                "init_value": tag.count_projects,
            },
        ]

    @view_config(route_name="tag_all", renderer="tag_all.mako", permission="view")
    @view_config(
        route_name="tag_more",
        renderer="tag_more.mako",
        permission="view",
    )
    def all(self):
        page = int(self.request.params.get("page", 1))
        name = self.request.params.get("name", None)
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        sort_criteria = dict(SORT_CRITERIA)
        order_criteria = dict(ORDER_CRITERIA)
        search_query = {}
        stmt = select(Tag)

        if name:
            stmt = stmt.filter(Tag.name.ilike("%" + name + "%"))
            search_query["name"] = name

        if _order == "asc":
            stmt = stmt.order_by(getattr(Tag, _sort).asc())
        elif _order == "desc":
            stmt = stmt.order_by(getattr(Tag, _sort).desc())

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "tag_more",
            _query={
                **search_query,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
                "page": page + 1,
            },
        )

        dd_sort = Dropdown(
            self.request, sort_criteria, Dd.SORT, search_query, _filter, _sort, _order
        )
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, search_query, _filter, _sort, _order
        )

        return {
            "search_query": search_query,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
        }

    @view_config(
        route_name="tag_count",
        renderer="json",
        permission="view",
    )
    def count(self):
        return self.request.dbsession.execute(
            select(func.count()).select_from(select(Tag))
        ).scalar()

    @view_config(
        route_name="tag_view",
        renderer="tag_view.mako",
        permission="view",
    )
    def view(self):
        tag = self.request.context.tag
        return {"tag": tag, "title": tag.name, "tag_pills": self.pills(tag)}

    @view_config(
        route_name="tag_map_companies",
        renderer="tag_map_companies.mako",
        permission="view",
    )
    def map_companies(self):
        tag = self.request.context.tag
        url = self.request.route_url("tag_json_companies", tag_id=tag.id, slug=tag.slug)
        return {"tag": tag, "url": url, "tag_pills": self.pills(tag)}

    @view_config(
        route_name="tag_map_projects",
        renderer="tag_map_projects.mako",
        permission="view",
    )
    def map_projects(self):
        tag = self.request.context.tag
        url = self.request.route_url("tag_json_projects", tag_id=tag.id, slug=tag.slug)
        return {"tag": tag, "url": url, "tag_pills": self.pills(tag)}

    @view_config(
        route_name="tag_json_companies",
        renderer="json",
        permission="view",
    )
    def json_companies(self):
        tag = self.request.context.tag
        stmt = select(Company).filter(Company.tags.any(name=tag.name))
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
        route_name="tag_json_projects",
        renderer="json",
        permission="view",
    )
    def json_projects(self):
        tag = self.request.context.tag
        stmt = select(Project).filter(Project.tags.any(name=tag.name))
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
        route_name="tag_companies",
        renderer="tag_companies.mako",
        permission="view",
    )
    @view_config(
        route_name="tag_more_companies",
        renderer="company_more.mako",
        permission="view",
    )
    def companies(self):
        tag = self.request.context.tag
        page = int(self.request.params.get("page", 1))
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "name")
        _order = self.request.params.get("order", "asc")
        colors = dict(COLORS)
        sort_criteria = dict(SORT_CRITERIA_COMPANIES)
        order_criteria = dict(ORDER_CRITERIA)
        search_query = {}
        stmt = select(Company)

        if _sort == "recommended":
            if _order == "asc":
                stmt = (
                    stmt.filter(Company.tags.any(name=tag.name))
                    .join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).asc(), Company.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.filter(Company.tags.any(name=tag.name))
                    .join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).desc(), Company.id)
                )
        else:
            if _order == "asc":
                stmt = stmt.filter(Company.tags.any(name=tag.name)).order_by(
                    getattr(Company, _sort).asc(), Company.id
                )
            elif _order == "desc":
                stmt = stmt.filter(Company.tags.any(name=tag.name)).order_by(
                    getattr(Company, _sort).desc(), Company.id
                )

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "tag_more_companies",
            tag_id=tag.id,
            slug=tag.slug,
            _query={
                **search_query,
                "page": page + 1,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
            },
        )

        dd_sort = Dropdown(
            self.request, sort_criteria, Dd.SORT, search_query, _filter, _sort, _order
        )
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, search_query, _filter, _sort, _order
        )

        return {
            "search_query": search_query,
            "tag": tag,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "colors": colors,
            "paginator": paginator,
            "next_page": next_page,
            "title": tag.name,
            "tag_pills": self.pills(tag),
        }

    @view_config(route_name="tag_export_companies", permission="view")
    def export_companies(self):
        _ = self.request.translate
        tag = self.request.context.tag
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "name")
        _order = self.request.params.get("order", "asc")
        stmt = select(
            Company.name,
            Company.street,
            Company.postcode,
            Company.city,
            Company.subdivision,
            Company.country,
            Company.link,
            Company.NIP,
            Company.REGON,
            Company.KRS,
        )

        if _sort == "recommended":
            if _order == "asc":
                stmt = (
                    stmt.filter(Company.tags.any(name=tag.name))
                    .join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).asc(), Company.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.filter(Company.tags.any(name=tag.name))
                    .join(recommended)
                    .group_by(Company)
                    .order_by(func.count(recommended.c.company_id).desc(), Company.id)
                )
        else:
            if _order == "asc":
                stmt = stmt.filter(Company.tags.any(name=tag.name)).order_by(
                    getattr(Company, _sort).asc(), Company.id
                )
            elif _order == "desc":
                stmt = stmt.filter(Company.tags.any(name=tag.name)).order_by(
                    getattr(Company, _sort).desc(), Company.id
                )

        if _filter:
            stmt = stmt.filter(Company.color == _filter)

        companies = self.request.dbsession.execute(stmt).all()
        header_row = [
            _("Name"),
            _("Street"),
            _("Post code"),
            _("City"),
            _("Subdivision"),
            _("Country"),
            _("Link"),
            _("NIP"),
            _("REGON"),
            _("KRS"),
        ]
        response = response_xlsx(companies, header_row)
        log.info(_("The user %s exported company data") % self.request.identity.name)
        return response

    @view_config(
        route_name="tag_count_companies",
        renderer="json",
        permission="view",
    )
    def count_companies(self):
        tag = self.request.context.tag
        return tag.count_companies

    @view_config(
        route_name="tag_projects",
        renderer="tag_projects.mako",
        permission="view",
    )
    @view_config(
        route_name="tag_more_projects",
        renderer="project_more.mako",
        permission="view",
    )
    def projects(self):
        tag = self.request.context.tag
        page = int(self.request.params.get("page", 1))
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "name")
        _order = self.request.params.get("order", "asc")
        colors = dict(COLORS)
        sort_criteria = dict(SORT_CRITERIA_PROJECTS)
        order_criteria = dict(ORDER_CRITERIA)
        search_query = {}
        stmt = select(Project)

        if _sort == "watched":
            if _order == "asc":
                stmt = (
                    stmt.filter(Project.tags.any(name=tag.name))
                    .join(watched)
                    .group_by(Project)
                    .order_by(func.count(watched.c.project_id).asc(), Project.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.filter(Project.tags.any(name=tag.name))
                    .join(watched)
                    .group_by(Project)
                    .order_by(func.count(watched.c.project_id).desc(), Project.id)
                )
        else:
            if _order == "asc":
                stmt = stmt.filter(Project.tags.any(name=tag.name)).order_by(
                    getattr(Project, _sort).asc(), Project.id
                )
            elif _order == "desc":
                stmt = stmt.filter(Project.tags.any(name=tag.name)).order_by(
                    getattr(Project, _sort).desc(), Project.id
                )

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "tag_more_projects",
            tag_id=tag.id,
            slug=tag.slug,
            _query={
                **search_query,
                "page": page + 1,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
            },
        )

        dd_sort = Dropdown(
            self.request, sort_criteria, Dd.SORT, search_query, _filter, _sort, _order
        )
        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, search_query, _filter, _sort, _order
        )

        return {
            "search_query": search_query,
            "tag": tag,
            "dd_sort": dd_sort,
            "dd_order": dd_order,
            "colors": colors,
            "paginator": paginator,
            "next_page": next_page,
            "title": tag.name,
            "tag_pills": self.pills(tag),
        }

    @view_config(route_name="tag_export_projects", permission="view")
    def export_projects(self):
        _ = self.request.translate
        tag = self.request.context.tag
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "name")
        _order = self.request.params.get("order", "asc")
        stmt = select(
            Project.name,
            Project.street,
            Project.postcode,
            Project.city,
            Project.subdivision,
            Project.country,
            Project.link,
            Project.deadline,
            Project.stage,
            Project.delivery_method,
        )

        if _sort == "watched":
            if _order == "asc":
                stmt = (
                    stmt.filter(Project.tags.any(name=tag.name))
                    .join(watched)
                    .group_by(Project)
                    .order_by(func.count(watched.c.project_id).asc(), Project.id)
                )
            elif _order == "desc":
                stmt = (
                    stmt.filter(Project.tags.any(name=tag.name))
                    .join(watched)
                    .group_by(Project)
                    .order_by(func.count(watched.c.project_id).desc(), Project.id)
                )
        else:
            if _order == "asc":
                stmt = stmt.filter(Project.tags.any(name=tag.name)).order_by(
                    getattr(Project, _sort).asc(), Project.id
                )
            elif _order == "desc":
                stmt = stmt.filter(Project.tags.any(name=tag.name)).order_by(
                    getattr(Project, _sort).desc(), Project.id
                )

        if _filter:
            stmt = stmt.filter(Project.color == _filter)

        projects = self.request.dbsession.execute(stmt).all()
        header_row = [
            _("Name"),
            _("Street"),
            _("Post code"),
            _("City"),
            _("Subdivision"),
            _("Country"),
            _("Link"),
            _("Deadline"),
            _("Stage"),
            _("Project delivery method"),
        ]
        response = response_xlsx(projects, header_row)
        log.info(_("The user %s exported project data") % self.request.identity.name)
        return response

    @view_config(
        route_name="tag_count_projects",
        renderer="json",
        permission="view",
    )
    def count_projects(self):
        tag = self.request.context.tag
        return tag.count_projects

    @view_config(route_name="tag_add", renderer="tag_form.mako", permission="edit")
    def add(self):
        _ = self.request.translate
        form = TagForm(self.request.POST, request=self.request)

        if self.request.method == "POST" and form.validate():
            tag = Tag(form.name.data)
            tag.created_by = self.request.identity
            self.request.dbsession.add(tag)
            self.request.session.flash(_("success:Added to the database"))
            log.info(_("The user %s has added a tag") % self.request.identity.name)
            next_url = self.request.route_url("tag_all")
            return HTTPSeeOther(location=next_url)

        return {"heading": _("Add tag"), "form": form}

    @view_config(route_name="tag_edit", renderer="tag_form.mako", permission="edit")
    def edit(self):
        _ = self.request.translate
        tag = self.request.context.tag
        form = TagForm(self.request.POST, tag, request=self.request)

        if self.request.method == "POST" and form.validate():
            form.populate_obj(tag)
            tag.updated_by = self.request.identity
            self.request.session.flash(_("success:Changes have been saved"))
            log.info(
                _("The user %s changed the name of the tag")
                % self.request.identity.name
            )
            next_url = self.request.route_url("tag_all")
            return HTTPSeeOther(location=next_url)
        return {"heading": _("Edit tag"), "form": form}

    @view_config(route_name="tag_delete", request_method="POST", permission="edit")
    def delete(self):
        _ = self.request.translate
        tag = self.request.context.tag
        self.request.dbsession.delete(tag)
        self.request.session.flash(_("success:Removed from the database"))
        log.info(_("The user %s removed the tag") % self.request.identity.name)
        next_url = self.request.route_url("home")
        response = self.request.response
        response.headers = {"HX-Redirect": next_url}
        response.status_code = 303
        return response

    @view_config(
        route_name="tag_del_row",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def tag_del_row(self):
        _ = self.request.translate
        tag = self.request.context.tag
        self.request.dbsession.delete(tag)
        log.info(_("The user %s removed the tag") % self.request.identity.name)
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": "tagEvent"}
        return ""

    @view_config(
        route_name="tag_check",
        request_method="POST",
        renderer="json",
        permission="view",
    )
    def check(self):
        tag = self.request.context.tag
        selected_tags = self.request.identity.selected_tags

        if tag in selected_tags:
            selected_tags.remove(tag)
            return {"checked": False}
        else:
            selected_tags.append(tag)
            return {"checked": True}

    @view_config(
        route_name="tag_select",
        renderer="tag_datalist.mako",
        request_method="GET",
    )
    def select(self):
        name = self.request.params.get("name")
        tags = []
        if name:
            tags = self.request.dbsession.execute(
                select(Tag).filter(Tag.name.ilike("%" + name + "%"))
            ).scalars()
        return {"tags": tags}

    @view_config(
        route_name="tag_search",
        renderer="tag_form.mako",
        permission="view",
    )
    def search(self):
        _ = self.request.translate
        form = TagSearchForm(self.request.POST)
        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "tag_all", _query={"name": form.name.data}
                )
            )
        return {"heading": _("Find the tag"), "form": form}
