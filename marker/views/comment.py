import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
from sqlalchemy import (
    select,
    func,
)
from ..models import (
    Comment,
    companies_comments,
    projects_comments,
)
from ..forms import CommentSearchForm
from ..forms.select import (
    COMMENTS_FILTER,
    DROPDOWN_ORDER,
)
from ..paginator import get_paginator
from ..dropdown import Dd, Dropdown

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
        filter = self.request.params.get("filter", None)
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        comments_filter = dict(COMMENTS_FILTER)
        dropdown_order = dict(DROPDOWN_ORDER)

        stmt = select(Comment)

        if comment:
            stmt = stmt.filter(Comment.comment.ilike("%" + comment + "%"))

        if filter == "C":
            stmt = stmt.join(companies_comments).filter(
                Comment.id == companies_comments.c.comment_id
            )
        elif filter == "P":
            stmt = stmt.join(projects_comments).filter(
                Comment.id == projects_comments.c.comment_id
            )

        if order == "asc":
            stmt = stmt.order_by(Comment.created_at.asc())
        elif order == "desc":
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
            "comment_more",
            _query={
                **search_query,
                "filter": filter,
                "sort": sort,
                "order": order,
                "page": page + 1,
            },
        )

        dd_filter = Dropdown(
            items=comments_filter,
            typ=Dd.FILTER,
            _filter=filter,
            _sort=sort,
            _order=order,
        )
        dd_order = Dropdown(
            items=dropdown_order, typ=Dd.ORDER, _filter=filter, _sort=sort, _order=order
        )

        return {
            "search_query": search_query,
            "paginator": paginator,
            "next_page": next_page,
            "counter": counter,
            "dd_filter": dd_filter,
            "dd_order": dd_order,
        }

    @view_config(
        route_name="comment_company",
        renderer="comment.mako",
        request_method="POST",
        permission="edit",
    )
    def add_to_company(self):
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
        route_name="comment_project",
        renderer="comment.mako",
        request_method="POST",
        permission="edit",
    )
    def add_to_project(self):
        project = self.request.context.project
        comment = None
        comment_text = self.request.POST.get("comment")
        if comment_text:
            comment = Comment(comment=comment_text)
            comment.created_by = self.request.identity
            project.comments.append(comment)
            # If you want to use the id of a newly created object
            # in the middle of a transaction, you must call dbsession.flush()
            self.request.dbsession.flush()
        self.request.response.headers = {"HX-Trigger": "commentProjectEvent"}
        return {"comment": comment}

    @view_config(
        route_name="comment_delete",
        request_method="POST",
        permission="edit",
        renderer="string",
    )
    def delete(self):
        comment = self.request.context.comment
        if comment.company:
            event = "commentCompanyEvent"
        elif comment.project:
            event = "commentProjectEvent"
        self.request.dbsession.delete(comment)
        log.info(f"Użytkownik {self.request.identity.name} usunął komentarz")
        # This request responds with empty content,
        # indicating that the row should be replaced with nothing.
        self.request.response.headers = {"HX-Trigger": event}
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
