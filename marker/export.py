import io
from urllib.parse import quote

import xlsxwriter
from mako.template import Template
from pyramid.path import AssetResolver
from pyramid.response import Response
from unidecode import unidecode


def export_companies_to_xlsx(request, companies):
    _ = request.translate
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {"constant_memory": True})
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({"bold": True})

    # Write rows.
    header = [
        _("Company"),
        _("City"),
        _("Region"),
        _("Recommended"),
        _("Link"),
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
    response.content_disposition = 'attachment; filename="%s.xlsx"' % _("Companies")
    return response


def export_projects_to_xlsx(request, projects):
    _ = request.translate
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": "dd.mm.yyyy"}
    )
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({"bold": True})
    # Write rows.
    header = [
        _("Project"),
        _("Deadline"),
        _("City"),
        _("Region"),
        _("Link"),
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
    response.content_disposition = 'attachment; filename="%s.xlsx"' % _("Projects")
    return response


def export_tags_to_xlsx(request, tags):
    _ = request.translate
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": "dd.mm.yyyy"}
    )
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({"bold": True})
    # Write rows.
    header = [_("Tag"), _("Companies"), _("Projects")]

    for j, col in enumerate(header):
        worksheet.write(0, j, col, bold)

    i = 1
    for tag in tags:
        cols = [tag.name, tag.count_companies, tag.count_projects]
        for j, col in enumerate(cols):
            worksheet.write(i, j, col)
        i += 1

    cols_width = [70, 10, 10]
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
    response.content_disposition = 'attachment; filename="%s.xlsx"' % _("Tags")
    return response


def export_contacts_to_xlsx(request, contacts):
    _ = request.translate
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": "dd.mm.yyyy"}
    )
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({"bold": True})
    # Write rows.
    header = [
        _("First name and last name"),
        _("Company/Project"),
        _("Role"),
        _("Phone"),
        _("Email"),
    ]

    for j, col in enumerate(header):
        worksheet.write(0, j, col, bold)

    i = 1
    for contact in contacts:
        if contact.company:
            member = contact.company.name
        elif contact.project:
            member = contact.project.name
        else:
            member = "---"
        cols = [
            contact.name,
            member,
            contact.role,
            contact.phone,
            contact.email,
        ]
        for j, col in enumerate(cols):
            worksheet.write(i, j, col)
        i += 1

    cols_width = [70, 20, 20, 20, 20]
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
    response.content_disposition = 'attachment; filename="%s.xlsx"' % _("Contacts")
    return response


def export_vcard(contact):
    response = Response()
    a = AssetResolver("marker")
    resolver = a.resolve("templates/vcard.mako")
    template = Template(filename=resolver.abspath())
    response.text = template.render(contact=contact)
    response.charset = "utf-8"
    response.content_type = "text/vcard"
    response.content_disposition = f"attachment; filename={unidecode(contact.name)}.vcf; filename*=UTF-8''{quote(contact.name)}.vcf"
    return response
