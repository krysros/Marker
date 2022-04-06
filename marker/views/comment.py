import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import select
import deform
from deform.schema import CSRFSchema
import colander

from ..models import Comment
from ..paginator import get_paginator


log = logging.getLogger(__name__)


class CommentView(object):
    def __init__(self, request):
        self.request = request

    @property
    def comment_form(self):
        class Schema(CSRFSchema):
            comment = colander.SchemaNode(
                colander.String(),
                title="Komentarz",
            )

        schema = Schema().bind(request=self.request)
        submit_btn = deform.form.Button(name="submit", title="Dodaj")
        form = deform.Form(schema, buttons=(submit_btn,))
        form.set_widgets({"comment": deform.widget.TextAreaWidget()})
        return form

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
        stmt = select(Comment).order_by(Comment.added.desc())
        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )
        next_page = self.request.route_url(
            "comment_more", _query={"page": page + 1}
        )
        return {"paginator": paginator, "next_page": next_page}

    @view_config(
        route_name="comment_add", renderer="form.mako", permission="edit"
    )
    def add(self):
        company = self.request.context.company
        form = self.comment_form
        appstruct = {}
        rendered_form = None

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                rendered_form = e.render()
            else:
                comment = Comment(
                    comment=appstruct["comment"],
                )
                comment.added_by = self.request.identity
                company.comments.append(comment)
                self.request.dbsession.add(comment)
                self.request.session.flash("success:Dodano do bazy danych")
                log.info(
                    f"Użytkownik {self.request.identity.username} dodał komentarz dot. firmy {company.name}"
                )
                return HTTPFound(
                    location=self.request.route_url(
                        "company_comments",
                        company_id=company.id,
                        slug=company.slug,
                    )
                )

        if rendered_form is None:
            rendered_form = form.render(appstruct=appstruct)
        reqts = form.get_widget_resources()

        return dict(
            heading=f"Komentarz dot. firmy {company.name}",
            rendered_form=rendered_form,
            css_links=reqts["css"],
            js_links=reqts["js"],
        )

    @view_config(
        route_name="comment_delete", request_method="GET", permission="edit"
    )
    def delete(self):
        comment = self.request.context.comment
        query = self.request.params["from"]
        company = comment.company
        self.request.dbsession.delete(comment)
        self.request.session.flash("success:Usunięto z bazy danych")
        log.info(
            f"Użytkownik {self.request.identity.username} usunął komentarz dot. firmy {company.name}"
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
                    "user_view", username=self.request.identity.username
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
