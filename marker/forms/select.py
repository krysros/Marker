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
        subdivisions = [
            (subdivision.code, subdivision.name)
            for subdivision in pycountry.subdivisions.get(country_code=country_code)
        ]
        subdivisions = sorted(subdivisions)
    subdivisions = first_option + subdivisions
    return subdivisions


SORT_CRITERIA = [
    ("name", _("by name")),
    ("created_at", _("by date added")),
    ("updated_at", _("by edit date")),
]


SORT_CRITERIA_EXT = [
    ("name", _("by name")),
    ("city", _("by city")),
    ("subdivision", _("by subdivision")),
    ("created_at", _("by date added")),
    ("updated_at", _("by edit date")),
]


SORT_CRITERIA_COMPANIES = [
    ("name", _("by name")),
    ("city", _("by city")),
    ("subdivision", _("by subdivision")),
    ("created_at", _("by date added")),
    ("updated_at", _("by edit date")),
    ("recommended", _("by the number of recommendations")),
]


SORT_CRITERIA_PROJECTS = [
    ("name", _("by name")),
    ("city", "wg miasta"),
    ("subdivision", _("by city")),
    ("created_at", _("by date added")),
    ("updated_at", _("by edit date")),
    ("watched", _("by number of observations")),
]


ORDER_CRITERIA = [
    ("asc", _("ascending")),
    ("desc", _("descending")),
]


STATUS = [
    ("", "---"),
    ("in_progress", _("in progress")),
    ("completed", _("completed")),
]


COLORS = [
    ("", "---"),
    ("default", _("default")),
    ("success", _("green")),
    ("info", _("blue")),
    ("warning", _("orange")),
    ("danger", _("red")),
]


USER_ROLES = [
    ("default", _("default")),
    ("editor", _("editor")),
    ("admin", _("administrator")),
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


COMMENTS_FILTER = [
    ("", "---"),
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
    ("recommended-companies", _("Recommended companies")),
    ("watched-projects", _("Watched projects")),
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
]


# https://pl.wikipedia.org/wiki/Krajowy_Rejestr_S%C4%85dowy#Siedziba_i_obszary_w%C5%82a%C5%9Bciwo%C5%9Bci
COURTS = [
    ("", "---"),
    (
        "Białystok XII",
        "Sąd Rejonowy w Białymstoku, XII Wydział Gospodarczy KRS",
    ),
    (
        "Bielsko-Biała VIII",
        "Sąd Rejonowy w Bielsku-Białej, VIII Wydział Gospodarczy KRS",
    ),
    (
        "Bydgoszcz XIII",
        "Sąd Rejonowy w Bydgoszczy, XIII Wydział Gospodarczy KRS",
    ),
    (
        "Częstochowa XVII",
        "Sąd Rejonowy w Częstochowie, XVII Wydział Gospodarczy KRS",
    ),
    (
        "Gdańsk VII",
        "Sąd Rejonowy Gdańsk-Północ w Gdańsku, VII Wydział Gospodarczy KRS",
    ),
    (
        "Gdańsk VIII",
        "Sąd Rejonowy Gdańsk-Północ w Gdańsku, VIII Wydział Gospodarczy KRS",
    ),
    (
        "Gliwice X",
        "Sąd Rejonowy w Gliwicach, X Wydział Gospodarczy KRS",
    ),
    (
        "Katowice VIII",
        "Sąd Rejonowy Katowice-Wschód w Katowicach, VIII Wydział Gospodarczy KRS",
    ),
    (
        "Kielce X",
        "Sąd Rejonowy w Kielcach, X Wydział Gospodarczy KRS",
    ),
    (
        "Koszalin IX",
        "Sąd Rejonowy w Koszalinie, IX Wydział Gospodarczy KRS",
    ),
    (
        "Kraków XI",
        "Sąd Rejonowy dla Krakowa-Śródmieścia w Krakowie, XI Wydział Gospodarczy KRS",
    ),
    (
        "Kraków XII",
        "Sąd Rejonowy dla Krakowa-Śródmieścia w Krakowie, XII Wydział Gospodarczy KRS",
    ),
    (
        "Lublin VI",
        "Sąd Rejonowy Lublin-Wschód w Świdniku, VI Wydział Gospodarczy KRS",
    ),
    (
        "Łódź XX",
        "Sąd Rejonowy dla Łodzi-Śródmieścia w Łodzi, XX Wydział Gospodarczy KRS",
    ),
    (
        "Olsztyn VIII",
        "Sąd Rejonowy w Olsztynie, VIII Wydział Gospodarczy KRS",
    ),
    (
        "Opole VIII",
        "Sąd Rejonowy w Opolu",
    ),
    (
        "Poznań VIII",
        "Sąd Rejonowy Poznań-Nowe Miasto i Wilda w Poznaniu, VIII Wydział Gospodarczy KRS",
    ),
    (
        "Poznań IX",
        "Sąd Rejonowy Poznań-Nowe Miasto i Wilda w Poznaniu, IX Wydział Gospodarczy KRS",
    ),
    (
        "Rzeszów XII",
        "Sąd Rejonowy w Rzeszowie, XII Wydział Gospodarczy KRS",
    ),
    (
        "Szczecin XIII",
        "Sąd Rejonowy Szczecin-Centrum w Szczecinie, XIII Wydział Gospodarczy KRS",
    ),
    (
        "Toruń VII",
        "Sąd Rejonowy w Toruniu, VII Wydział Gospodarczy KRS",
    ),
    (
        "Warszawa XII",
        "Sąd Rejonowy dla m.st. Warszawy w Warszawie, XII Wydział Gospodarczy KRS",
    ),
    (
        "Warszawa XIII",
        "Sąd Rejonowy dla m.st. Warszawy w Warszawie, XIII Wydział Gospodarczy KRS",
    ),
    (
        "Warszawa XIV",
        "Sąd Rejonowy dla m.st. Warszawy w Warszawie, XIV Wydział Gospodarczy KRS",
    ),
    (
        "Wrocław VI",
        "Sąd Rejonowy dla Wrocławia-Fabrycznej we Wrocławiu, VI Wydział Gospodarczy KRS",
    ),
    (
        "Wrocław IX",
        "Sąd Rejonowy dla Wrocławia-Fabrycznej we Wrocławiu, IX Wydział Gospodarczy KRS",
    ),
    (
        "Zielona Góra VIII",
        "Sąd Rejonowy w Zielonej Górze, VIII Wydział Gospodarczy KRS",
    ),
]
