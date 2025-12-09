import io
from urllib.parse import quote

import pycountry
import xlsxwriter
from mako.template import Template
from pyramid.path import AssetResolver
from pyramid.response import Response
from unidecode import unidecode

from ..forms.ts import TranslationString as _


def response_xlsx(rows, header_row, default_date_format="yyyy-mm-dd"):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()
    # Create a workbook.
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": default_date_format}
    )
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format({"bold": True})

    index_of_subdivision = None
    try:
        index_of_subdivision = header_row.index(str(_("Subdivision")))
    except ValueError:
        pass

    index_of_country = None
    try:
        index_of_country = header_row.index(str(_("Country")))
    except ValueError:
        pass

    # Write rows.
    for j, elem in enumerate(header_row):
        worksheet.write(0, j, elem, cell_format)

    for i, row in enumerate(rows, start=1):
        for j, elem in enumerate(row):
            if j == index_of_subdivision:
                elem = getattr(pycountry.subdivisions.get(code=elem), "name", "---")
            elif j == index_of_country:
                elem = getattr(pycountry.countries.get(alpha_2=elem), "name", "---")
            worksheet.write(i, j, elem)

    # Close the workbook before streaming the data.
    workbook.close()
    # Rewind the buffer.
    output.seek(0)
    # Construct a server response.
    response = Response()
    response.body_file = output
    response.content_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response.content_disposition = 'attachment; filename="Marker.xlsx"'
    return response


def response_contacts_xlsx(rows, default_date_format="yyyy-mm-dd"):
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
        _("Company_Project"),
    ]

    # Write rows.
    for j, elem in enumerate(header_row):
        worksheet.write(0, j, str(elem), cell_format)

    for i, row in enumerate(rows, start=1):
        worksheet.write(i, 0, row.name)
        worksheet.write(i, 1, row.role)
        worksheet.write(i, 2, row.phone)
        worksheet.write(i, 3, row.email)
        if row.company:
            worksheet.write(i, 4, row.company.name)
        if row.project:
            worksheet.write(i, 4, row.project.name)

    # Close the workbook before streaming the data.
    workbook.close()
    # Rewind the buffer.
    output.seek(0)
    # Construct a server response.
    response = Response()
    response.body_file = output
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
    response.content_disposition = f"attachment; filename={unidecode(contact.name)}.vcf; filename*=UTF-8''{quote(contact.name)}.vcf"
    return response
