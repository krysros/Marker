import logging
import datetime
import colander
import deform
from pyramid.view import view_config
from deform.schema import CSRFSchema

from babel.numbers import format_currency
from babel.dates import (
    format_date,
    format_datetime,
)
from slownie import slownie_zl100gr
from ..models import (
    Person,
    Document,
)
from .select import (
    SETTLEMENT,
    COURTS,
    UNITS,
    RMS,
)
from ..export import export_to_docx


log = logging.getLogger(__name__)


class ContractView(object):
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

    def _get_complaint_address(self, id):
        if id == 0:
            company = self.request.context.company
            return company.email
        else:
            person = self.request.dbsession.get(Person, id)
            return person.email

    @staticmethod
    def _get_people(company):
        people = []
        for person in company.people:
            people.append((person.id, person.fullname))
        return people

    @staticmethod
    def _get_emails(company):
        emails = [(0, company.email)]
        for person in company.people:
            if person.email:
                emails.append((person.id, person.email))
        return emails

    def _get_persons(self, ids):
        return (
            self.request.dbsession.query(Person)
            .filter(Person.id.in_(ids))
            .all()
        )

    def _fmt_datetime(self, dt):
        return format_datetime(dt, format="dd.MM.YYYY", locale="pl_PL")

    def _fmt_date(self, d):
        return format_date(d, format="long", locale="pl_PL")

    def _fmt_currency(self, c):
        return format_currency(c, "PLN", locale="pl_PL")

    def _prepare_template_data(self, company, appstruct):
        courts = dict(COURTS)
        court = courts.get(company.court)
        representation = self._get_persons(appstruct["representation"])
        contacts = self._get_persons(appstruct["contacts"])
        complaint_address = self._get_complaint_address(
            appstruct["complaint_address"]
        )

        appstruct["company"] = company
        appstruct["court"] = court
        appstruct["representation"] = representation
        appstruct["contacts"] = contacts
        appstruct["complaint_address"] = complaint_address

        penalty = 0
        M_counter = 0

        for price in appstruct["contract_price"]:
            value = price["price"]
            if "M" in price["category"]:
                M_counter += 1
            price["category"] = "".join(price["category"])
            price["price"] = self._fmt_currency(value)
            price["in_words"] = slownie_zl100gr(value)
            penalty += 0.005 * float(value)

        if appstruct["lump_sum"]:
            if penalty < 1000 or not appstruct["lump_sum"]:
                appstruct["penalty"] = self._fmt_currency(1000.00)
        else:
            appstruct["penalty"] = self._fmt_currency(1000.00)

        if M_counter == 0:
            appstruct["materials"] = False
        else:
            appstruct["materials"] = True

        total = 0
        appstruct["labels"] = ["Zakres", "Od", "Do", "Wartość"]
        periods_from = []
        periods_to = []
        for deadline in appstruct["deadlines"]:
            value = deadline["value"]
            period_from = deadline["period_from"]
            period_to = deadline["period_to"]
            periods_from.append(period_from)
            periods_to.append(period_to)
            deadline["period_from"] = self._fmt_datetime(period_from)
            deadline["period_to"] = self._fmt_datetime(period_to)
            deadline["value"] = self._fmt_currency(value)
            total += value
        appstruct["total"] = self._fmt_currency(total)

        today = datetime.datetime.now()
        start_date = min(periods_from)
        end_date = max(periods_to)
        final_date = end_date + datetime.timedelta(30)
        appstruct["today"] = self._fmt_date(today)
        appstruct["start_date"] = self._fmt_date(start_date)
        appstruct["end_date"] = self._fmt_date(end_date)
        appstruct["final_date"] = self._fmt_date(final_date)
        return appstruct

    @property
    def contract_form(self):
        class Price(colander.Schema):
            price = colander.SchemaNode(
                colander.Decimal(),
                title="Cena (PLN)",
                widget=deform.widget.MoneyInputWidget(
                    options={"allowZero": True}
                ),
            )
            unit = colander.SchemaNode(
                colander.String(),
                title="Jednostka",
                missing="",
                widget=deform.widget.SelectWidget(values=UNITS),
                description="Wybierz w przypadku rozliczenia obmiarowego",
            )
            category = colander.SchemaNode(
                colander.List(),
                title="Kategoria",
                widget=deform.widget.CheckboxChoiceWidget(
                    values=RMS, inline=True
                ),
                validator=colander.Length(min=1),
            )
            description = colander.SchemaNode(
                colander.String(),
                title="Opis",
            )

        class Deadline(colander.Schema):
            scope = colander.SchemaNode(
                colander.String(),
                title="Zakres",
            )
            period_from = colander.SchemaNode(
                colander.Date(),
                title="Termin (od)",
            )
            period_to = colander.SchemaNode(
                colander.Date(),
                title="Termin (do)",
            )
            value = colander.SchemaNode(
                colander.Decimal(),
                title="Wartość (PLN)",
                widget=deform.widget.MoneyInputWidget(
                    options={"allowZero": True}
                ),
                description="Podaj 0.00 w przypadku rozliczenia obmiarowego",
            )

        class ContractPrice(colander.SequenceSchema):
            price = Price(title="Cena")

        class Deadlines(colander.SequenceSchema):
            deadline = Deadline(title="Termin")

        class Schema(CSRFSchema):
            docx_template = colander.SchemaNode(
                colander.Integer(),
                title="Szablon dokumentu",
                widget=deform.widget.SelectWidget(values=self.docs),
            )
            representation = colander.SchemaNode(
                colander.List(),
                title="Reprezentacja",
                widget=deform.widget.Select2Widget(
                    values=self.people, multiple=True
                ),
            )
            contacts = colander.SchemaNode(
                colander.List(),
                title="Osoby do kontaktu",
                widget=deform.widget.Select2Widget(
                    values=self.people, multiple=True
                ),
            )
            subject = colander.SchemaNode(
                colander.String(),
                title="Przedmiot umowy",
            )
            works_manager = colander.SchemaNode(
                colander.Boolean(),
                description="Zaznacz, jeśli wymagany jest kierownik robót z uprawnieniami w danej specjalności",
                widget=deform.widget.CheckboxWidget(),
                title="Kierownik robót",
            )
            as_built_documentation = colander.SchemaNode(
                colander.Boolean(),
                description="Zaznacz, jeśli wymagana jest dokumentacja powykonawcza i zdjęciowa robót zanikających",
                widget=deform.widget.CheckboxWidget(),
                title="Dokumentacja powykonawcza",
            )
            lump_sum = colander.SchemaNode(
                colander.Int(),
                validator=colander.OneOf([x[0] for x in SETTLEMENT]),
                widget=deform.widget.RadioChoiceWidget(values=SETTLEMENT),
                title="Rozliczenie",
                description="Wybierz sposób rozliczenia",
            )
            payment_deadline = colander.SchemaNode(
                colander.Integer(),
                default=30,
                title="Termin płatności (dni)",
                validator=colander.Range(min=0),
            )
            utilities = colander.SchemaNode(
                colander.Decimal(),
                default=1,
                title="Media (%)",
                validator=colander.Range(min=0, max=100),
            )
            deposit = colander.SchemaNode(
                colander.Decimal(),
                default=5,
                title="Kaucja (%)",
                validator=colander.Range(min=0, max=100),
            )
            refund = colander.SchemaNode(
                colander.Integer(),
                default=40,
                missing=0,
                title="Zwrot kaucji (%)",
                validator=colander.Range(min=0, max=100),
                description="Podaj 0, jeśli kaucja ma być w całości lub w części zmieniona na gwarancję ubezpieczeniową lub bankową",
            )
            advance_payment = colander.SchemaNode(
                colander.Integer(),
                default=0,
                title="Zaliczka (%)",
                validator=colander.Range(min=0, max=100),
            )
            guarantee = colander.SchemaNode(
                colander.Integer(),
                default=66,
                title="Gwarancja (miesiące)",
                validator=colander.Range(min=0),
            )
            warranty = colander.SchemaNode(
                colander.Integer(),
                default=66,
                title="Rękojmia (miesiące)",
                validator=colander.Range(min=0),
            )
            complaint_address = colander.SchemaNode(
                colander.Integer(),
                title="Adres do zgłaszania wad lub usterek",
                widget=deform.widget.SelectWidget(values=self.emails),
            )
            contract_price = ContractPrice(title="Wynagrodzenie")
            deadlines = Deadlines(title="Terminy")

        schema = Schema().bind(request=self.request)
        submit_btn = deform.form.Button(name="submit", title="Pobierz")
        form = deform.Form(schema, buttons=(submit_btn,))
        form.set_widgets({"subject": deform.widget.TextAreaWidget()})
        form.set_widgets(
            {"contract_price": deform.widget.SequenceWidget(min_len=1)}
        )
        form.set_widgets(
            {"deadlines": deform.widget.SequenceWidget(min_len=1)}
        )
        return form

    @view_config(
        route_name="contract", renderer="form.mako", permission="view"
    )
    def download(self):
        company = self.request.context.company
        self.people = self._get_people(company)
        self.emails = self._get_emails(company)
        self.docs = self._get_docs("contract")
        form = self.contract_form
        appstruct = {}
        rendered_form = None

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                rendered_form = e.render()
            else:
                fields = self._prepare_template_data(company, appstruct)
                docx_template = self._get_document_filename(
                    fields["docx_template"]
                )
                response = export_to_docx(self.request, docx_template, fields)
                log.info(
                    f"Użytkownik {self.request.identity.username} wygenerował wzór umowy dla firmy {company.name}"
                )
                return response

        if rendered_form is None:
            rendered_form = form.render(appstruct=appstruct)
        reqts = form.get_widget_resources()

        return dict(
            heading=f"Wzór umowy dla firmy {company.name}",
            rendered_form=rendered_form,
            css_links=reqts["css"],
            js_links=reqts["js"],
        )
