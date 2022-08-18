import logging
from pyramid.csrf import new_csrf_token
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPSeeOther
from sqlalchemy import select
from ..models import Comment
from ..forms import CommentForm
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
        stmt = select(Comment).order_by(Comment.created_at.desc())
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url("comment_more", _query={"page": page + 1})
        return {"paginator": paginator, "next_page": next_page}

    @view_config(
        route_name="comment_add", renderer="comment_form.mako", permission="edit"
    )
    def add(self):
        company = self.request.context.company
        form = CommentForm(self.request.POST)

        if self.request.method == "POST" and form.validate():
            new_csrf_token(self.request)
            comment = Comment(comment=form.comment.data)
            comment.created_by = self.request.identity
            company.comments.append(comment)
            self.request.dbsession.add(comment)
            self.request.session.flash("success:Dodano do bazy danych")
            log.info(
                f"Użytkownik {self.request.identity.name} dodał komentarz dot. firmy {company.name}"
            )
            return HTTPSeeOther(
                location=self.request.route_url(
                    "company_comments",
                    company_id=company.id,
                    slug=company.slug,
                )
            )
        return dict(
            heading=f"Komentarz dot. firmy {company.name}",
            form=form,
        )

    @view_config(route_name="comment_delete", request_method="GET", permission="edit")
    def delete(self):
        comment = self.request.context.comment
        query = self.request.params["from"]
        company = comment.company
        self.request.dbsession.delete(comment)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(
            f"Użytkownik {self.request.identity.name} usunął komentarz dot. firmy {company.name}"
        )
        if query == "company":
            return HTTPFound(
                location=self.request.route_url(
                    "company_comments",
                    company_id=company.id,
                    slug=company.slug,
                )
            )
        elif query == "user":
            return HTTPFound(
                location=self.request.route_url(
                    "user_view", username=self.request.identity.name
                )
            )
        else:
            return HTTPFound(location=self.request.route_url("home"))

    @view_config(
        route_name="comment_search",
        renderer="comment_search.mako",
        permission="view",
    )
    def search(self):
        return {}

    @view_config(
        route_name="comment_results",
        renderer="comment_all.mako",
        permission="view",
    )
    @view_config(
        route_name="comment_results_more",
        renderer="comment_more.mako",
        permission="view",
    )
    def results(self):
        comment = self.request.params.get("comment")
        page = int(self.request.params.get("page", 1))
        stmt = (
            select(Comment)
            .filter(Comment.comment.ilike("%" + comment + "%"))
            .order_by(Comment.id.desc())
        )
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "comment_results_more",
            _query={"comment": comment, "page": page + 1},
        )
        return {"paginator": paginator, "next_page": next_page}
