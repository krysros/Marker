"""Prices view — project activity prices (unit prices per m²)."""
import logging
from collections import namedtuple
from decimal import Decimal, InvalidOperation

from pyramid.view import view_config
from sqlalchemy import case as sa_case, func, select

from ..forms.select import COMPANY_ROLES, OBJECT_CATEGORIES, ORDER_CRITERIA, STAGES, select_currencies
from ..models import Activity, Company, Project
from ..utils.export import make_export_response
from ..utils.paginator import get_paginator
from . import apply_order, polish_sort_expression

log = logging.getLogger(__name__)

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
        value_net_from = self.request.params.get("value_net_from", "")
        value_net_to = self.request.params.get("value_net_to", "")
        value_gross_from = self.request.params.get("value_gross_from", "")
        value_gross_to = self.request.params.get("value_gross_to", "")
        unit_price_net_from = self.request.params.get("unit_price_net_from", "")
        unit_price_net_to = self.request.params.get("unit_price_net_to", "")
        unit_price_gross_from = self.request.params.get("unit_price_gross_from", "")
        unit_price_gross_to = self.request.params.get("unit_price_gross_to", "")
        object_category = self.request.params.get("object_category", "")
        _sort = self.request.params.get("sort", "project_name")
        _order = self.request.params.get("order", "asc")
        if _order not in {"asc", "desc"}:
            _order = "asc"

        stages = dict(STAGES)
        roles = dict(COMPANY_ROLES)
        object_categories = dict(OBJECT_CATEGORIES)
        stage_choices = [(v, l) for v, l in STAGES if v]
        role_choices = [(v, l) for v, l in COMPANY_ROLES if v]
        currency_choices = select_currencies()
        sort_criteria = {
            "project_name": _("Project"),
            "object_category": _("Object category"),
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

        if value_net_from:
            try:
                stmt = stmt.filter(Activity.value_net >= Decimal(value_net_from))
                q["value_net_from"] = value_net_from
            except (InvalidOperation, ValueError):
                pass

        if value_net_to:
            try:
                stmt = stmt.filter(Activity.value_net <= Decimal(value_net_to))
                q["value_net_to"] = value_net_to
            except (InvalidOperation, ValueError):
                pass

        if value_gross_from:
            try:
                stmt = stmt.filter(Activity.value_gross >= Decimal(value_gross_from))
                q["value_gross_from"] = value_gross_from
            except (InvalidOperation, ValueError):
                pass

        if value_gross_to:
            try:
                stmt = stmt.filter(Activity.value_gross <= Decimal(value_gross_to))
                q["value_gross_to"] = value_gross_to
            except (InvalidOperation, ValueError):
                pass

        if unit_price_net_from:
            try:
                stmt = stmt.filter(
                    Project.usable_area > 0,
                    Activity.value_net / Project.usable_area >= Decimal(unit_price_net_from),
                )
                q["unit_price_net_from"] = unit_price_net_from
            except (InvalidOperation, ValueError):
                pass

        if unit_price_net_to:
            try:
                stmt = stmt.filter(
                    Project.usable_area > 0,
                    Activity.value_net / Project.usable_area <= Decimal(unit_price_net_to),
                )
                q["unit_price_net_to"] = unit_price_net_to
            except (InvalidOperation, ValueError):
                pass

        if unit_price_gross_from:
            try:
                stmt = stmt.filter(
                    Project.usable_area > 0,
                    Activity.value_gross / Project.usable_area >= Decimal(unit_price_gross_from),
                )
                q["unit_price_gross_from"] = unit_price_gross_from
            except (InvalidOperation, ValueError):
                pass

        if unit_price_gross_to:
            try:
                stmt = stmt.filter(
                    Project.usable_area > 0,
                    Activity.value_gross / Project.usable_area <= Decimal(unit_price_gross_to),
                )
                q["unit_price_gross_to"] = unit_price_gross_to
            except (InvalidOperation, ValueError):
                pass

        if object_category:
            stmt = stmt.filter(Project.object_category == object_category)
            q["object_category"] = object_category

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
            "object_category": Project.object_category,
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
            "object_categories": object_categories,
            "stage_choices": stage_choices,
            "role_choices": role_choices,
            "currency_choices": currency_choices,
            "sort_criteria": sort_criteria,
            "order_criteria": order_criteria,
            "next_page": next_page,
        }

    def _build_filtered_stmt(self, stage, role, currency,
                             value_net_from, value_net_to,
                             value_gross_from, value_gross_to,
                             unit_price_net_from, unit_price_net_to,
                             unit_price_gross_from, unit_price_gross_to):
        stmt = (
            select(Activity, Project, Company)
            .join(Project, Activity.project_id == Project.id)
            .join(Company, Activity.company_id == Company.id)
        )
        if stage:
            stmt = stmt.filter(Activity.stage == stage)
        if role:
            stmt = stmt.filter(Activity.role == role)
        if currency:
            stmt = stmt.filter(Activity.currency == currency)
        for col, val in (
            (Activity.value_net.__ge__, value_net_from),
            (Activity.value_net.__le__, value_net_to),
            (Activity.value_gross.__ge__, value_gross_from),
            (Activity.value_gross.__le__, value_gross_to),
        ):
            if val:
                try:
                    stmt = stmt.filter(col(Decimal(val)))
                except (InvalidOperation, ValueError):
                    pass
        for expr_fn, val in (
            (lambda d: Activity.value_net / Project.usable_area >= d, unit_price_net_from),
            (lambda d: Activity.value_net / Project.usable_area <= d, unit_price_net_to),
            (lambda d: Activity.value_gross / Project.usable_area >= d, unit_price_gross_from),
            (lambda d: Activity.value_gross / Project.usable_area <= d, unit_price_gross_to),
        ):
            if val:
                try:
                    stmt = stmt.filter(Project.usable_area > 0, expr_fn(Decimal(val)))
                except (InvalidOperation, ValueError):
                    pass
        return stmt

    @view_config(route_name="prices_export", permission="view")
    def export(self):
        _ = self.request.translate
        stage = self.request.params.get("stage", "")
        role = self.request.params.get("role", "")
        currency = self.request.params.get("currency", "")
        value_net_from = self.request.params.get("value_net_from", "")
        value_net_to = self.request.params.get("value_net_to", "")
        value_gross_from = self.request.params.get("value_gross_from", "")
        value_gross_to = self.request.params.get("value_gross_to", "")
        unit_price_net_from = self.request.params.get("unit_price_net_from", "")
        unit_price_net_to = self.request.params.get("unit_price_net_to", "")
        unit_price_gross_from = self.request.params.get("unit_price_gross_from", "")
        unit_price_gross_to = self.request.params.get("unit_price_gross_to", "")
        _sort = self.request.params.get("sort", "project_name")
        _order = self.request.params.get("order", "asc")
        if _order not in {"asc", "desc"}:
            _order = "asc"

        stmt = self._build_filtered_stmt(
            stage, role, currency,
            value_net_from, value_net_to,
            value_gross_from, value_gross_to,
            unit_price_net_from, unit_price_net_to,
            unit_price_gross_from, unit_price_gross_to,
        )

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

        stages_map = dict(STAGES)
        roles_map = dict(COMPANY_ROLES)
        object_categories_map = dict(OBJECT_CATEGORIES)
        raw_rows = self.request.dbsession.execute(stmt).all()

        rows = []
        for activity, project, company in raw_rows:
            unit_price_net = None
            unit_price_gross = None
            if project.usable_area and project.usable_area > 0:
                if activity.value_net is not None:
                    unit_price_net = round(float(activity.value_net / project.usable_area), 2)
                if activity.value_gross is not None:
                    unit_price_gross = round(float(activity.value_gross / project.usable_area), 2)
            rows.append((
                project.name,
                object_categories_map.get(project.object_category, project.object_category or ""),
                company.name,
                str(_(stages_map.get(activity.stage, activity.stage or ""))),
                str(_(roles_map.get(activity.role, activity.role or ""))),
                activity.currency or "",
                float(activity.value_net) if activity.value_net is not None else None,
                float(activity.value_gross) if activity.value_gross is not None else None,
                unit_price_net,
                unit_price_gross,
            ))

        header_row = [
            _("Project"),
            _("Object category"),
            _("Company"),
            _("Stage"),
            _("Role"),
            _("Currency"),
            _("Net value"),
            _("Gross value"),
            _("Net / m\u00b2"),
            _("Gross / m\u00b2"),
        ]
        response = make_export_response(self.request, rows, header_row)
        log.info(_("The user %s exported prices data") % self.request.identity.name)
        return response
