import io
from urllib.parse import quote

import xlsxwriter
from mako.template import Template
from pyramid.path import AssetResolver
from pyramid.response import Response
from unidecode import unidecode


def export_companies_to_xlsx(companies):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {"constant_memory": True})
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({"bold": True})

    # Write rows.
    header = [
        "Firma",
        "Miasto",
        "Region",
        "Rekomendacje",
        "Link",
    ]

    for j, col in enumerate(header):
        worksheet.write(0, j, col, bold)

    i = 1
    for company in companies:
        cols = [
            company.name,
            company.city,
            company.region,
            company.count_recommended,
            company.link,
        ]
        for j, col in enumerate(cols):
            worksheet.write(i, j, col)
        i += 1

    cols_width = [40, 20, 20, 20, 20]
    for col, width in enumerate(cols_width):
        worksheet.set_column(col, col, width)

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
    response.content_disposition = 'attachment; filename="firmy.xlsx"'
    return response


def export_projects_to_xlsx(projects):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": "dd.mm.yyyy"}
    )
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({"bold": True})
    # Write rows.
    header = [
        "Projekt",
        "Termin",
        "Miasto",
        "Region",
        "Link",
    ]

    for j, col in enumerate(header):
        worksheet.write(0, j, col, bold)

    i = 1
    for project in projects:
        cols = [
            project.name,
            project.deadline,
            project.city,
            project.region,
            project.link,
        ]
        for j, col in enumerate(cols):
            worksheet.write(i, j, col)
        i += 1

    cols_width = [70, 10, 20, 5, 50, 20]
    for col, width in enumerate(cols_width):
        worksheet.set_column(col, col, width)

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
    response.content_disposition = 'attachment; filename="projekty.xlsx"'
    return response


def export_vcard(person):
    response = Response()
    a = AssetResolver("marker")
    resolver = a.resolve("templates/vcard.mako")
    template = Template(filename=resolver.abspath())
    response.text = template.render(person=person)
    response.charset = "utf-8"
    response.content_type = "text/vcard"
    response.content_disposition = f"attachment; filename={unidecode(person.name)}.vcf; filename*=UTF-8''{quote(person.name)}.vcf"
    return response
