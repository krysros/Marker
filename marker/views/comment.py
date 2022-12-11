import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
from sqlalchemy import (
    select,
    func,
)
from ..models import Comment
from ..forms import CommentSearchForm
from ..paginator import get_paginator


log = logging.getLogger(__name__)


class CommentView(object):
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
        stmt = select(Comment)

        if comment:
            stmt = stmt.filter(Comment.comment.ilike("%" + comment + "%"))

        stmt = stmt.order_by(Comment.created_at.desc())

        counter = self.request.dbsession.execute(
            select(func.count()).select_from(stmt)
        ).scalar()

        search_query = {"comment": comment}

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "comment_more", _query={**search_query, "page": page + 1}
        )
        return {
            "search_query": search_query,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
        }

    @view_config(
        route_name="comment_add",
        renderer="comment.mako",
        request_method="POST",
        permission="edit",
    )
    def add(self):
        company = self.request.context.company
        comment = None
        comment_text = self.request.POST.get("comment")
        if comment_text:
            comment = Comment(comment=comment_text)
            comment.created_by = self.request.identity
            company.comments.append(comment)
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "commentCompanyEvent"}
        return {"comment": comment}

    @view_config(
        route_name="comment_delete",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def delete(self):
        comment = self.request.context.comment
        self.request.dbsession.delete(comment)
        log.info(f"Użytkownik {self.request.identity.name} usunął komentarz")
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": "commentCompanyEvent"}
        return ""

    @view_config(
        route_name="comment_search",
        renderer="comment_form.mako",
        permission="view",
    )
    def search(self):
        form = CommentSearchForm(self.request.POST)
        if self.request.method == "POST" and form.validate():
            return HTTPSeeOther(
                location=self.request.route_url(
                    "comment_all", _query={"comment": form.comment.data}
                )
            )
        return {"heading": "Znajdź komentarz", "form": form}
