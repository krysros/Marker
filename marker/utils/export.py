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


def response_xlsx(rows, header_row, default_date_format="yyyy-mm-dd", row_colors=None):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": default_date_format}
    )
    worksheet = workbook.add_worksheet()
    bold_format = workbook.add_format({"bold": True})
    date_format = workbook.add_format({"num_format": default_date_format})
    stages_map = dict(STAGES)
    delivery_methods_map = dict(PROJECT_DELIVERY_METHODS)

    def _normalized(text):
        return str(text or "").strip().lower()

    def _safe_cell_value(value):
        if value is None:
            return ""
        if isinstance(value, (datetime.datetime, datetime.date, str, int, float, bool)):
            return value
        return str(value)

    subdivision_markers = {
        _normalized(_("Subdivision")),
        "subdivision",
        "województwo",
    }
    country_markers = {
        _normalized(_("Country")),
        "country",
        "kraj",
    }
    stage_markers = {
        _normalized(_("Stage")),
        _normalized(_("Project stage")),
        "stage",
        "project stage",
    }
    delivery_method_markers = {
        _normalized(_("Project delivery method")),
        _normalized(_("Delivery method")),
        "project delivery method",
        "delivery method",
    }
    column_transformers = [
        (subdivision_markers, lambda value: get_subdivision_name(value)),
        (country_markers, lambda value: get_country_name(value)),
        (stage_markers, lambda value: stages_map.get(value, value or "")),
        (delivery_method_markers, lambda value: delivery_methods_map.get(value, value or "")),
    ]

    for j, elem in enumerate(header_row):
        header = str(elem).replace(" ", "_")
        worksheet.write(0, j, header, bold_format)

    for i, row in enumerate(rows, start=1):
        for j, elem in enumerate(row):
            header_name = _normalized(header_row[j])
            for markers, transform in column_transformers:
                if any(marker and marker in header_name for marker in markers):
                    elem = transform(elem)
                    break
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


def response_xlsx_contacts_company(rows, default_date_format="yyyy-mm-dd"):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()
    # Create a workbook.
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": default_date_format}
    )
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format({"bold": True})

    header_row = [
        _("Name"),
        _("Role"),
        _("Phone"),
        _("Email"),
        _("Company"),
        _("City"),
        _("Subdivision"),
        _("Country"),
    ]

    # Write header row with underscores instead of spaces
    for j, elem in enumerate(header_row):
        header = str(elem).replace(" ", "_")
        worksheet.write(0, j, header, cell_format)

    for i, row in enumerate(rows, start=1):
        worksheet.write(i, 0, row.name)
        worksheet.write(i, 1, row.role)
        worksheet.write(i, 2, row.phone)
        worksheet.write(i, 3, row.email)
        worksheet.write(i, 4, row.company.name)
        worksheet.write(i, 5, row.company.city)
        worksheet.write(
            i,
            6,
            get_subdivision_name(row.company.subdivision),
        )
        worksheet.write(
            i,
            7,
            get_country_name(row.company.country),
        )

    # Close the workbook before streaming the data.
    workbook.close()
    # Rewind the buffer.
    output.seek(0)
    # Construct a server response.
    response = Response()
    response.body_file = output
    response.body = output.getvalue()  # For test access
    response.content_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response.content_disposition = 'attachment; filename="Marker.xlsx"'
    return response


def response_xlsx_contacts_project(rows, default_date_format="yyyy-mm-dd"):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()
    # Create a workbook.
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": default_date_format}
    )
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format({"bold": True})

    header_row = [
        _("Name"),
        _("Role"),
        _("Phone"),
        _("Email"),
        _("Project"),
        _("City"),
        _("Subdivision"),
        _("Country"),
    ]

    # Write header row with underscores instead of spaces
    for j, elem in enumerate(header_row):
        header = str(elem).replace(" ", "_")
        worksheet.write(0, j, header, cell_format)

    for i, row in enumerate(rows, start=1):
        worksheet.write(i, 0, row.name)
        worksheet.write(i, 1, row.role)
        worksheet.write(i, 2, row.phone)
        worksheet.write(i, 3, row.email)
        worksheet.write(i, 4, row.project.name)
        worksheet.write(i, 5, row.project.city)
        worksheet.write(
            i,
            6,
            get_subdivision_name(row.project.subdivision),
        )
        worksheet.write(
            i,
            7,
            get_country_name(row.project.country),
        )

    # Close the workbook before streaming the data.
    workbook.close()
    # Rewind the buffer.
    output.seek(0)
    # Construct a server response.
    response = Response()
    response.body_file = output
    response.body = output.getvalue()  # For test access
    response.content_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response.content_disposition = 'attachment; filename="Marker.xlsx"'
    return response


def response_ods(rows, header_row, row_colors=None):
    doc = OpenDocumentSpreadsheet()
    stages_map = dict(STAGES)
    delivery_methods_map = dict(PROJECT_DELIVERY_METHODS)

    bold_style = Style(name="bold", family="table-cell")
    bold_style.addElement(TextProperties(fontweight="bold"))
    doc.automaticstyles.addElement(bold_style)

    def _normalized(text):
        return str(text or "").strip().lower()

    subdivision_markers = {
        _normalized(_("Subdivision")),
        "subdivision",
        "województwo",
    }
    country_markers = {
        _normalized(_("Country")),
        "country",
        "kraj",
    }
    stage_markers = {
        _normalized(_("Stage")),
        _normalized(_("Project stage")),
        "stage",
        "project stage",
    }
    delivery_method_markers = {
        _normalized(_("Project delivery method")),
        _normalized(_("Delivery method")),
        "project delivery method",
        "delivery method",
    }
    column_transformers = [
        (subdivision_markers, lambda value: get_subdivision_name(value)),
        (country_markers, lambda value: get_country_name(value)),
        (stage_markers, lambda value: stages_map.get(value, value or "")),
        (delivery_method_markers, lambda value: delivery_methods_map.get(value, value or "")),
    ]

    table = Table(name="Sheet1")
    table.addElement(TableColumn(numbercolumnsrepeated=str(len(header_row))))

    header_tr = TableRow()
    for elem in header_row:
        header = str(elem).replace(" ", "_")
        tc = TableCell(stylename=bold_style, valuetype="string")
        tc.addElement(P(text=header))
        header_tr.addElement(tc)
    table.addElement(header_tr)

    for row in rows:
        tr = TableRow()
        for j, elem in enumerate(row):
            header_name = _normalized(header_row[j])
            for markers, transform in column_transformers:
                if any(marker and marker in header_name for marker in markers):
                    elem = transform(elem)
                    break
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


def response_ods_contacts_company(rows):
    doc = OpenDocumentSpreadsheet()

    bold_style = Style(name="bold", family="table-cell")
    bold_style.addElement(TextProperties(fontweight="bold"))
    doc.automaticstyles.addElement(bold_style)

    header_row = [
        _("Name"),
        _("Role"),
        _("Phone"),
        _("Email"),
        _("Company"),
        _("City"),
        _("Subdivision"),
        _("Country"),
    ]

    table = Table(name="Sheet1")
    table.addElement(TableColumn(numbercolumnsrepeated=str(len(header_row))))

    header_tr = TableRow()
    for elem in header_row:
        header = str(elem).replace(" ", "_")
        tc = TableCell(stylename=bold_style, valuetype="string")
        tc.addElement(P(text=header))
        header_tr.addElement(tc)
    table.addElement(header_tr)

    for row in rows:
        tr = TableRow()
        values = [
            row.name,
            row.role,
            row.phone,
            row.email,
            row.company.name,
            row.company.city,
            get_subdivision_name(row.company.subdivision),
            get_country_name(row.company.country),
        ]
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


def response_ods_contacts_project(rows):
    doc = OpenDocumentSpreadsheet()

    bold_style = Style(name="bold", family="table-cell")
    bold_style.addElement(TextProperties(fontweight="bold"))
    doc.automaticstyles.addElement(bold_style)

    header_row = [
        _("Name"),
        _("Role"),
        _("Phone"),
        _("Email"),
        _("Project"),
        _("City"),
        _("Subdivision"),
        _("Country"),
    ]

    table = Table(name="Sheet1")
    table.addElement(TableColumn(numbercolumnsrepeated=str(len(header_row))))

    header_tr = TableRow()
    for elem in header_row:
        header = str(elem).replace(" ", "_")
        tc = TableCell(stylename=bold_style, valuetype="string")
        tc.addElement(P(text=header))
        header_tr.addElement(tc)
    table.addElement(header_tr)

    for row in rows:
        tr = TableRow()
        values = [
            row.name,
            row.role,
            row.phone,
            row.email,
            row.project.name,
            row.project.city,
            get_subdivision_name(row.project.subdivision),
            get_country_name(row.project.country),
        ]
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
