import io
from urllib.parse import quote

import xlsxwriter
from mako.template import Template
from pyramid.path import AssetResolver
from pyramid.response import Response
from unidecode import unidecode


def response_xlsx(items, header, cols):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": "dd.mm.yyyy"}
    )
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({"bold": True})

    # Write rows.
    for j, col in enumerate(header):
        worksheet.write(0, j, col, bold)

    i = 1
    for item in items:
        for j, col in enumerate(cols):
            worksheet.write(i, j, getattr(item, col))
        i += 1

    for col, width in enumerate(cols.values()):
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
    response.content_disposition = 'attachment; filename="Marker.xlsx"'
    return response


def export_companies_to_xlsx(request, companies):
    _ = request.translate

    header = [
        _("Company"),
        _("City"),
        _("Subdivision"),
        _("Recommended"),
        _("Link"),
    ]

    cols = {
        "name": 40,
        "city": 20,
        "subdivision": 20,
        "count_recommended": 20,
        "link": 20,
    }
    return response_xlsx(companies, header, cols)


def export_projects_to_xlsx(request, projects):
    _ = request.translate

    header = [
        _("Project"),
        _("Deadline"),
        _("City"),
        _("Subdivision"),
        _("Link"),
    ]

    cols = {"name": 70, "deadline": 10, "city": 20, "subdivision": 5, "link": 50}
    return response_xlsx(projects, header, cols)


def export_tags_to_xlsx(request, tags):
    _ = request.translate

    header = [_("Tag"), _("Companies"), _("Projects")]
    cols = {"name": 70, "count_companies": 10, "count_projects": 10}
    return response_xlsx(tags, header, cols)


def export_contacts_to_xlsx(request, contacts):
    _ = request.translate

    header = [
        _("First name and last name"),
        _("Role"),
        _("Phone"),
        _("Email"),
    ]

    cols = {"name": 70, "role": 20, "phone": 20, "email": 20}
    return response_xlsx(contacts, header, cols)


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
