import logging
from marker.views.select import VOIVODESHIPS
import colander
import deform
from deform.schema import CSRFSchema
from pyramid.view import view_config

from ..models import (
    Document,
    Person,
)

from marker.export import export_to_docx


log = logging.getLogger(__name__)


class EnvelopeView(object):
    def __init__(self, request):
        self.request = request

    def _get_docs(self, typ):
        documents = (
            self.request.dbsession.query(Document)
            .filter(Document.typ == typ)
            .all()
        )
        docs = []
        for document in documents:
            docs.append((document.id, document.filename))
        return docs

    def _get_document_filename(self, id):
        document = self.request.dbsession.get(Document, id)
        return document.filename

    @staticmethod
    def _get_people(company):
        people = []
        for person in company.people:
            people.append((person.id, person.fullname))
        return people

    def _get_person(self, id):
        return self.request.dbsession.get(Person, id)

    @property
    def envelope_form(self):
        class Schema(CSRFSchema):
            docx_template = colander.SchemaNode(
                colander.Integer(),
                title="Szablon dokumentu",
                widget=deform.widget.SelectWidget(values=self.docs),
            )
            addressee = colander.SchemaNode(
                colander.Integer(),
                title="Adresat",
                widget=deform.widget.SelectWidget(values=self.people),
            )

        schema = Schema().bind(request=self.request)
        submit_btn = deform.form.Button(name="submit", title="Pobierz")
        form = deform.Form(schema, buttons=(submit_btn,))
        return form

    @view_config(
        route_name="envelope", renderer="form.mako", permission="view"
    )
    def download(self):
        company = self.request.context.company
        self.people = self._get_people(company)
        self.docs = self._get_docs("envelope")
        form = self.envelope_form
        appstruct = {}
        rendered_form = None

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                rendered_form = e.render()
            else:
                addressee = self._get_person(appstruct["addressee"])
                docx_template = self._get_document_filename(
                    appstruct["docx_template"]
                )
                fields = {"company": company, "addressee": addressee}
                response = export_to_docx(self.request, docx_template, fields)
                log.info(
                    f"Użytkownik {self.request.identity.username} wygenerował kopertę dla firmy {company.name}"
                )
                return response

        if rendered_form is None:
            rendered_form = form.render(appstruct=appstruct)
        reqts = form.get_widget_resources()

        return dict(
            heading=f"Adresowanie koperty dla firmy {company.name}",
            rendered_form=rendered_form,
            css_links=reqts["css"],
            js_links=reqts["js"],
        )
