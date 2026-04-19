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


OBJECT_CATEGORIES = [
    ("", "---"),
    ("I", "Kategoria I – budynki mieszkalne jednorodzinne"),
    (
        "II",
        "Kategoria II – budynki służące gospodarce rolnej, jak: produkcyjne, gospodarcze, inwentarsko-składowe",
    ),
    (
        "III",
        "Kategoria III – inne niewielkie budynki, jak: domy letniskowe, budynki gospodarcze, garaże do dwóch stanowisk włącznie",
    ),
    (
        "IV",
        "Kategoria IV – elementy dróg publicznych i kolejowych dróg szynowych, jak: skrzyżowania i węzły, wjazdy, zjazdy, przejazdy, perony, rampy",
    ),
    (
        "V",
        "Kategoria V – obiekty sportu i rekreacji, jak: stadiony, amfiteatry, skocznie i wyciągi narciarskie, kolejki linowe, odkryte baseny, zjeżdżalnie",
    ),
    ("VI", "Kategoria VI – cmentarze"),
    ("VII", "Kategoria VII – obiekty melioracji wodnych"),
    ("VIII", "Kategoria VIII – inne budowle"),
    (
        "IX",
        "Kategoria IX – budynki kultury, nauki i oświaty, jak: teatry, opery, kina, muzea, biblioteki, domy kultury, ogniska artystyczne, galerie sztuki, stacje meteorologiczne, obserwatoria astronomiczne, budynki szkolne i przedszkolne, żłobki, placówki naukowo-badawcze, szkoły wyższe, laboratoria",
    ),
    (
        "X",
        "Kategoria X – budynki kultu religijnego, jak: kościoły, kaplice, klasztory, cerkwie, synagogi, meczety oraz domy pogrzebowe, krematoria",
    ),
    (
        "XI",
        "Kategoria XI – budynki służby zdrowia, opieki społecznej i socjalnej, jak: szpitale, sanatoria, hospicja, przychodnie, poradnie, stacje krwiodawstwa, lecznice weterynaryjne, domy pomocy i opieki społecznej, domy dziecka, domy rencisty, schroniska dla bezdomnych oraz hotele robotnicze",
    ),
    (
        "XII",
        "Kategoria XII – budynki administracji publicznej, budynki Sejmu, Senatu, Kancelarii Prezydenta, ministerstw i urzędów centralnych, terenowej administracji rządowej i samorządowej, sądów i trybunałów, więzień i domów poprawczych, zakładów dla nieletnich, zakładów karnych, aresztów śledczych oraz obiekty budowlane Sił Zbrojnych",
    ),
    ("XIII", "Kategoria XIII – pozostałe budynki mieszkalne"),
    (
        "XIV",
        "Kategoria XIV – budynki zakwaterowania turystycznego i rekreacyjnego, jak: hotele, motele, pensjonaty, domy wypoczynkowe, schroniska turystyczne",
    ),
    (
        "XV",
        "Kategoria XV – budynki sportu i rekreacji, jak: hale sportowe, widowiskowe, kryte baseny",
    ),
    ("XVI", "Kategoria XVI – budynki biurowe i konferencyjne"),
    (
        "XVII",
        "Kategoria XVII – budynki handlu, gastronomii i usług, jak: sklepy, centra handlowe, domy towarowe, hale targowe, restauracje, bary, kasyna, dyskoteki, warsztaty rzemieślnicze, stacje obsługi pojazdów, myjnie samochodowe, garaże powyżej dwóch stanowisk, budynki dworcowe",
    ),
    (
        "XVIII",
        "Kategoria XVIII – obiekty magazynowe, jak: budynki składowe, chłodnie, hangary, wiaty, a także budynki kolejowe, jak: nastawnie, podstacje trakcyjne, lokomotywownie, wagonownie, strażnice przejazdowe, myjnie taboru kolejowego",
    ),
    (
        "XIX",
        "Kategoria XIX – budynki przemysłowe, jak: budynki produkcyjne, służące energetyce, hale produkcyjne, warsztaty, wytwórnie betonu i asfaltu",
    ),
    ("XX", "Kategoria XX – stacje paliw"),
    (
        "XXI",
        "Kategoria XXI – zbiorniki przemysłowe, jak: silosy, zasobniki, zbiorniki na paliwa i gazy oraz inne produkty chemiczne",
    ),
    (
        "XXII",
        "Kategoria XXII – budowle i urządzenia morskie, jak: suche doki, nabrzeża, mola, falochrony, pochylnie, pirsy, pomosty, przystanie",
    ),
    (
        "XXIII",
        "Kategoria XXIII – budowle lotniskowe, jak: pasy startowe, drogi kołowania, płyty lotniskowe, lądowniki, drogi dojazdowe, place postojowe i manewrowe",
    ),
    (
        "XXIV",
        "Kategoria XXIV – obiekty gospodarki wodnej, jak: stawy rybne, ujęcia wód, budowle zrzutów wód i ścieków, kanały wodne, wały przeciwpowodziowe, pompownie, stacje uzdatniania wody, oczyszczalnie ścieków",
    ),
    (
        "XXV",
        "Kategoria XXV – drogi, w tym: autostrady, drogi ekspresowe, drogi krajowe, wojewódzkie, powiatowe i gminne, oraz kolejowe drogi szynowe",
    ),
    (
        "XXVI",
        "Kategoria XXVI – sieci uzbrojenia terenu, jak: linie elektroenergetyczne, telekomunikacyjne, gazowe, ciepłownicze, wodociągowe, kanalizacyjne oraz rurociągi przesyłowe",
    ),
    (
        "XXVII",
        "Kategoria XXVII – budowle hydrotechniczne piętrzące, upustowe i regulacyjne, jak: zapory, progi i stopnie wodne, jazy, bramy przeciwpowodziowe, śluzy wałowe, syfony, śluzy żeglowne, opaski i ostrogi brzegowe, rowy melioracyjne",
    ),
    (
        "XXVIII",
        "Kategoria XXVIII – obiekty mostowe, jak: mosty, wiadukty, estakady, kładki dla pieszych, tunele, przejścia podziemne",
    ),
    (
        "XXIX",
        "Kategoria XXIX – wolno stojące kominy, maszty, wieże, w tym wieże ciśnień, słupy, pylony, pomniki i inne podobne obiekty",
    ),
    (
        "XXX",
        "Kategoria XXX – obiekty służące do korzystania z zasobów wodnych, jak: ujęcia wód morskich i śródlądowych, budowle zrzutów wód i ścieków, pompownie, stacje strefowe, stacje uzdatniania wody, oczyszczalnie ścieków",
    ),
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
