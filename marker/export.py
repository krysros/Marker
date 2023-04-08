import io
from urllib.parse import quote

import xlsxwriter
from mako.template import Template
from pyramid.path import AssetResolver
from pyramid.response import Response
from unidecode import unidecode

from .models import Company, Project, Tag, Contact


def response_xlsx(items, columns):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": "dd.mm.yyyy"}
    )
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({"bold": True})

    # Write rows.
    for j, col in enumerate(columns):
        worksheet.write(0, j, col, bold)

    for i, item in enumerate(items, start=1):
        for j, col in enumerate(columns):
            worksheet.write(i, j, getattr(item, col))

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


def export_companies_to_xlsx(request, companies):
    _ = request.translate
    columns = Company.__table__.columns.keys()
    return response_xlsx(companies, columns)


def export_projects_to_xlsx(request, projects):
    _ = request.translate
    columns = Project.__table__.columns.keys()
    return response_xlsx(projects, columns)


def export_tags_to_xlsx(request, tags):
    _ = request.translate
    columns = Tag.__table__.columns.keys()
    return response_xlsx(tags, columns)


def export_contacts_to_xlsx(request, contacts):
    _ = request.translate
    columns = Contact.__table__.columns.keys()
    return response_xlsx(contacts, columns)


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
