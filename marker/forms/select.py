DROPDOWN_SORT = [
    ("name", "wg nazwy"),
    ("created_at", "wg daty dodania"),
    ("updated_at", "wg daty edycji"),
]


DROPDOWN_EXT_SORT = [
    ("name", "wg nazwy"),
    ("city", "wg miasta"),
    ("state", "wg województwa"),
    ("created_at", "wg daty dodania"),
    ("updated_at", "wg daty edycji"),
]


DROPDOWN_SORT_COMPANIES = [
    ("name", "wg nazwy"),
    ("city", "wg miasta"),
    ("state", "wg województwa"),
    ("created_at", "wg daty dodania"),
    ("updated_at", "wg daty edycji"),
    ("recommended", "wg rekomendacji"),
]


DROPDOWN_SORT_PROJECTS = [
    ("name", "wg nazwy"),
    ("city", "wg miasta"),
    ("state", "wg województwa"),
    ("created_at", "wg daty dodania"),
    ("updated_at", "wg daty edycji"),
    ("watched", "wg obserwacji"),
]


DROPDOWN_ORDER = [
    ("asc", "rosnąco"),
    ("desc", "malejąco"),
]


DROPDOWN_STATUS = [
    ("", "---"),
    ("in_progress", "w trakcie"),
    ("completed", "zakończone"),
]


COLORS = [
    ("", "---"),
    ("default", "domyślny"),
    ("success", "zielony"),
    ("info", "niebieski"),
    ("warning", "pomarańczowy"),
    ("danger", "czerwony"),
]


STATES = [
    ("", "---"),
    ("DS", "dolnośląskie"),
    ("KP", "kujawsko-pomorskie"),
    ("LU", "lubelskie"),
    ("LB", "lubuskie"),
    ("LD", "łódzkie"),
    ("MP", "małopolskie"),
    ("MA", "mazowieckie"),
    ("OP", "opolskie"),
    ("PK", "podkarpackie"),
    ("PD", "podlaskie"),
    ("PM", "pomorskie"),
    ("SL", "śląskie"),
    ("SW", "świętokrzyskie"),
    ("WM", "warmińsko-mazurskie"),
    ("WP", "wielkopolskie"),
    ("ZP", "zachodniopomorskie"),
]


# import pprint
# import pycountry
# countries = [(country.alpha_2, country.name) for country in pycountry.countries]
# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(countries)

COUNTRIES = [
    ("", "---"),
    ("AW", "Aruba"),
    ("AF", "Afghanistan"),
    ("AO", "Angola"),
    ("AI", "Anguilla"),
    ("AX", "Åland Islands"),
    ("AL", "Albania"),
    ("AD", "Andorra"),
    ("AE", "United Arab Emirates"),
    ("AR", "Argentina"),
    ("AM", "Armenia"),
    ("AS", "American Samoa"),
    ("AQ", "Antarctica"),
    ("TF", "French Southern Territories"),
    ("AG", "Antigua and Barbuda"),
    ("AU", "Australia"),
    ("AT", "Austria"),
    ("AZ", "Azerbaijan"),
    ("BI", "Burundi"),
    ("BE", "Belgium"),
    ("BJ", "Benin"),
    ("BQ", "Bonaire, Sint Eustatius and Saba"),
    ("BF", "Burkina Faso"),
    ("BD", "Bangladesh"),
    ("BG", "Bulgaria"),
    ("BH", "Bahrain"),
    ("BS", "Bahamas"),
    ("BA", "Bosnia and Herzegovina"),
    ("BL", "Saint Barthélemy"),
    ("BY", "Belarus"),
    ("BZ", "Belize"),
    ("BM", "Bermuda"),
    ("BO", "Bolivia, Plurinational State of"),
    ("BR", "Brazil"),
    ("BB", "Barbados"),
    ("BN", "Brunei Darussalam"),
    ("BT", "Bhutan"),
    ("BV", "Bouvet Island"),
    ("BW", "Botswana"),
    ("CF", "Central African Republic"),
    ("CA", "Canada"),
    ("CC", "Cocos (Keeling) Islands"),
    ("CH", "Switzerland"),
    ("CL", "Chile"),
    ("CN", "China"),
    ("CI", "Côte d'Ivoire"),
    ("CM", "Cameroon"),
    ("CD", "Congo, The Democratic Republic of the"),
    ("CG", "Congo"),
    ("CK", "Cook Islands"),
    ("CO", "Colombia"),
    ("KM", "Comoros"),
    ("CV", "Cabo Verde"),
    ("CR", "Costa Rica"),
    ("CU", "Cuba"),
    ("CW", "Curaçao"),
    ("CX", "Christmas Island"),
    ("KY", "Cayman Islands"),
    ("CY", "Cyprus"),
    ("CZ", "Czechia"),
    ("DE", "Germany"),
    ("DJ", "Djibouti"),
    ("DM", "Dominica"),
    ("DK", "Denmark"),
    ("DO", "Dominican Republic"),
    ("DZ", "Algeria"),
    ("EC", "Ecuador"),
    ("EG", "Egypt"),
    ("ER", "Eritrea"),
    ("EH", "Western Sahara"),
    ("ES", "Spain"),
    ("EE", "Estonia"),
    ("ET", "Ethiopia"),
    ("FI", "Finland"),
    ("FJ", "Fiji"),
    ("FK", "Falkland Islands (Malvinas)"),
    ("FR", "France"),
    ("FO", "Faroe Islands"),
    ("FM", "Micronesia, Federated States of"),
    ("GA", "Gabon"),
    ("GB", "United Kingdom"),
    ("GE", "Georgia"),
    ("GG", "Guernsey"),
    ("GH", "Ghana"),
    ("GI", "Gibraltar"),
    ("GN", "Guinea"),
    ("GP", "Guadeloupe"),
    ("GM", "Gambia"),
    ("GW", "Guinea-Bissau"),
    ("GQ", "Equatorial Guinea"),
    ("GR", "Greece"),
    ("GD", "Grenada"),
    ("GL", "Greenland"),
    ("GT", "Guatemala"),
    ("GF", "French Guiana"),
    ("GU", "Guam"),
    ("GY", "Guyana"),
    ("HK", "Hong Kong"),
    ("HM", "Heard Island and McDonald Islands"),
    ("HN", "Honduras"),
    ("HR", "Croatia"),
    ("HT", "Haiti"),
    ("HU", "Hungary"),
    ("ID", "Indonesia"),
    ("IM", "Isle of Man"),
    ("IN", "India"),
    ("IO", "British Indian Ocean Territory"),
    ("IE", "Ireland"),
    ("IR", "Iran, Islamic Republic of"),
    ("IQ", "Iraq"),
    ("IS", "Iceland"),
    ("IL", "Israel"),
    ("IT", "Italy"),
    ("JM", "Jamaica"),
    ("JE", "Jersey"),
    ("JO", "Jordan"),
    ("JP", "Japan"),
    ("KZ", "Kazakhstan"),
    ("KE", "Kenya"),
    ("KG", "Kyrgyzstan"),
    ("KH", "Cambodia"),
    ("KI", "Kiribati"),
    ("KN", "Saint Kitts and Nevis"),
    ("KR", "Korea, Republic of"),
    ("KW", "Kuwait"),
    ("LA", "Lao People's Democratic Republic"),
    ("LB", "Lebanon"),
    ("LR", "Liberia"),
    ("LY", "Libya"),
    ("LC", "Saint Lucia"),
    ("LI", "Liechtenstein"),
    ("LK", "Sri Lanka"),
    ("LS", "Lesotho"),
    ("LT", "Lithuania"),
    ("LU", "Luxembourg"),
    ("LV", "Latvia"),
    ("MO", "Macao"),
    ("MF", "Saint Martin (French part)"),
    ("MA", "Morocco"),
    ("MC", "Monaco"),
    ("MD", "Moldova, Republic of"),
    ("MG", "Madagascar"),
    ("MV", "Maldives"),
    ("MX", "Mexico"),
    ("MH", "Marshall Islands"),
    ("MK", "North Macedonia"),
    ("ML", "Mali"),
    ("MT", "Malta"),
    ("MM", "Myanmar"),
    ("ME", "Montenegro"),
    ("MN", "Mongolia"),
    ("MP", "Northern Mariana Islands"),
    ("MZ", "Mozambique"),
    ("MR", "Mauritania"),
    ("MS", "Montserrat"),
    ("MQ", "Martinique"),
    ("MU", "Mauritius"),
    ("MW", "Malawi"),
    ("MY", "Malaysia"),
    ("YT", "Mayotte"),
    ("NA", "Namibia"),
    ("NC", "New Caledonia"),
    ("NE", "Niger"),
    ("NF", "Norfolk Island"),
    ("NG", "Nigeria"),
    ("NI", "Nicaragua"),
    ("NU", "Niue"),
    ("NL", "Netherlands"),
    ("NO", "Norway"),
    ("NP", "Nepal"),
    ("NR", "Nauru"),
    ("NZ", "New Zealand"),
    ("OM", "Oman"),
    ("PK", "Pakistan"),
    ("PA", "Panama"),
    ("PN", "Pitcairn"),
    ("PE", "Peru"),
    ("PH", "Philippines"),
    ("PW", "Palau"),
    ("PG", "Papua New Guinea"),
    ("PL", "Poland"),
    ("PR", "Puerto Rico"),
    ("KP", "Korea, Democratic People's Republic of"),
    ("PT", "Portugal"),
    ("PY", "Paraguay"),
    ("PS", "Palestine, State of"),
    ("PF", "French Polynesia"),
    ("QA", "Qatar"),
    ("RE", "Réunion"),
    ("RO", "Romania"),
    ("RU", "Russian Federation"),
    ("RW", "Rwanda"),
    ("SA", "Saudi Arabia"),
    ("SD", "Sudan"),
    ("SN", "Senegal"),
    ("SG", "Singapore"),
    ("GS", "South Georgia and the South Sandwich Islands"),
    ("SH", "Saint Helena, Ascension and Tristan da Cunha"),
    ("SJ", "Svalbard and Jan Mayen"),
    ("SB", "Solomon Islands"),
    ("SL", "Sierra Leone"),
    ("SV", "El Salvador"),
    ("SM", "San Marino"),
    ("SO", "Somalia"),
    ("PM", "Saint Pierre and Miquelon"),
    ("RS", "Serbia"),
    ("SS", "South Sudan"),
    ("ST", "Sao Tome and Principe"),
    ("SR", "Suriname"),
    ("SK", "Slovakia"),
    ("SI", "Slovenia"),
    ("SE", "Sweden"),
    ("SZ", "Eswatini"),
    ("SX", "Sint Maarten (Dutch part)"),
    ("SC", "Seychelles"),
    ("SY", "Syrian Arab Republic"),
    ("TC", "Turks and Caicos Islands"),
    ("TD", "Chad"),
    ("TG", "Togo"),
    ("TH", "Thailand"),
    ("TJ", "Tajikistan"),
    ("TK", "Tokelau"),
    ("TM", "Turkmenistan"),
    ("TL", "Timor-Leste"),
    ("TO", "Tonga"),
    ("TT", "Trinidad and Tobago"),
    ("TN", "Tunisia"),
    ("TR", "Turkey"),
    ("TV", "Tuvalu"),
    ("TW", "Taiwan, Province of China"),
    ("TZ", "Tanzania, United Republic of"),
    ("UG", "Uganda"),
    ("UA", "Ukraine"),
    ("UM", "United States Minor Outlying Islands"),
    ("UY", "Uruguay"),
    ("US", "United States"),
    ("UZ", "Uzbekistan"),
    ("VA", "Holy See (Vatican City State)"),
    ("VC", "Saint Vincent and the Grenadines"),
    ("VE", "Venezuela, Bolivarian Republic of"),
    ("VG", "Virgin Islands, British"),
    ("VI", "Virgin Islands, U.S."),
    ("VN", "Viet Nam"),
    ("VU", "Vanuatu"),
    ("WF", "Wallis and Futuna"),
    ("WS", "Samoa"),
    ("YE", "Yemen"),
    ("ZA", "South Africa"),
    ("ZM", "Zambia"),
    ("ZW", "Zimbabwe"),
]


USER_ROLES = [
    ("", "---"),
    ("basic", "wyświetlanie"),
    ("editor", "edytowanie"),
    ("admin", "administrator"),
]


COMPANY_ROLES = [
    ("", "---"),
    ("purchaser", "Zamawiający"),  # Purchaser
    ("investor", "Inwestor"),  # Investor
    ("general_contractor", "Generalny Wykonawca"),  # General Contractor
    ("subcontractor", "Podwykonawca"),  # Subcontractor
]


RMS = [
    ("R", "Robocizna"),
    ("M", "Materiał"),
    ("S", "Sprzęt"),
]


CURRENCIES = [
    ("PLN", "PLN"),
    ("EUR", "EUR"),
    ("USD", "USD"),
]


# Lista jednostek z programu RODOS
UNITS = [
    ("", "---"),
    ("t", "tona"),
    ("szt.", "sztuka"),
    ("odc.", "odcinek"),
    ("mp", "metr przestrzenny"),
    ("m3", "metr sześcienny"),
    ("m2", "metr kwadratowy"),
    ("m", "metr"),
    ("kpl.", "komplet"),
    ("km", "kilometr"),
    ("kg", "kilogram"),
    ("ha", "hektar"),
    ("elem.", "element"),
    ("dm3", "decymetr sześcienny"),
    ("dm2", "decymetr kwadratowy"),
    ("dm", "decymetr"),
    ("cm2", "centrymetr kwadratowy"),
    ("cm", "centymetr"),
    ("ar", "ar"),
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


REPORTS = [
    ("companies-tags", "Najpopularniejsze tagi wśród firm"),
    ("projects-tags", "Najpopularniejsze tagi wśród projektów"),
    ("companies-states", "Województwa o największej liczbie firm"),
    ("companies-cities", "Miasta o największej liczbie firm"),
    ("companies-comments", "Najczęściej komentowane firmy"),
    ("projects-states", "Województwa o największej liczbie projektów"),
    ("projects-cities", "Miasta o największej liczbie projektów"),
    ("projects-comments", "Najczęściej komentowane projekty"),
    ("users-companies", "Aktywność użytkowników (dodane firmy)"),
    ("users-projects", "Aktywność użytkowników (dodane projekty)"),
    ("companies-projects", "Inwestorzy (liczba projektów)"),
    ("recommended-companies", "Rekomendowane firmy"),
    ("watched-projects", "Obserwowane projekty"),
]


STAGES = [
    ("", "---"),
    ("tender", "Przetarg"),
    ("construction", "Realizacja"),
]


PROJECT_DELIVERY_METHODS = [
    ("", "---"),
    ("design-build", "Projektuj i buduj"),
    ("build", "Buduj"),
]


COMMENTS_FILTER = [
    ("", "---"),
    ("C", "Firmy"),
    ("P", "Projekty"),
]
