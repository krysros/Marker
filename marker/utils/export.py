import datetime
import io
import unicodedata
from urllib.parse import quote

import xlsxwriter
from mako.template import Template
from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import Style, TextProperties
from odf.table import Table, TableCell, TableColumn, TableRow
from odf.text import P
from pyramid.path import AssetResolver
from pyramid.response import Response

from ..forms.select import PROJECT_DELIVERY_METHODS, STAGES
from ..forms.ts import TranslationString as _
from ..subscribers import get_country_name, get_subdivision_name


def ascii_slug(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


# ---------------------------------------------------------------------------
# Module-level helpers shared by all export functions
# ---------------------------------------------------------------------------

def _normalized(text):
    return str(text or "").strip().lower()


def _safe_cell_value(value):
    if value is None:
        return ""
    if isinstance(value, (datetime.datetime, datetime.date, str, int, float, bool)):
        return value
    return str(value)


_STAGES_MAP = dict(STAGES)
_DELIVERY_METHODS_MAP = dict(PROJECT_DELIVERY_METHODS)


def _build_column_transformers():
    """Build column transformer list. Must be called within a request context."""
    return [
        (
            {_normalized(_("Subdivision")), "subdivision", "województwo"},
            get_subdivision_name,
        ),
        (
            {_normalized(_("Country")), "country", "kraj"},
            get_country_name,
        ),
        (
            {_normalized(_("Stage")), _normalized(_("Project stage")), "stage", "project stage"},
            lambda v: _STAGES_MAP.get(v, v or ""),
        ),
        (
            {
                _normalized(_("Project delivery method")),
                _normalized(_("Delivery method")),
                "project delivery method",
                "delivery method",
            },
            lambda v: _DELIVERY_METHODS_MAP.get(v, v or ""),
        ),
    ]


def _apply_column_transform(elem, header_name, column_transformers):
    for markers, transform in column_transformers:
        if any(marker and marker in header_name for marker in markers):
            return transform(elem)
    return elem


# ---------------------------------------------------------------------------
# XLSX
# ---------------------------------------------------------------------------

def response_xlsx(rows, header_row, default_date_format="yyyy-mm-dd", row_colors=None):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": default_date_format}
    )
    worksheet = workbook.add_worksheet()
    bold_format = workbook.add_format({"bold": True})
    date_format = workbook.add_format({"num_format": default_date_format})
    column_transformers = _build_column_transformers()

    normalized_headers = [_normalized(h) for h in header_row]

    for j, elem in enumerate(header_row):
        worksheet.write(0, j, str(elem).replace(" ", "_"), bold_format)

    for i, row in enumerate(rows, start=1):
        for j, elem in enumerate(row):
            elem = _apply_column_transform(elem, normalized_headers[j], column_transformers)
            elem = _safe_cell_value(elem)
            if isinstance(elem, (datetime.datetime, datetime.date)):
                worksheet.write(i, j, elem, date_format)
            else:
                worksheet.write(i, j, elem)

    workbook.close()
    output.seek(0)
    response = Response()
    response.body_file = output
    response.body = output.getvalue()  # For test access
    response.content_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response.content_disposition = 'attachment; filename="Marker.xlsx"'
    return response


def _response_xlsx_contacts(rows, entity_attr, entity_label, default_date_format="yyyy-mm-dd"):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": default_date_format}
    )
    worksheet = workbook.add_worksheet()
    bold_format = workbook.add_format({"bold": True})

    header_row = [_("Name"), _("Role"), _("Phone"), _("Email"), entity_label, _("City"), _("Subdivision"), _("Country")]
    for j, elem in enumerate(header_row):
        worksheet.write(0, j, str(elem).replace(" ", "_"), bold_format)

    for i, row in enumerate(rows, start=1):
        entity = getattr(row, entity_attr)
        worksheet.write(i, 0, row.name)
        worksheet.write(i, 1, row.role)
        worksheet.write(i, 2, row.phone)
        worksheet.write(i, 3, row.email)
        worksheet.write(i, 4, entity.name)
        worksheet.write(i, 5, entity.city)
        worksheet.write(i, 6, get_subdivision_name(entity.subdivision))
        worksheet.write(i, 7, get_country_name(entity.country))

    workbook.close()
    output.seek(0)
    response = Response()
    response.body_file = output
    response.body = output.getvalue()  # For test access
    response.content_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response.content_disposition = 'attachment; filename="Marker.xlsx"'
    return response


def response_xlsx_contacts_company(rows, default_date_format="yyyy-mm-dd"):
    return _response_xlsx_contacts(rows, "company", _("Company"), default_date_format)


def response_xlsx_contacts_project(rows, default_date_format="yyyy-mm-dd"):
    return _response_xlsx_contacts(rows, "project", _("Project"), default_date_format)


# ---------------------------------------------------------------------------
# ODS
# ---------------------------------------------------------------------------

def response_ods(rows, header_row, row_colors=None):
    doc = OpenDocumentSpreadsheet()

    bold_style = Style(name="bold", family="table-cell")
    bold_style.addElement(TextProperties(fontweight="bold"))
    doc.automaticstyles.addElement(bold_style)
    column_transformers = _build_column_transformers()

    normalized_headers = [_normalized(h) for h in header_row]

    table = Table(name="Sheet1")
    table.addElement(TableColumn(numbercolumnsrepeated=str(len(header_row))))

    header_tr = TableRow()
    for elem in header_row:
        tc = TableCell(stylename=bold_style, valuetype="string")
        tc.addElement(P(text=str(elem).replace(" ", "_")))
        header_tr.addElement(tc)
    table.addElement(header_tr)

    for row in rows:
        tr = TableRow()
        for j, elem in enumerate(row):
            elem = _apply_column_transform(elem, normalized_headers[j], column_transformers)
            if isinstance(elem, (datetime.datetime, datetime.date)):
                tc = TableCell(valuetype="date", datevalue=elem.isoformat())
                tc.addElement(P(text=str(elem)))
            elif isinstance(elem, (int, float)):
                tc = TableCell(valuetype="float", value=str(elem))
                tc.addElement(P(text=str(elem)))
            else:
                tc = TableCell(valuetype="string")
                tc.addElement(P(text=str(elem if elem is not None else "")))
            tr.addElement(tc)
        table.addElement(tr)

    doc.spreadsheet.addElement(table)

    output = io.BytesIO()
    doc.save(output)
    output.seek(0)

    response = Response()
    response.body = output.getvalue()
    response.content_type = "application/vnd.oasis.opendocument.spreadsheet"
    response.content_disposition = 'attachment; filename="Marker.ods"'
    return response


def _response_ods_contacts(rows, entity_attr, entity_label):
    doc = OpenDocumentSpreadsheet()

    bold_style = Style(name="bold", family="table-cell")
    bold_style.addElement(TextProperties(fontweight="bold"))
    doc.automaticstyles.addElement(bold_style)

    header_row = [_("Name"), _("Role"), _("Phone"), _("Email"), entity_label, _("City"), _("Subdivision"), _("Country")]

    table = Table(name="Sheet1")
    table.addElement(TableColumn(numbercolumnsrepeated=str(len(header_row))))

    header_tr = TableRow()
    for elem in header_row:
        tc = TableCell(stylename=bold_style, valuetype="string")
        tc.addElement(P(text=str(elem).replace(" ", "_")))
        header_tr.addElement(tc)
    table.addElement(header_tr)

    for row in rows:
        entity = getattr(row, entity_attr)
        values = [
            row.name,
            row.role,
            row.phone,
            row.email,
            entity.name,
            entity.city,
            get_subdivision_name(entity.subdivision),
            get_country_name(entity.country),
        ]
        tr = TableRow()
        for val in values:
            tc = TableCell(valuetype="string")
            tc.addElement(P(text=str(val or "")))
            tr.addElement(tc)
        table.addElement(tr)

    doc.spreadsheet.addElement(table)

    output = io.BytesIO()
    doc.save(output)
    output.seek(0)

    response = Response()
    response.body = output.getvalue()
    response.content_type = "application/vnd.oasis.opendocument.spreadsheet"
    response.content_disposition = 'attachment; filename="Marker.ods"'
    return response


def response_ods_contacts_company(rows):
    return _response_ods_contacts(rows, "company", _("Company"))


def response_ods_contacts_project(rows):
    return _response_ods_contacts(rows, "project", _("Project"))


def vcard_template():
    a = AssetResolver("marker")
    resolver = a.resolve("templates/contact/vcard.mako")
    template = Template(filename=resolver.abspath())
    return template


def response_vcard(contact):
    response = Response()
    template = vcard_template()
    response.text = template.render(contact=contact)
    response.charset = "utf-8"
    response.content_type = "text/vcard"
    response.content_disposition = f"attachment; filename={ascii_slug(contact.name)}.vcf; filename*=UTF-8''{quote(contact.name)}.vcf"
    return response
