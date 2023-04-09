import io
from urllib.parse import quote

import xlsxwriter
from mako.template import Template
from pyramid.path import AssetResolver
from pyramid.response import Response
from unidecode import unidecode


def response_xlsx(rows, header_row):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": "dd.mm.yyyy"}
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


def export_companies_to_xlsx(request, companies):
    _ = request.translate
    header_row = [
        _("Name"),
        _("Street"),
        _("Post code"),
        _("City"),
        _("Subdivision"),
        _("Country"),
        _("Link"),
        _("NIP"),
        _("REGON"),
        _("KRS"),
        _("Court"),
    ]
    return response_xlsx(companies, header_row)


def export_projects_to_xlsx(request, projects):
    _ = request.translate
    header_row = [
        _("Name"),
        _("Street"),
        _("Post code"),
        _("City"),
        _("Subdivision"),
        _("Country"),
        _("Link"),
        _("Deadline"),
        _("Stage"),
        _("Project delivery method"),
    ]
    return response_xlsx(projects, header_row)


def export_tags_to_xlsx(request, tags):
    _ = request.translate
    header_row = [_("Tag")]
    return response_xlsx(tags, header_row)


def export_contacts_to_xlsx(request, contacts):
    _ = request.translate
    header_row = [_("Fullname"), _("Role"), _("Phone"), _("Email")]
    return response_xlsx(contacts, header_row)


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
