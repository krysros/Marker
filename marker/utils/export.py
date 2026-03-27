import datetime
import io
import unicodedata
from urllib.parse import quote

import pycountry
import xlsxwriter
from mako.template import Template
from pyramid.path import AssetResolver
from pyramid.response import Response
from ..forms.select import COURTS, PROJECT_DELIVERY_METHODS, STAGES
from ..forms.ts import TranslationString as _
from ..forms.select import COURTS, PROJECT_DELIVERY_METHODS, STAGES
from ..forms.ts import TranslationString as _


def ascii_slug(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def response_xlsx(rows, header_row, default_date_format="yyyy-mm-dd", row_colors=None):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()
    # Create a workbook.
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": default_date_format}
    )
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format({"bold": True})
    courts_map = dict(COURTS)
    stages_map = dict(STAGES)
    delivery_methods_map = dict(PROJECT_DELIVERY_METHODS)
    bootstrap_palette = {
        "primary": {"bg": "#DCEBFF", "font": "#1F2D3D"},
        "secondary": {"bg": "#ECEFF1", "font": "#1F2D3D"},
        "success": {"bg": "#DDF3E4", "font": "#1F2D3D"},
        "danger": {"bg": "#FBE3E6", "font": "#1F2D3D"},
        "warning": {"bg": "#FFF4CC", "font": "#1F2D3D"},
        "info": {"bg": "#D8F4FB", "font": "#1F2D3D"},
        "light": {"bg": "#F8F9FA", "font": "#1F2D3D"},
        "dark": {"bg": "#D6D8DB", "font": "#1F2D3D"},
    }

    row_formats = {}
    row_date_formats = {}
    for color_key, palette in bootstrap_palette.items():
        row_formats[color_key] = workbook.add_format(
            {"bg_color": palette["bg"], "font_color": palette["font"]}
        )
        row_date_formats[color_key] = workbook.add_format(
            {
                "bg_color": palette["bg"],
                "font_color": palette["font"],
                "num_format": default_date_format,
            }
        )

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
    court_markers = {
        _normalized(_("Court")),
        "court",
        "sąd",
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
        (
            subdivision_markers,
            lambda value: getattr(pycountry.subdivisions.get(code=value), "name", ""),
        ),
        (
            country_markers,
            lambda value: getattr(pycountry.countries.get(alpha_2=value), "name", ""),
        ),
        (court_markers, lambda value: courts_map.get(value, value or "")),
        (stage_markers, lambda value: stages_map.get(value, value or "")),
        (
            delivery_method_markers,
            lambda value: delivery_methods_map.get(value, value or ""),
        ),
    ]

    # Write rows.
    # Write header row with underscores instead of spaces
    for j, elem in enumerate(header_row):
        header = str(elem).replace(" ", "_")
        worksheet.write(0, j, _safe_cell_value(header), cell_format)

    for i, row in enumerate(rows, start=1):
        row_color = None
        if row_colors and len(row_colors) >= i:
            row_color = str(row_colors[i - 1] or "").strip().lower()

        for j, elem in enumerate(row):
            header_name = _normalized(header_row[j])

            for markers, transform in column_transformers:
                if any(marker and marker in header_name for marker in markers):
                    elem = transform(elem)
                    break

            elem = _safe_cell_value(elem)

            if row_color in row_formats:
                if isinstance(elem, (datetime.datetime, datetime.date)):
                    worksheet.write(i, j, elem, row_date_formats[row_color])
                else:
                    worksheet.write(i, j, elem, row_formats[row_color])
            else:
                worksheet.write(i, j, elem)

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
            getattr(
                pycountry.subdivisions.get(code=row.company.subdivision), "name", ""
            ),
        )
        worksheet.write(
            i,
            7,
            getattr(pycountry.countries.get(alpha_2=row.company.country), "name", ""),
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
            getattr(
                pycountry.subdivisions.get(code=row.project.subdivision), "name", ""
            ),
        )
        worksheet.write(
            i,
            7,
            getattr(pycountry.countries.get(alpha_2=row.project.country), "name", ""),
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
