import io
from urllib.parse import quote

import xlsxwriter
from mako.template import Template
from pyramid.path import AssetResolver
from pyramid.response import Response
from unidecode import unidecode


def response_xlsx(rows, header_row, default_date_format="yyyy-mm-dd"):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()
    # Create a workbook.
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": default_date_format}
    )
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format({"bold": True})

    # Write rows.
    for j, elem in enumerate(header_row):
        worksheet.write(0, j, elem, cell_format)

    for i, row in enumerate(rows, start=1):
        for j, elem in enumerate(row):
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


def response_vcard(contact):
    response = Response()
    a = AssetResolver("marker")
    resolver = a.resolve("templates/vcard.mako")
    template = Template(filename=resolver.abspath())
    response.text = template.render(contact=contact)
    response.charset = "utf-8"
    response.content_type = "text/vcard"
    response.content_disposition = f"attachment; filename={unidecode(contact.name)}.vcf; filename*=UTF-8''{quote(contact.name)}.vcf"
    return response
