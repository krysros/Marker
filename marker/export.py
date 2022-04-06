import io
import xlsxwriter
from pathlib import Path
from urllib.parse import quote
from unidecode import unidecode
from mako.template import Template
from pyramid.response import Response
from pyramid.path import AssetResolver
from docxtpl import DocxTemplate


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
        "Województwo",
        "Rekomendacje",
        "Imię i nazwisko",
        "Stanowisko",
        "Telefon",
        "Email",
        "WWW",
    ]

    for j, col in enumerate(header):
        worksheet.write(0, j, col, bold)

    i = 1
    for company in companies:
        cols = [
            company.name,
            company.city,
            company.voivodeship,
            company.upvote_count,
            "",
            "",
            company.phone,
            company.email,
            company.www,
        ]
        for j, col in enumerate(cols):
            worksheet.write(i, j, col)
        i += 1
        for person in company.people:
            cols = [
                company.name,
                company.city,
                company.voivodeship,
                company.upvote_count,
                person.fullname,
                person.position,
                person.phone,
                person.email,
                company.www,
            ]
            for j, col in enumerate(cols):
                worksheet.write(i, j, col)
            i += 1

    cols_width = [50, 20, 5, 5, 20, 30, 20, 20, 20]
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


def export_tenders_to_xlsx(tenders):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        output, {"constant_memory": True, "default_date_format": "dd.mm.yyyy"}
    )
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({"bold": True})
    # Write rows.
    header = [
        "Przetarg",
        "Miasto",
        "Województwo",
        "Zamawiający",
        "WWW",
        "Termin składania ofert",
    ]

    for j, col in enumerate(header):
        worksheet.write(0, j, col, bold)

    i = 1
    for tender in tenders:
        cols = [
            tender.name,
            tender.city,
            tender.voivodeship,
            tender.company.name,
            tender.link,
            tender.deadline,
        ]
        for j, col in enumerate(cols):
            worksheet.write(i, j, col)
        i += 1

    cols_width = [70, 20, 5, 50, 20, 10]
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
    response.content_disposition = 'attachment; filename="przetargi.xlsx"'
    return response


def export_to_docx(request, docx_template, fields):
    storage_base_path = request.registry.settings.get("storage.base_path")
    p = Path(storage_base_path, docx_template)
    docx = DocxTemplate(p)
    docx.render(fields)
    output = io.BytesIO()
    docx.save(output)
    output.seek(0)
    response = request.response
    response.body_file = output
    response.content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    response.content_disposition = f'attachment; filename="{docx_template}"'
    return response


def export_vcard(person):
    response = Response()
    a = AssetResolver("marker")
    resolver = a.resolve("templates/vcard.mako")
    template = Template(filename=resolver.abspath())
    response.text = template.render(person=person)
    response.charset = "utf-8"
    response.content_type = "text/vcard"
    response.content_disposition = f"attachment; filename={unidecode(person.fullname)}.vcf; filename*=UTF-8''{quote(person.fullname)}.vcf"
    return response
