import logging

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import func, select

from ..forms import CommentFilterForm, CommentSearchForm
from ..forms.select import CATEGORIES, ORDER_CRITERIA
from ..models import Comment
from ..utils.paginator import get_paginator
from . import Filter, contains_ci

log = logging.getLogger(__name__)


class CommentView:
    def __init__(self, request):
        self.request = request

    @view_config(
        route_name="comment_all",
        renderer="comment_all.mako",
        permission="view",
    )
    @view_config(
        route_name="comment_more",
        renderer="comment_more.mako",
        permission="view",
    )
    def all(self):
        page = int(self.request.params.get("page", 1))
        comment = self.request.params.get("comment", None)
        category = self.request.params.get("category", "")
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        order_criteria = dict(ORDER_CRITERIA)
        categories = dict(CATEGORIES)
        q = {}
        stmt = select(Comment)

        if comment:
            stmt = stmt.filter(contains_ci(Comment.comment, comment))
            q["comment"] = comment

        if category == "companies":
            stmt = stmt.filter(Comment.company_id.is_not(None))
            q["category"] = category
        elif category == "projects":
            stmt = stmt.filter(Comment.project_id.is_not(None))
            q["category"] = category

        q["sort"] = _sort
        q["order"] = _order

        if _order == "asc":
            stmt = stmt.order_by(Comment.created_at.asc())
        elif _order == "desc":
            stmt = stmt.order_by(Comment.created_at.desc())

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "comment_more",
            _query={
                **q,
                "page": page + 1,
            },
        )

        obj = Filter(**q)
        form = CommentFilterForm(self.request.GET, obj, request=self.request)

        return {
            "q": q,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "order_criteria": order_criteria,
            "categories": categories,
            "form": form,
        }

    @view_config(
        route_name="comment_count",
        renderer="json",
        permission="view",
    )
    def count(self):
        return self.request.dbsession.execute(
            select(func.count()).select_from(Comment)
        ).scalar()

    @view_config(
        route_name="comment_delete",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def delete(self):
        _ = self.request.translate
        comment = self.request.context.comment
        self.request.dbsession.delete(comment)
        log.info(_("The user %s deleted the comment") % self.request.identity.name)
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": "commentEvent"}
        return ""

    @view_config(
        route_name="comment_search",
        renderer="comment_form.mako",
        permission="view",
    )
    def search(self):
        _ = self.request.translate
        form = CommentSearchForm(self.request.POST)
        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "comment_all", _query={"comment": form.comment.data}
                )
            )
        return {"heading": _("Find a comment"), "form": form}
