import logging
from pathlib import Path
from pyramid.response import FileIter
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
import colander
import deform
from pyramid_storage.exceptions import FileNotAllowed
from marker.paginator import get_paginator
from ..models import Document
from .select import DOCTYPES


log = logging.getLogger(__name__)


class MemoryTmpStore(dict):
    """Instances of this class implement the
    :class:`deform.interfaces.FileUploadTempStore` interface"""

    def preview_url(self, uid):
        return None


tmpstore = MemoryTmpStore()


class DocumentView(object):
    def __init__(self, request):
        self.request = request

    @property
    def storage_base_path(self):
        return self.request.registry.settings.get("storage.base_path")

    @property
    def document_form(self):
        class Schema(colander.Schema):
            typ = colander.SchemaNode(
                colander.String(),
                title="Typ dokumentu",
                validator=colander.OneOf([x[0] for x in DOCTYPES]),
                widget=deform.widget.RadioChoiceWidget(values=DOCTYPES),
            )
            upload = colander.SchemaNode(
                deform.FileData(),
                title="Plik",
                widget=deform.widget.FileUploadWidget(tmpstore),
                description="Wybierz plik docx",
            )

        schema = Schema()
        submit_btn = deform.form.Button(name="submit", title="Prześlij")
        return deform.Form(schema, buttons=(submit_btn,))

    @view_config(
        route_name="document_all",
        renderer="document_all.mako",
        permission="view",
    )
    @view_config(
        route_name="document_more",
        renderer="document_more.mako",
        permission="view",
    )
    def all(self):
        page = int(self.request.params.get("page", 1))
        filter = self.request.params.get("filter", "all")
        sort = self.request.params.get("sort", "created_at")
        order = self.request.params.get("order", "desc")
        stmt = self.request.dbsession.query(Document)
        doctypes = dict(DOCTYPES)

        if filter in list(doctypes):
            stmt = stmt.filter(Document.typ == filter)

        if order == "asc":
            stmt = stmt.order_by(getattr(Document, sort).asc())
        elif order == "desc":
            stmt = stmt.order_by(getattr(Document, sort).desc())

        paginator = (
            self.request.dbsession.execute(get_paginator(stmt, page=page))
            .scalars()
            .all()
        )

        next_page = self.request.route_url(
            "document_more",
            _query={
                "filter": filter,
                "sort": sort,
                "order": order,
                "page": page + 1,
            },
        )
        return dict(
            filter=filter,
            sort=sort,
            order=order,
            paginator=paginator,
            next_page=next_page,
            doctypes=doctypes,
        )

    @view_config(
        route_name="document_upload", renderer="form.mako", permission="edit"
    )
    def upload(self):
        form = self.document_form
        appstruct = {}
        rendered_form = None

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                rendered_form = e.render()
            else:
                try:
                    filename = self.request.storage.save(
                        self.request.POST["upload"]
                    )
                    typ = appstruct["typ"]
                except FileNotAllowed:
                    self.request.session.flash(
                        "warning:Ten plik jest niedozwolony"
                    )
                else:
                    document = Document(filename, typ)
                    document.created_by = self.request.identity
                    self.request.dbsession.add(document)
                    self.request.session.flash("success:Dodano plik")
                    log.info(
                        f"Użytkownik {self.request.identity.username} dodał plik {filename}"
                    )
                    next_url = self.request.route_url("document_all")
                    return HTTPSeeOther(location=next_url)

        if rendered_form is None:
            rendered_form = form.render(appstruct=appstruct)

        return dict(
            heading="Dodaj dokument",
            rendered_form=rendered_form,
        )

    @view_config(
        route_name="document_download",
        request_method="POST",
        permission="view",
    )
    def download(self):
        document = self.request.context.document
        p = Path(self.storage_base_path, document.filename)
        f = open(p, "rb")
        f.seek(0)
        response = self.request.response
        response.content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        response.content_disposition = (
            f'attachment; filename="{document.filename}"'
        )
        response.app_iter = FileIter(f)
        return response

    @view_config(
        route_name="document_delete", request_method="POST", permission="edit"
    )
    def delete(self):
        document = self.request.context.document
        document_id = document.id
        document_filename = document.filename
        self.request.dbsession.delete(document)
        p = Path(self.storage_base_path, document_filename)
        try:
            p.unlink()
        except FileNotFoundError:
            pass
        self.request.session.flash("success:Usunięto dokument")
        log.info(
            f"Użytkownik {self.request.identity.username} usunął dokument {document_filename}"
        )
        next_url = self.request.route_url("document_all")
        return HTTPSeeOther(location=next_url)
