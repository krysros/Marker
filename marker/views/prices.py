"""Prices view — project activity prices (unit prices per m²)."""
from collections import namedtuple

from pyramid.view import view_config
from sqlalchemy import case as sa_case, func, select

from ..forms.select import COMPANY_ROLES, ORDER_CRITERIA, STAGES, select_currencies
from ..models import Activity, Company, Project
from ..utils.paginator import get_paginator
from . import apply_order, polish_sort_expression

PriceRow = namedtuple(
    "PriceRow",
    ["activity", "project", "company", "unit_price_net", "unit_price_gross"],
)


class PricesView:
    def __init__(self, request):
        self.request = request

    @view_config(
        route_name="prices_all",
        renderer="prices_all.mako",
        permission="view",
    )
    @view_config(
        route_name="prices_more",
        renderer="prices_more.mako",
        permission="view",
    )
    def all(self):
        _ = self.request.translate
        page = int(self.request.params.get("page", 1))
        stage = self.request.params.get("stage", "")
        role = self.request.params.get("role", "")
        currency = self.request.params.get("currency", "")
        _sort = self.request.params.get("sort", "project_name")
        _order = self.request.params.get("order", "asc")
        if _order not in {"asc", "desc"}:
            _order = "asc"

        stages = dict(STAGES)
        roles = dict(COMPANY_ROLES)
        stage_choices = [(v, l) for v, l in STAGES if v]
        role_choices = [(v, l) for v, l in COMPANY_ROLES if v]
        currency_choices = select_currencies()
        sort_criteria = {
            "project_name": _("Project"),
            "company_name": _("Company"),
            "stage": _("Stage"),
            "role": _("Role"),
            "currency": _("Currency"),
            "value_net": _("Net value"),
            "value_gross": _("Gross value"),
            "unit_price_net": _("Net / m\u00b2"),
            "unit_price_gross": _("Gross / m\u00b2"),
        }
        order_criteria = dict(ORDER_CRITERIA)

        q = {}

        stmt = (
            select(Activity, Project, Company)
            .join(Project, Activity.project_id == Project.id)
            .join(Company, Activity.company_id == Company.id)
        )

        if stage:
            stmt = stmt.filter(Activity.stage == stage)
            q["stage"] = stage

        if role:
            stmt = stmt.filter(Activity.role == role)
            q["role"] = role

        if currency:
            stmt = stmt.filter(Activity.currency == currency)
            q["currency"] = currency

        q["sort"] = _sort
        q["order"] = _order

        stage_case = sa_case(
            *[(Activity.stage == v, str(_(l))) for v, l in STAGES if v],
            else_=Activity.stage,
        ).collate("POLISH_CI")
        role_case = sa_case(
            *[(Activity.role == v, str(_(l))) for v, l in COMPANY_ROLES if v],
            else_=Activity.role,
        ).collate("POLISH_CI")

        _sort_map = {
            "project_name": polish_sort_expression(Project.name),
            "company_name": polish_sort_expression(Company.name),
            "stage": stage_case,
            "role": role_case,
            "currency": Activity.currency,
            "value_net": Activity.value_net,
            "value_gross": Activity.value_gross,
            "unit_price_net": Activity.value_net / Project.usable_area,
            "unit_price_gross": Activity.value_gross / Project.usable_area,
        }
        sort_col = _sort_map.get(_sort, polish_sort_expression(Project.name))
        stmt = apply_order(stmt, sort_col, _order, Activity.project_id, Activity.company_id)

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        ).scalar()

        raw_rows = self.request.dbsession.execute(
            get_paginator(stmt, page=page)
        ).all()

        paginator = []
        for activity, project, company in raw_rows:
            unit_price_net = None
            unit_price_gross = None
            if project.usable_area and project.usable_area > 0:
                if activity.value_net is not None:
                    unit_price_net = round(activity.value_net / project.usable_area, 2)
                if activity.value_gross is not None:
                    unit_price_gross = round(
                        activity.value_gross / project.usable_area, 2
                    )
            paginator.append(
                PriceRow(
                    activity=activity,
                    project=project,
                    company=company,
                    unit_price_net=unit_price_net,
                    unit_price_gross=unit_price_gross,
                )
            )

        next_page = self.request.route_url(
            "prices_more",
            _query={**q, "page": page + 1},
        )

        return {
            "heading": _("Project Prices"),
            "paginator": paginator,
            "counter": counter,
            "q": q,
            "stages": stages,
            "roles": roles,
            "stage_choices": stage_choices,
            "role_choices": role_choices,
            "currency_choices": currency_choices,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "next_page": next_page,
        }
