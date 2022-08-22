import logging
from pyramid.view import view_config

from sqlalchemy import select
from ..models import Person
from ..paginator import get_paginator
from ..forms.select import (
    DROPDOWN_SORT,
    DROPDOWN_ORDER,
)

log = logging.getLogger(__name__)


class PersonView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="person_all", renderer="person_all.mako", permission="view")
    @view_config(
        route_name="person_more",
        renderer="person_more.mako",
        permission="view",
    )
    def all(self):
        page = int(self.request.params.get("page", 1))
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        dropdown_sort = dict(DROPDOWN_SORT)
        dropdown_order = dict(DROPDOWN_ORDER)
        stmt = select(Person)

        if order == "asc":
            stmt = stmt.order_by(getattr(Person, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Person, sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "person_more",
            _query={"sort": sort, "order": order, "page": page + 1},
        )

        return dict(
            sort=sort,
            order=order,
            dropdown_sort=dropdown_sort,
            dropdown_order=dropdown_order,
            paginator=paginator,
            next_page=next_page,
        )