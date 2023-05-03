import logging

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy import func, select

from ..forms import CommentSearchForm, CommentFilterForm
from ..forms.select import COMMENTS_FILTER, ORDER_CRITERIA
from ..models import Comment
from ..utils.dropdown import Dd, Dropdown
from ..utils.paginator import get_paginator

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
        _filter = self.request.params.get("filter", None)
        _sort = self.request.params.get("sort", "created_at")
        _order = self.request.params.get("order", "desc")
        # comments_filter = dict(COMMENTS_FILTER)
        order_criteria = dict(ORDER_CRITERIA)
        search_query = {}
        filter_form = CommentFilterForm()
        stmt = select(Comment)

        if comment:
            stmt = stmt.filter(Comment.comment.ilike("%" + comment + "%"))
            search_query["comment"] = comment

        if _filter == "companies":
            stmt = stmt.filter(Comment.company)
        elif _filter == "projects":
            stmt = stmt.filter(Comment.project)

        if _order == "asc":
            stmt = stmt.order_by(Comment.created_at.asc())
        elif _order == "desc":
            stmt = stmt.order_by(Comment.created_at.desc())

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "comment_more",
            _query={
                **search_query,
                "filter": _filter,
                "sort": _sort,
                "order": _order,
                "page": page + 1,
            },
        )

        dd_order = Dropdown(
            self.request, order_criteria, Dd.ORDER, search_query, _filter, _sort, _order
        )

        return {
            "search_query": search_query,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "dd_order": dd_order,
            "filter_form": filter_form,
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
        route_name="company_add_comment",
        renderer="comment.mako",
        request_method="POST",
        permission="edit",
    )
    def company_add_comment(self):
        _ = self.request.translate
        company = self.request.context.company
        comment = None
        comment_text = self.request.POST.get("comment")
        if comment_text:
            comment = Comment(comment=comment_text)
            comment.created_by = self.request.identity
            company.comments.append(comment)
            log.info(_("The user %s added a comment") % self.request.identity.name)
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "commentEvent"}
        return {"comment": comment}

    @view_config(
        route_name="project_add_comment",
        renderer="comment.mako",
        request_method="POST",
        permission="edit",
    )
    def project_add_comment(self):
        _ = self.request.translate
        project = self.request.context.project
        comment = None
        comment_text = self.request.POST.get("comment")
        if comment_text:
            comment = Comment(comment=comment_text)
            comment.created_by = self.request.identity
            project.comments.append(comment)
            log.info(_("The user %s added a comment") % self.request.identity.name)
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "commentEvent"}
        return {"comment": comment}

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
