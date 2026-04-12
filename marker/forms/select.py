import pycountry

from .ts import TranslationString as _


def select_countries():
    first_option = [("", "---")]
    countries = [(country.alpha_2, country.name) for country in pycountry.countries]
    countries = first_option + countries
    return countries


def select_subdivisions(country_code=None):
    first_option = [("", "---")]
    subdivisions = []
    if country_code:
        country_subdivisions = (
            pycountry.subdivisions.get(country_code=country_code) or []
        )
        subdivisions = [
            (subdivision.code, subdivision.name) for subdivision in country_subdivisions
        ]
        subdivisions = sorted(subdivisions)
    subdivisions = first_option + subdivisions
    return subdivisions


def select_currencies():
    first_option = [("", "---")]
    currencies = [
        (currency.alpha_3, f"{currency.alpha_3} - {currency.name}")
        for currency in pycountry.currencies
    ]
    currencies = sorted(currencies)
    currencies = first_option + currencies
    return currencies


SORT_CRITERIA = [
    ("name", _("Name")),
    ("created_at", _("Date created")),
    ("updated_at", _("Date modified")),
]


SORT_CRITERIA_CONTACTS = [
    ("name", _("Name")),
    ("role", _("Role")),
    ("category_name", _("Category")),
    ("city", _("City")),
    ("subdivision", _("Subdivision")),
    ("country", _("Country")),
    ("created_at", _("Date created")),
    ("updated_at", _("Date modified")),
]


SORT_CRITERIA_EXT = [
    ("name", _("Name")),
    ("city", _("City")),
    ("subdivision", _("Subdivision")),
    ("country", _("Country")),
    ("created_at", _("Date created")),
    ("updated_at", _("Date modified")),
]


SORT_CRITERIA_COMPANIES = [
    ("name", _("Name")),
    ("city", _("City")),
    ("subdivision", _("Subdivision")),
    ("country", _("Country")),
    ("created_at", _("Date created")),
    ("updated_at", _("Date modified")),
    ("stars", _("Stars")),
    ("comments", _("Comments")),
]


SORT_CRITERIA_PROJECTS = [
    ("name", _("Name")),
    ("city", _("City")),
    ("subdivision", _("Subdivision")),
    ("country", _("Country")),
    ("created_at", _("Date created")),
    ("updated_at", _("Date modified")),
    ("stars", _("Stars")),
    ("comments", _("Comments")),
]


ORDER_CRITERIA = [
    ("asc", _("Ascending")),
    ("desc", _("Descending")),
]


STATUS = [
    ("", "---"),
    ("in_progress", _("In progress")),
    ("completed", _("Completed")),
]


# https://getbootstrap.com/docs/5.3/utilities/colors/
COLORS = [
    ("", "---"),
    ("primary", _("Primary")),
    ("secondary", _("Secondary")),
    ("success", _("Success")),
    ("danger", _("Danger")),
    ("warning", _("Warning")),
    ("info", _("Info")),
    ("light", _("Light")),
    ("dark", _("Dark")),
]


USER_ROLES = [
    ("default", _("Default")),
    ("editor", _("Editor")),
    ("admin", _("Administrator")),
]


COMPANY_ROLES = [
    ("", "---"),
    ("designer", _("Designer")),
    ("purchaser", _("Purchaser")),
    ("investor", _("Investor")),
    ("general_contractor", _("General Contractor")),
    ("subcontractor", _("Subcontractor")),
    ("supplier", _("Supplier")),
]


STAGES = [
    ("", "---"),
    ("announcement", _("Announcement")),
    ("tender", _("Tender")),
    ("construction", _("Construction")),
]


PROJECT_DELIVERY_METHODS = [
    ("", "---"),
    ("design-build", _("Design–build")),
    ("build", _("Build")),
]


CATEGORIES = [
    ("", _("All")),
    ("companies", _("Companies")),
    ("projects", _("Projects")),
]


REPORTS = [
    ("companies-tags", _("The most popular tags among companies")),
    ("projects-tags", _("The most popular tags among projects")),
    ("companies-subdivisions", _("Subdivisions with the largest number of companies")),
    ("companies-cities", _("Cities with the largest number of companies")),
    ("companies-comments", _("The most commented companies")),
    ("projects-subdivisions", _("Subdivisions with the largest number of projects")),
    ("projects-cities", _("Cities with the largest number of projects")),
    ("projects-comments", _("The most commented projects")),
    ("users-companies", _("User activity (added companies)")),
    ("users-projects", _("User activity (added projects)")),
    ("companies-projects", _("Investors (number of projects)")),
    ("companies-stars", _("Recommended companies")),
    ("projects-stars", _("Watched projects")),
    (
        "companies-announcement",
        _("Companies that announced the largest number of investments"),
    ),
    (
        "companies-tenders",
        _("Companies that took part in the largest number of tenders"),
    ),
    (
        "companies-constructions",
        _("Companies that have completed the largest number of investments"),
    ),
    ("designers", _("The most active designers")),
    ("purchasers", _("The most active purchasers")),
    ("investors", _("The most active investors")),
    ("general-contractors", _("The most active general contractors")),
    ("subcontractors", _("The most active subcontractors")),
    ("suppliers", _("The most active suppliers")),
    ("projects-companies", _("Projects with the greatest interest")),
    ("projects-highest-value", _("Projects with the highest value")),
    ("projects-highest-usable-area", _("Projects with the highest usable area")),
    ("projects-highest-cubic-volume", _("Projects with the highest cubic volume")),
]
