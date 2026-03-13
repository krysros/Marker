from pyramid.view import view_config
from sqlalchemy import func, select

from ..forms import ContractorFilterForm
from ..forms.select import COMPANY_ROLES, ORDER_CRITERIA, SORT_CRITERIA_COMPANIES
from ..models import Activity, Comment, Company, Tag, companies_stars, companies_tags
from ..utils.paginator import get_paginator
from . import (
    Filter,
    handle_bulk_selection,
    is_bulk_select_request,
    normalize_ci_expression,
    normalize_ci_value,
    sort_column,
)


class ContractorView:
    def __init__(self, request):
        self.request = request

    def _normalized_tags(self):
        seen = set()
        tags = []
        for value in self.request.params.getall("tag"):
            name = value.strip()
            normalized = normalize_ci_value(name)
            if name and normalized not in seen:
                seen.add(normalized)
                tags.append(name)
        return tags

    def _available_tags(self):
        names = self.request.dbsession.execute(
            select(Tag.name)
            .join(companies_tags, companies_tags.c.tag_id == Tag.id)
            .join(Activity, Activity.company_id == companies_tags.c.company_id)
            .distinct()
        ).scalars()

        tags_by_normalized = {}
        for name in names:
            if not name:
                continue
            normalized = normalize_ci_value(name)
            tags_by_normalized.setdefault(normalized, name)

        return sorted(tags_by_normalized.values(), key=normalize_ci_value)

    @view_config(
        route_name="contractor_all",
        renderer="contractor_all.mako",
        permission="view",
    )
    @view_config(
        route_name="contractor_more",
        renderer="company_more.mako",
        permission="view",
    )
    def all(self):
        _ = self.request.translate
        page = int(self.request.params.get("page", 1))
        tags = self._normalized_tags()
        roles = [value for value in self.request.params.getall("role") if value]
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")

        sort_criteria = dict(SORT_CRITERIA_COMPANIES)
        order_criteria = dict(ORDER_CRITERIA)
        role_criteria = dict(COMPANY_ROLES)
        available_tags = self._available_tags()
        available_roles = [(value, label) for value, label in COMPANY_ROLES if value]

        q = {}

        allowed_sorts = set(sort_criteria)
        if _sort not in allowed_sorts:
            _sort = "created_at"

        if _order not in {"asc", "desc"}:
            _order = "desc"

        stmt = select(Company).join(Activity, Activity.company_id == Company.id).group_by(Company.id)

        if tags:
            normalized_tags = [normalize_ci_value(tag) for tag in tags]

            company_tag_exists = (
                select(1)
                .select_from(companies_tags.join(Tag, Tag.id == companies_tags.c.tag_id))
                .where(
                    companies_tags.c.company_id == Company.id,
                    normalize_ci_expression(Tag.name).in_(normalized_tags),
                )
                .exists()
            )

            stmt = stmt.where(company_tag_exists)
            q["tag"] = tags

        if roles:
            stmt = stmt.where(Activity.role.in_(roles))
            q["role"] = list(roles)

        q["sort"] = _sort
        q["order"] = _order

        if _sort == "stars":
            stars_count_expr = (
                select(func.count())
                .select_from(companies_stars)
                .where(companies_stars.c.company_id == Company.id)
                .scalar_subquery()
            )
            if _order == "asc":
                stmt = stmt.order_by(
                    stars_count_expr.asc(),
                    Company.id,
                )
            else:
                stmt = stmt.order_by(
                    stars_count_expr.desc(),
                    Company.id,
                )
        elif _sort == "comments":
            comments_count_expr = (
                select(func.count())
                .select_from(Comment)
                .where(Comment.company_id == Company.id)
                .scalar_subquery()
            )
            if _order == "asc":
                stmt = stmt.order_by(
                    comments_count_expr.asc(),
                    Company.id,
                )
            else:
                stmt = stmt.order_by(
                    comments_count_expr.desc(),
                    Company.id,
                )
        else:
            sort_expr = sort_column(Company, _sort)
            if _order == "asc":
                stmt = stmt.order_by(
                    sort_expr.asc(),
                    Company.id,
                )
            else:
                stmt = stmt.order_by(
                    sort_expr.desc(),
                    Company.id,
                )

        if is_bulk_select_request(self.request):
            return handle_bulk_selection(
                self.request, stmt, self.request.identity.selected_companies
            )

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        obj = Filter(role=q.get("role", []))
        form = ContractorFilterForm(self.request.GET, obj, request=self.request)

        next_page = self.request.route_url(
            "contractor_more",
            _query={
                **q,
                "page": page + 1,
            },
        )

        return {
            "q": q,
            "counter": counter,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "available_tags": available_tags,
            "available_roles": available_roles,
            "role_criteria": role_criteria,
            "form": form,
            "paginator": paginator,
            "next_page": next_page,
        }
