import os

from sqlalchemy import select

from marker import models


def _login_as_editor(testapp, username, password):
    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = username
    form["password"] = password
    form.submit(status=303)


def _assert_category_select_has_default_all(page_text):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(page_text, "html.parser")
    category_select = soup.find("select", {"name": "category"})
    assert category_select is not None

    options = category_select.find_all("option")
    option_map = {
        option.get("value", ""): option.get_text(strip=True) for option in options
    }

    selected_value = None
    for option in options:
        if option.has_attr("selected"):
            selected_value = option.get("value", "")
            break

    if selected_value is None and options:
        selected_value = options[0].get("value", "")

    assert option_map.get("") == "All"
    assert option_map.get("companies") == "Companies"
    assert option_map.get("projects") == "Projects"
    assert selected_value == ""


def _extract_hx_csrf_token(page_text):
    import json

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(page_text, "html.parser")
    select_all_checkbox = soup.find("input", class_="marker-select-all")
    assert select_all_checkbox is not None

    hx_headers = select_all_checkbox.get("hx-headers")
    assert hx_headers is not None
    if not isinstance(hx_headers, str):
        hx_headers = str(hx_headers)

    return json.loads(hx_headers)["X-CSRF-Token"]


def _assert_text_order(page_text, values):
    positions = [page_text.index(value) for value in values]
    assert positions == sorted(positions)


def _extract_sort_values_from_dropdown(page_text):
    from urllib.parse import parse_qs, urlparse

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(page_text, "html.parser")
    sort_values = []
    for link in soup.select('a.dropdown-item[href*="sort="]'):
        href = link.get("href")
        if not isinstance(href, str) or not href:
            continue
        sort_values.extend(parse_qs(urlparse(href).query).get("sort", []))
    return sort_values


def _extract_selected_sort_value(page_text):
    from urllib.parse import parse_qs, urlparse

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(page_text, "html.parser")
    for link in soup.select('a.dropdown-item[href*="sort="]'):
        if link.find("strong") is None:
            continue
        href = link.get("href")
        if not isinstance(href, str) or not href:
            continue
        sort_values = parse_qs(urlparse(href).query).get("sort", [])
        if sort_values:
            return sort_values[0]
    return None


def _extract_info_badge_values(page_text):
    import re

    return [
        int(value)
        for value in re.findall(
            r'class="badge text-bg-info"[^>]*>\s*(\d+)\s*</span>',
            page_text,
            re.S,
        )
    ]


def _set_cookie_headers(response):
    return [value for key, value in response.headerlist if key.lower() == "set-cookie"]


def test_my_view_success(testapp, dbsession):
    model = models.user.User(
        name="admin",
        password="admin",
        fullname="Jan Kowalski",
        email="jan.kowalski@example.com",
        role="admin",
    )
    dbsession.add(model)
    dbsession.flush()

    res = testapp.get("/", status=200)
    assert res.body


def test_tag_search_is_case_insensitive_in_project_and_company_lists(
    testapp, dbsession
):
    import datetime

    user = models.user.User(
        name="case-search-user",
        password="admin",
        fullname="Case Search User",
        email="case.search.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    company = models.company.Company(
        name="Case Search Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company.created_by = user

    project = models.project.Project(
        name="Case Search Project",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="",
        website="",
        color="",
        deadline=datetime.datetime.now(),
        stage="",
        delivery_method="",
    )
    project.created_by = user

    tag = models.tag.Tag(name="MiXeDcAsEtAg")
    tag.created_by = user
    tag.companies.append(company)
    tag.projects.append(project)

    dbsession.add_all([company, project, tag])
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "case-search-user"
    form["password"] = "admin"
    form.submit(status=303)

    company_res = testapp.get("/company", params={"tag": "mixedcasetag"}, status=200)
    assert "Case Search Company" in company_res.text

    project_res = testapp.get("/project", params={"tag": "MIXEDCASETAG"}, status=200)
    assert "Case Search Project" in project_res.text


def test_contact_tag_search_results_support_filters_and_sorting(testapp, dbsession):
    import datetime

    user = models.user.User(
        name="contact-tags-user",
        password="admin",
        fullname="Contact Tags User",
        email="contact.tags.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    company_a = models.company.Company(
        name="Alpha Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="DE",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company_a.created_by = user

    company_b = models.company.Company(
        name="Zulu Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company_b.created_by = user

    project = models.project.Project(
        name="Tagged Project",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        deadline=datetime.datetime.now(),
        stage="",
        delivery_method="",
    )
    project.created_by = user

    tag = models.tag.Tag(name="pipeline")
    tag.created_by = user
    tag.companies.extend([company_a, company_b])
    tag.projects.append(project)

    contact_a = models.contact.Contact(
        name="Alpha Contact",
        role="",
        phone="",
        email="",
        color="",
    )
    contact_a.company = company_a
    contact_a.created_by = user

    contact_b = models.contact.Contact(
        name="Zulu Contact",
        role="",
        phone="",
        email="",
        color="",
    )
    contact_b.company = company_b
    contact_b.created_by = user

    contact_project = models.contact.Contact(
        name="Project Contact",
        role="",
        phone="",
        email="",
        color="",
    )
    contact_project.project = project
    contact_project.created_by = user

    dbsession.add_all(
        [
            company_a,
            company_b,
            project,
            tag,
            contact_a,
            contact_b,
            contact_project,
        ]
    )
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "contact-tags-user"
    form["password"] = "admin"
    form.submit(status=303)

    res_sorted = testapp.get(
        "/search/tags/results",
        params={
            "target": "contacts",
            "tag": "pipeline",
            "sort": "name",
            "order": "asc",
        },
        status=200,
    )
    _assert_text_order(
        res_sorted.text,
        ["Alpha Contact", "Project Contact", "Zulu Contact"],
    )

    res_filtered = testapp.get(
        "/search/tags/results",
        params={
            "target": "contacts",
            "tag": "pipeline",
            "category": "companies",
            "country": "DE",
        },
        status=200,
    )
    assert "Alpha Contact" in res_filtered.text
    assert "Zulu Contact" not in res_filtered.text
    assert "Project Contact" not in res_filtered.text

    legacy_route_res = testapp.get(
        "/contact/search/tags/results",
        params={"tag": "pipeline", "sort": "name", "order": "asc"},
        status=303,
    )


def test_search_tags_handles_polish_letters_in_tag_name(testapp, dbsession):
    import datetime

    user = models.user.User(
        name="polish-tag-search-user",
        password="admin",
        fullname="Polish Tag Search User",
        email="polish.tag.search.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    company = models.company.Company(
        name="Polish Tag Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company.created_by = user

    project = models.project.Project(
        name="Polish Tag Project",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        deadline=datetime.datetime.now(),
        stage="",
        delivery_method="",
    )
    project.created_by = user

    contact_company = models.contact.Contact(
        name="Polish Company Contact",
        role="",
        phone="",
        email="",
        color="",
    )
    contact_company.company = company
    contact_company.created_by = user

    contact_project = models.contact.Contact(
        name="Polish Project Contact",
        role="",
        phone="",
        email="",
        color="",
    )
    contact_project.project = project
    contact_project.created_by = user

    tag = models.tag.Tag(name="Ślusarka aluminiowa")
    tag.created_by = user
    tag.companies.append(company)
    tag.projects.append(project)

    dbsession.add_all([company, project, contact_company, contact_project, tag])
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "polish-tag-search-user"
    form["password"] = "admin"
    form.submit(status=303)

    companies_redirect = testapp.get(
        "/search/tags/results",
        params={"target": "companies", "tag": "ślusarka aluminiowa"},
        status=303,
    )
    companies_page = companies_redirect.follow(status=200)
    assert "Polish Tag Company" in companies_page.text

    projects_redirect = testapp.get(
        "/search/tags/results",
        params={"target": "projects", "tag": "ślusarka aluminiowa"},
        status=303,
    )
    projects_page = projects_redirect.follow(status=200)
    assert "Polish Tag Project" in projects_page.text

    contacts_page = testapp.get(
        "/search/tags/results",
        params={"target": "contacts", "tag": "ślusarka aluminiowa"},
        status=200,
    )
    assert "Polish Company Contact" in contacts_page.text
    assert "Polish Project Contact" in contacts_page.text


def test_tag_search_redirects_and_supports_contacts_view_for_company_and_project(
    testapp, dbsession
):
    import datetime

    user = models.user.User(
        name="tag-search-switch-user",
        password="admin",
        fullname="Tag Search Switch User",
        email="tag.search.switch.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    company = models.company.Company(
        name="Switch Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company.created_by = user

    project = models.project.Project(
        name="Switch Project",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        deadline=datetime.datetime.now(),
        stage="",
        delivery_method="",
    )
    project.created_by = user

    company_contact = models.contact.Contact(
        name="Company Switch Contact",
        role="",
        phone="",
        email="",
        color="",
    )
    company_contact.company = company
    company_contact.created_by = user

    project_contact = models.contact.Contact(
        name="Project Switch Contact",
        role="",
        phone="",
        email="",
        color="",
    )
    project_contact.project = project
    project_contact.created_by = user

    tag = models.tag.Tag(name="switch-tag")
    tag.created_by = user
    tag.companies.append(company)
    tag.projects.append(project)

    dbsession.add_all([company, project, company_contact, project_contact, tag])
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "tag-search-switch-user"
    form["password"] = "admin"
    form.submit(status=303)

    company_redirect = testapp.get(
        "/search/tags/results",
        params={"target": "companies", "tag": "switch-tag"},
        status=303,
    )
    assert "/company" in company_redirect.location

    project_redirect = testapp.get(
        "/search/tags/results",
        params={"target": "projects", "tag": "switch-tag"},
        status=303,
    )
    assert "/project" in project_redirect.location

    company_contacts_view = testapp.get(
        "/company",
        params={"tag": "switch-tag", "view": "contacts"},
        status=200,
    )
    assert "Company Switch Contact" in company_contacts_view.text
    assert "Switch Company" in company_contacts_view.text

    project_contacts_view = testapp.get(
        "/project",
        params={"tag": "switch-tag", "view": "contacts"},
        status=200,
    )
    assert "Project Switch Contact" in project_contacts_view.text
    assert "Switch Project" in project_contacts_view.text


def test_contact_views_do_not_allow_sorting_by_color(testapp, dbsession):
    user = models.user.User(
        name="contact-color-sort-user",
        password="admin",
        fullname="Contact Color Sort User",
        email="contact.color.sort.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    company = models.company.Company(
        name="Color Sort Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company.created_by = user

    tag = models.tag.Tag(name="pipeline")
    tag.created_by = user
    tag.companies.append(company)

    contact = models.contact.Contact(
        name="Color Sort Contact",
        role="",
        phone="",
        email="",
        color="warning",
    )
    contact.created_by = user
    contact.company = company

    dbsession.add_all([company, tag, contact])
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "contact-color-sort-user"
    form["password"] = "admin"
    form.submit(status=303)

    all_contacts = testapp.get("/contact", status=200)
    assert "color" not in _extract_sort_values_from_dropdown(all_contacts.text)

    all_contacts_with_color_sort = testapp.get(
        "/contact", params={"sort": "color", "order": "asc"}, status=200
    )
    assert "color" not in _extract_sort_values_from_dropdown(
        all_contacts_with_color_sort.text
    )
    assert (
        _extract_selected_sort_value(all_contacts_with_color_sort.text) == "created_at"
    )

    tags_results_with_color_sort = testapp.get(
        "/contact/search/tags/results",
        params={"tag": "pipeline", "sort": "color", "order": "asc"},
        status=303,
    )


def test_name_search_is_case_insensitive_with_polish_letters(testapp, dbsession):
    import datetime

    user = models.user.User(
        name="lodz-search-user",
        password="admin",
        fullname="Lodz Search User",
        email="lodz.search.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    company = models.company.Company(
        name="ALFA ŁÓDŹ",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company.created_by = user

    project = models.project.Project(
        name="BETA ŁÓDŹ",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="",
        website="",
        color="",
        deadline=datetime.datetime.now(),
        stage="",
        delivery_method="",
    )
    project.created_by = user

    dbsession.add_all([company, project])
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "lodz-search-user"
    form["password"] = "admin"
    form.submit(status=303)

    company_res = testapp.get("/company", params={"name": "łódź"}, status=200)
    assert "ALFA ŁÓDŹ" in company_res.text

    project_res = testapp.get("/project", params={"name": "łódź"}, status=200)
    assert "BETA ŁÓDŹ" in project_res.text


def test_city_search_is_case_insensitive_with_polish_letters(testapp, dbsession):
    import datetime

    user = models.user.User(
        name="city-search-user",
        password="admin",
        fullname="City Search User",
        email="city.search.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    company = models.company.Company(
        name="City Search Company",
        street="",
        postcode="",
        city="ŁÓDŹ",
        subdivision="",
        country="",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company.created_by = user

    project = models.project.Project(
        name="City Search Project",
        street="",
        postcode="",
        city="ŁÓDŹ",
        subdivision="",
        country="",
        website="",
        color="",
        deadline=datetime.datetime.now(),
        stage="",
        delivery_method="",
    )
    project.created_by = user

    dbsession.add_all([company, project])
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "city-search-user"
    form["password"] = "admin"
    form.submit(status=303)

    company_res = testapp.get("/company", params={"city": "łódź"}, status=200)
    assert "City Search Company" in company_res.text

    project_res = testapp.get("/project", params={"city": "łódź"}, status=200)
    assert "City Search Project" in project_res.text


def test_desc_sort_uses_polish_alphabetical_order_for_names(testapp, dbsession):
    import datetime

    user = models.user.User(
        name="sort-search-user",
        password="admin",
        fullname="Sort Search User",
        email="sort.search.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    company_names = [
        "Sort Wacek Company",
        "Sort Zygmunt Company",
        "Sort Śnieg Company",
        "Sort Łukasz Company",
        "Sort Żaba Company",
    ]
    project_names = [
        "Sort Wacek Project",
        "Sort Zygmunt Project",
        "Sort Śnieg Project",
        "Sort Łukasz Project",
        "Sort Żaba Project",
    ]

    for company_name in company_names:
        company = models.company.Company(
            name=company_name,
            street="",
            postcode="",
            city="",
            subdivision="",
            country="",
            website="",
            color="",
            NIP="",
            REGON="",
            KRS="",
        )
        company.created_by = user
        dbsession.add(company)

    for project_name in project_names:
        project = models.project.Project(
            name=project_name,
            street="",
            postcode="",
            city="",
            subdivision="",
            country="",
            website="",
            color="",
            deadline=datetime.datetime.now(),
            stage="",
            delivery_method="",
        )
        project.created_by = user
        dbsession.add(project)

    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "sort-search-user"
    form["password"] = "admin"
    form.submit(status=303)

    company_res = testapp.get(
        "/company", params={"sort": "name", "order": "desc"}, status=200
    )
    _assert_text_order(
        company_res.text,
        [
            "Sort Żaba Company",
            "Sort Zygmunt Company",
            "Sort Wacek Company",
            "Sort Śnieg Company",
            "Sort Łukasz Company",
        ],
    )

    project_res = testapp.get(
        "/project", params={"sort": "name", "order": "desc"}, status=200
    )
    _assert_text_order(
        project_res.text,
        [
            "Sort Żaba Project",
            "Sort Zygmunt Project",
            "Sort Wacek Project",
            "Sort Śnieg Project",
            "Sort Łukasz Project",
        ],
    )


def test_company_similar_defaults_to_shared_tags_sort_with_badges(testapp, dbsession):
    user = models.user.User(
        name="company-similar-sort-user",
        password="admin",
        fullname="Company Similar Sort User",
        email="company.similar.sort.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    base_company = models.company.Company(
        name="Base Similar Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    base_company.created_by = user

    most_similar = models.company.Company(
        name="Zulu Similar Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    most_similar.created_by = user

    medium_similar = models.company.Company(
        name="Alpha Similar Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    medium_similar.created_by = user

    least_similar = models.company.Company(
        name="Bravo Similar Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    least_similar.created_by = user

    unrelated_company = models.company.Company(
        name="Unrelated Similar Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    unrelated_company.created_by = user

    tag1 = models.tag.Tag(name="similar-company-tag-1")
    tag2 = models.tag.Tag(name="similar-company-tag-2")
    tag3 = models.tag.Tag(name="similar-company-tag-3")
    unrelated_tag = models.tag.Tag(name="similar-company-tag-unrelated")
    for tag in [tag1, tag2, tag3, unrelated_tag]:
        tag.created_by = user

    base_company.tags.extend([tag1, tag2, tag3])
    most_similar.tags.extend([tag1, tag2, tag3])
    medium_similar.tags.extend([tag1, tag2])
    least_similar.tags.extend([tag1])
    unrelated_company.tags.extend([unrelated_tag])

    dbsession.add_all(
        [
            base_company,
            most_similar,
            medium_similar,
            least_similar,
            unrelated_company,
            tag1,
            tag2,
            tag3,
            unrelated_tag,
        ]
    )
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "company-similar-sort-user"
    form["password"] = "admin"
    form.submit(status=303)

    similar_url = f"/company/{base_company.id}/{base_company.slug}/similar"
    res_default = testapp.get(similar_url, status=200)

    assert _extract_selected_sort_value(res_default.text) == "shared_tags"
    _assert_text_order(
        res_default.text,
        [
            "Zulu Similar Company",
            "Alpha Similar Company",
            "Bravo Similar Company",
        ],
    )

    assert _extract_info_badge_values(res_default.text) == [3, 2, 1]
    assert 'data-bs-toggle="popover"' in res_default.text
    assert (
        'data-bs-content="similar-company-tag-1, similar-company-tag-2, '
        'similar-company-tag-3"' in res_default.text
    )
    assert (
        'data-bs-content="similar-company-tag-1, similar-company-tag-2"'
        in res_default.text
    )
    assert 'data-bs-content="similar-company-tag-1"' in res_default.text

    sort_values = set(_extract_sort_values_from_dropdown(res_default.text))
    assert {
        "shared_tags",
        "name",
        "city",
        "subdivision",
        "country",
        "created_at",
        "updated_at",
        "stars",
        "comments",
    }.issubset(sort_values)

    res_name_asc = testapp.get(
        similar_url,
        params={"sort": "name", "order": "asc"},
        status=200,
    )
    _assert_text_order(
        res_name_asc.text,
        [
            "Alpha Similar Company",
            "Bravo Similar Company",
            "Zulu Similar Company",
        ],
    )


def test_project_similar_defaults_to_shared_tags_sort_with_badges(testapp, dbsession):
    import datetime

    user = models.user.User(
        name="project-similar-sort-user",
        password="admin",
        fullname="Project Similar Sort User",
        email="project.similar.sort.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    now = datetime.datetime.now()

    base_project = models.project.Project(
        name="Base Similar Project",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        deadline=now,
        stage="",
        delivery_method="",
    )
    base_project.created_by = user

    most_similar = models.project.Project(
        name="Zulu Similar Project",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        deadline=now,
        stage="",
        delivery_method="",
    )
    most_similar.created_by = user

    medium_similar = models.project.Project(
        name="Alpha Similar Project",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        deadline=now,
        stage="",
        delivery_method="",
    )
    medium_similar.created_by = user

    least_similar = models.project.Project(
        name="Bravo Similar Project",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        deadline=now,
        stage="",
        delivery_method="",
    )
    least_similar.created_by = user

    unrelated_project = models.project.Project(
        name="Unrelated Similar Project",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        deadline=now,
        stage="",
        delivery_method="",
    )
    unrelated_project.created_by = user

    tag1 = models.tag.Tag(name="similar-project-tag-1")
    tag2 = models.tag.Tag(name="similar-project-tag-2")
    tag3 = models.tag.Tag(name="similar-project-tag-3")
    unrelated_tag = models.tag.Tag(name="similar-project-tag-unrelated")
    for tag in [tag1, tag2, tag3, unrelated_tag]:
        tag.created_by = user

    base_project.tags.extend([tag1, tag2, tag3])
    most_similar.tags.extend([tag1, tag2, tag3])
    medium_similar.tags.extend([tag1, tag2])
    least_similar.tags.extend([tag1])
    unrelated_project.tags.extend([unrelated_tag])

    dbsession.add_all(
        [
            base_project,
            most_similar,
            medium_similar,
            least_similar,
            unrelated_project,
            tag1,
            tag2,
            tag3,
            unrelated_tag,
        ]
    )
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "project-similar-sort-user"
    form["password"] = "admin"
    form.submit(status=303)

    similar_url = f"/project/{base_project.id}/{base_project.slug}/similar"
    res_default = testapp.get(similar_url, status=200)

    assert _extract_selected_sort_value(res_default.text) == "shared_tags"
    _assert_text_order(
        res_default.text,
        [
            "Zulu Similar Project",
            "Alpha Similar Project",
            "Bravo Similar Project",
        ],
    )

    assert _extract_info_badge_values(res_default.text) == [3, 2, 1]
    assert 'data-bs-toggle="popover"' in res_default.text
    assert (
        'data-bs-content="similar-project-tag-1, similar-project-tag-2, '
        'similar-project-tag-3"' in res_default.text
    )
    assert (
        'data-bs-content="similar-project-tag-1, similar-project-tag-2"'
        in res_default.text
    )
    assert 'data-bs-content="similar-project-tag-1"' in res_default.text

    sort_values = set(_extract_sort_values_from_dropdown(res_default.text))
    assert {
        "shared_tags",
        "name",
        "city",
        "subdivision",
        "country",
        "created_at",
        "updated_at",
        "stars",
        "comments",
    }.issubset(sort_values)

    res_name_asc = testapp.get(
        similar_url,
        params={"sort": "name", "order": "asc"},
        status=200,
    )
    _assert_text_order(
        res_name_asc.text,
        [
            "Alpha Similar Project",
            "Bravo Similar Project",
            "Zulu Similar Project",
        ],
    )


def test_contractors_view_default_sort_and_multiselect_tag_and_role_filter(
    testapp, dbsession
):
    import datetime

    user = models.user.User(
        name="contractor-view-user",
        password="admin",
        fullname="Contractor View User",
        email="contractor.view.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    company_alpha = models.company.Company(
        name="Contractor Alpha Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company_alpha.created_by = user

    company_beta = models.company.Company(
        name="Contractor Beta Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company_beta.created_by = user

    company_gamma = models.company.Company(
        name="Contractor Gamma Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company_gamma.created_by = user

    now = datetime.datetime.now()
    project_one = models.project.Project(
        name="Contractor Project One",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        deadline=now,
        stage="",
        delivery_method="",
    )
    project_one.created_by = user

    project_two = models.project.Project(
        name="Contractor Project Two",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        deadline=now,
        stage="",
        delivery_method="",
    )
    project_two.created_by = user

    project_three = models.project.Project(
        name="Contractor Project Three",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        deadline=now,
        stage="",
        delivery_method="",
    )
    project_three.created_by = user

    company_tag_steel = models.tag.Tag(name="contractor-company-steel")
    company_tag_steel.created_by = user
    company_beta.tags.append(company_tag_steel)

    company_tag_concrete = models.tag.Tag(name="contractor-company-concrete")
    company_tag_concrete.created_by = user
    company_alpha.tags.append(company_tag_concrete)

    company_tag_electrical = models.tag.Tag(name="contractor-company-electrical")
    company_tag_electrical.created_by = user
    company_gamma.tags.append(company_tag_electrical)

    project_tag_bridge = models.tag.Tag(name="contractor-project-bridge")
    project_tag_bridge.created_by = user
    project_one.tags.append(project_tag_bridge)

    project_tag_road = models.tag.Tag(name="contractor-project-road")
    project_tag_road.created_by = user
    project_two.tags.append(project_tag_road)

    project_tag_tunnel = models.tag.Tag(name="contractor-project-tunnel")
    project_tag_tunnel.created_by = user
    project_three.tags.append(project_tag_tunnel)

    activity_alpha_1 = models.Activity(
        company=company_alpha,
        project=project_one,
        stage="",
        role="designer",
    )
    activity_alpha_2 = models.Activity(
        company=company_alpha,
        project=project_two,
        stage="",
        role="designer",
    )
    activity_beta_1 = models.Activity(
        company=company_beta,
        project=project_one,
        stage="",
        role="supplier",
    )
    activity_gamma_1 = models.Activity(
        company=company_gamma,
        project=project_one,
        stage="",
        role="subcontractor",
    )
    activity_gamma_2 = models.Activity(
        company=company_gamma,
        project=project_two,
        stage="",
        role="subcontractor",
    )
    activity_gamma_3 = models.Activity(
        company=company_gamma,
        project=project_three,
        stage="",
        role="investor",
    )

    dbsession.add_all(
        [
            company_alpha,
            company_beta,
            company_gamma,
            project_one,
            project_two,
            project_three,
            company_tag_steel,
            company_tag_concrete,
            company_tag_electrical,
            project_tag_bridge,
            project_tag_road,
            project_tag_tunnel,
            activity_alpha_1,
            activity_alpha_2,
            activity_beta_1,
            activity_gamma_1,
            activity_gamma_2,
            activity_gamma_3,
        ]
    )
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "contractor-view-user"
    form["password"] = "admin"
    form.submit(status=303)

    res_default = testapp.get("/contractor", status=200)

    sort_values = set(_extract_sort_values_from_dropdown(res_default.text))
    assert {
        "name",
        "city",
        "subdivision",
        "country",
        "created_at",
        "updated_at",
        "stars",
        "comments",
    }.issubset(sort_values)

    res_name_asc = testapp.get(
        "/contractor",
        params={"sort": "name", "order": "asc"},
        status=200,
    )
    _assert_text_order(
        res_name_asc.text,
        [
            "Contractor Alpha Company",
            "Contractor Beta Company",
            "Contractor Gamma Company",
        ],
    )

    assert "<th>Company</th>" in res_default.text
    assert "<th>City</th>" in res_default.text
    assert "<th>Projects</th>" in res_default.text
    assert "<th>Stars</th>" in res_default.text
    assert "<th>Comments</th>" in res_default.text
    assert "<th>Action</th>" in res_default.text

    assert 'option value="contractor-company-steel"' in res_default.text
    assert 'option value="contractor-company-concrete"' in res_default.text
    assert 'option value="contractor-company-electrical"' in res_default.text
    assert 'option value="contractor-project-bridge"' not in res_default.text
    assert 'option value="contractor-project-road"' not in res_default.text
    assert 'option value="contractor-project-tunnel"' not in res_default.text

    assert 'option value="designer"' in res_default.text
    assert 'option value="supplier"' in res_default.text
    assert 'option value="investor"' in res_default.text

    res_role_filter = testapp.get(
        "/contractor",
        params=[("role", "designer")],
        status=200,
    )
    assert "Contractor Alpha Company" in res_role_filter.text
    assert "Contractor Beta Company" not in res_role_filter.text
    assert "Contractor Gamma Company" not in res_role_filter.text

    res_multi_role_filter = testapp.get(
        "/contractor",
        params=[("role", "supplier"), ("role", "investor")],
        status=200,
    )
    assert "Contractor Beta Company" in res_multi_role_filter.text
    assert "Contractor Gamma Company" in res_multi_role_filter.text
    assert "Contractor Alpha Company" not in res_multi_role_filter.text

    res_company_tag_filter = testapp.get(
        "/contractor",
        params=[("tag", "contractor-company-steel")],
        status=200,
    )
    assert "Contractor Beta Company" in res_company_tag_filter.text
    assert "Contractor Alpha Company" not in res_company_tag_filter.text
    assert "Contractor Gamma Company" not in res_company_tag_filter.text

    res_project_tag_filter = testapp.get(
        "/contractor",
        params=[("tag", "contractor-project-tunnel")],
        status=200,
    )
    assert "Contractor Gamma Company" not in res_project_tag_filter.text
    assert "Contractor Alpha Company" not in res_project_tag_filter.text
    assert "Contractor Beta Company" not in res_project_tag_filter.text

    res_multi_tag_filter = testapp.get(
        "/contractor",
        params=[
            ("tag", "contractor-company-steel"),
            ("tag", "contractor-company-concrete"),
        ],
        status=200,
    )
    assert "Contractor Beta Company" in res_multi_tag_filter.text
    assert "Contractor Alpha Company" in res_multi_tag_filter.text
    assert "Contractor Gamma Company" not in res_multi_tag_filter.text

    res_tag_and_role_filter = testapp.get(
        "/contractor",
        params=[("tag", "contractor-company-steel"), ("role", "supplier")],
        status=200,
    )
    assert "Contractor Beta Company" in res_tag_and_role_filter.text
    assert "Contractor Alpha Company" not in res_tag_and_role_filter.text
    assert "Contractor Gamma Company" not in res_tag_and_role_filter.text


def test_notfound(testapp):
    res = testapp.get("/badurl", status=404)
    assert res.status_code == 404


def test_login_redirect_rejects_external_next_and_allows_local_path(testapp, dbsession):
    user = models.user.User(
        name="login-redirect-user",
        password="admin",
        fullname="Login Redirect User",
        email="login.redirect.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    login_page = testapp.get(
        "/login",
        params={"next": "https://evil.example/phishing"},
        status=200,
    )
    form = login_page.forms[0]
    form["username"] = "login-redirect-user"
    form["password"] = "admin"
    response_external = form.submit(status=303)
    assert response_external.headers["Location"] == "http://example.com/"

    testapp.reset()

    login_page = testapp.get("/login", params={"next": "/project"}, status=200)
    form = login_page.forms[0]
    form["username"] = "login-redirect-user"
    form["password"] = "admin"
    response_local = form.submit(status=303)
    assert response_local.headers["Location"] == "http://example.com/project"


def test_login_sets_httponly_and_samesite_cookies(testapp, dbsession):
    user = models.user.User(
        name="cookie-security-user",
        password="admin",
        fullname="Cookie Security User",
        email="cookie.security.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "cookie-security-user"
    form["password"] = "admin"
    response = form.submit(status=303)

    cookies = _set_cookie_headers(response)
    auth_cookies = [cookie for cookie in cookies if cookie.startswith("auth_tkt=")]
    csrf_cookies = [cookie for cookie in cookies if cookie.startswith("csrf_token=")]
    session_cookies = [cookie for cookie in cookies if cookie.startswith("session=")]

    assert auth_cookies
    assert csrf_cookies
    assert session_cookies

    for cookie in auth_cookies + csrf_cookies + session_cookies:
        assert "HttpOnly" in cookie
        assert "SameSite=Lax" in cookie


def test_set_locale_rejects_external_referrer(testapp):
    response = testapp.get(
        "/locale/pl",
        headers={"Referer": "https://evil.example/steal"},
        status=302,
    )
    assert response.headers["Location"] == "http://example.com/"

    cookies = _set_cookie_headers(response)
    locale_cookies = [cookie for cookie in cookies if cookie.startswith("_LOCALE_=")]
    assert locale_cookies
    assert "HttpOnly" in locale_cookies[0]
    assert "SameSite=Lax" in locale_cookies[0]


def test_comment_markdown_sanitizes_dangerous_html(testapp, dbsession):
    user = models.user.User(
        name="comment-sanitize-user",
        password="admin",
        fullname="Comment Sanitize User",
        email="comment.sanitize.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    company = models.company.Company(
        name="Comment Sanitizer Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company.created_by = user

    comment = models.comment.Comment(
        "**Safe** <script>alert(1)</script> "
        "<img src=x onerror=alert(2)> "
        "[malicious](javascript:alert(3))"
    )
    comment.created_by = user
    comment.company = company

    dbsession.add_all([company, comment])
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "comment-sanitize-user"
    form["password"] = "admin"
    form.submit(status=303)

    comments_page = testapp.get("/comment", status=200)

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(comments_page.text, "html.parser")
    comment_bodies = [
        body.decode_contents().lower() for body in soup.select(".card .card-body")
    ]

    sanitized_body = next(
        (body for body in comment_bodies if "<strong>safe</strong>" in body),
        "",
    )

    assert sanitized_body
    assert "<script" not in sanitized_body
    assert "onerror=" not in sanitized_body
    assert "javascript:alert(3)" not in sanitized_body


def test_plus_shortcut_script_and_single_button(testapp, dbsession):
    """Pages that render exactly one green "plus-lg" button should have the
    keyboard-shortcut helper available and the icon count should be one.

    We create a minimal project and then request its comments view, which is
    known to render a single plus button for adding a comment.  The layout
    template injects the JavaScript snippet for handling ``+``/``Insert``
    shortcuts, so we simply verify the script is present and that the
    rendered HTML only contains one matching icon.  The script itself will
    apply the accesskey at runtime in a real browser.
    """
    import datetime

    # create an admin user just so we have someone in the database;
    # authentication is not required to view the comments page, but
    # having a user mirrors realistic state
    user = models.user.User(
        name="admin",
        password="admin",
        fullname="Admin User",
        email="admin@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    # create a minimal project record - constructor requires many fields
    project = models.project.Project(
        name="Shortcut Test",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="",
        website="",
        color="",
        deadline=datetime.datetime.now(),
        stage="",
        delivery_method="",
    )
    project.creator_id = user.id
    dbsession.add(project)
    dbsession.flush()

    # log in as the admin user so that the comments page can be reached
    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "admin"
    form["password"] = "admin"
    # the login view redirects on success (303 See Other)
    form.submit(status=303)

    # visit the comments page for the new project; slug is derived from name
    url = f"/project/{project.id}/{project.slug}/comments"
    res = testapp.get(url, status=200)

    # there should be exactly one green plus-lg button icon
    # count with a regex that tolerates line breaks; the icon is rendered on a
    # separate line from the <a> or <button> tag, so a simple substring match
    # was failing.
    import re

    count = len(
        re.findall(
            r'class="[^"]*btn-success[^"]*".*?<i class="bi bi-plus-lg"', res.text, re.S
        )
    )
    if count != 1:
        # dump a small snippet for easier debugging
        idx = res.text.find("plus-lg")
        snippet = res.text[idx - 100 : idx + 200] if idx != -1 else "<not found>"
        print("Lines containing plus-lg:")
        for line in res.text.splitlines():
            if "plus-lg" in line:
                print(line)
    assert count == 1


def test_trash_shortcut_script_and_single_button(testapp, dbsession):
    """Ensure a page with just one red trash icon gets the delete shortcut.

    The company view page renders exactly one red "trash" button alongside a
    pencil and star; the helper script should detect that single button and
    include the keyboard-shortcut code.  We mimic the same setup as the plus
    button test by creating a minimal company and then visiting its view URL
    after logging in.
    """
    # create an admin user
    user = models.user.User(
        name="admin2",
        password="admin",
        fullname="Admin User",
        email="admin2@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    # minimal company
    company = models.company.Company(
        name="Trash Test Co",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company.creator_id = user.id
    dbsession.add(company)
    dbsession.flush()

    # login then fetch view page
    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "admin2"
    form["password"] = "admin"
    form.submit(status=303)

    url = f"/company/{company.id}/{company.slug}"
    res = testapp.get(url, status=200)

    # count only red trash icons anywhere on page using regex that matches
    # <i class="bi bi-trash" inside a btn-danger.
    import re

    trash_count = len(
        re.findall(
            r'class="[^"]*btn-danger[^"]*".*?<i class="bi bi-trash"', res.text, re.S
        )
    )
    assert trash_count == 1
    assert (
        "keyboard shortcuts for pages with a single green plus or red trash" in res.text
    )


def test_category_filter_defaults_to_all_across_category_views(testapp, dbsession):
    import datetime

    user = models.user.User(
        name="category-all-user",
        password="admin",
        fullname="Category All User",
        email="category.all.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    company = models.company.Company(
        name="Category All Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company.created_by = user

    project = models.project.Project(
        name="Category All Project",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="",
        website="",
        color="",
        deadline=datetime.datetime.now(),
        stage="",
        delivery_method="",
    )
    project.created_by = user

    company_contact = models.contact.Contact(
        name="Category All Company Contact",
        role="",
        phone="",
        email="",
        color="",
    )
    company_contact.created_by = user
    company_contact.company = company

    project_contact = models.contact.Contact(
        name="Category All Project Contact",
        role="",
        phone="",
        email="",
        color="",
    )
    project_contact.created_by = user
    project_contact.project = project

    company_comment = models.comment.Comment("Category All Company Comment")
    company_comment.created_by = user
    company_comment.company = company

    project_comment = models.comment.Comment("Category All Project Comment")
    project_comment.created_by = user
    project_comment.project = project

    company_tag = models.tag.Tag(name="CategoryAllCompanyTag")
    company_tag.created_by = user
    company_tag.companies.append(company)

    project_tag = models.tag.Tag(name="CategoryAllProjectTag")
    project_tag.created_by = user
    project_tag.projects.append(project)

    dbsession.add_all(
        [
            company,
            project,
            company_contact,
            project_contact,
            company_comment,
            project_comment,
            company_tag,
            project_tag,
        ]
    )

    user.selected_contacts.append(company_contact)
    user.selected_contacts.append(project_contact)
    user.selected_tags.append(company_tag)
    user.selected_tags.append(project_tag)

    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "category-all-user"
    form["password"] = "admin"
    form.submit(status=303)

    pages_with_category_filter = [
        "/tag",
        "/comment",
        "/contact",
        f"/user/{user.name}/comments",
        f"/user/{user.name}/tags",
        f"/user/{user.name}/contacts",
        f"/user/{user.name}/selected_tags",
        f"/user/{user.name}/selected_contacts",
    ]

    for page_url in pages_with_category_filter:
        response = testapp.get(page_url, status=200)
        _assert_category_select_has_default_all(response.text)


def test_default_all_category_shows_company_and_project_records(testapp, dbsession):
    import datetime

    user = models.user.User(
        name="category-all-content-user",
        password="admin",
        fullname="Category All Content User",
        email="category.all.content@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    company = models.company.Company(
        name="Category Content Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company.created_by = user

    project = models.project.Project(
        name="Category Content Project",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="",
        website="",
        color="",
        deadline=datetime.datetime.now(),
        stage="",
        delivery_method="",
    )
    project.created_by = user

    company_comment = models.comment.Comment("Company default-all comment")
    company_comment.created_by = user
    company_comment.company = company

    project_comment = models.comment.Comment("Project default-all comment")
    project_comment.created_by = user
    project_comment.project = project

    company_contact = models.contact.Contact(
        name="Company default-all contact",
        role="",
        phone="",
        email="",
        color="",
    )
    company_contact.created_by = user
    company_contact.company = company

    project_contact = models.contact.Contact(
        name="Project default-all contact",
        role="",
        phone="",
        email="",
        color="",
    )
    project_contact.created_by = user
    project_contact.project = project

    company_tag = models.tag.Tag(name="Company default-all tag")
    company_tag.created_by = user
    company_tag.companies.append(company)

    project_tag = models.tag.Tag(name="Project default-all tag")
    project_tag.created_by = user
    project_tag.projects.append(project)

    dbsession.add_all(
        [
            company,
            project,
            company_comment,
            project_comment,
            company_contact,
            project_contact,
            company_tag,
            project_tag,
        ]
    )
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "category-all-content-user"
    form["password"] = "admin"
    form.submit(status=303)

    comments_page = testapp.get("/comment", status=200)
    assert "Company default-all comment" in comments_page.text
    assert "Project default-all comment" in comments_page.text

    contacts_page = testapp.get("/contact", status=200)
    assert "Company default-all contact" in contacts_page.text
    assert "Project default-all contact" in contacts_page.text

    tags_all_page = testapp.get("/tag", status=200)
    _assert_category_select_has_default_all(tags_all_page.text)
    assert "Company default-all tag" in tags_all_page.text
    assert "Project default-all tag" in tags_all_page.text

    tags_companies_page = testapp.get(
        "/tag", params={"category": "companies"}, status=200
    )
    assert "Company default-all tag" in tags_companies_page.text
    assert "Project default-all tag" not in tags_companies_page.text

    tags_projects_page = testapp.get(
        "/tag", params={"category": "projects"}, status=200
    )
    assert "Company default-all tag" not in tags_projects_page.text
    assert "Project default-all tag" in tags_projects_page.text


def test_selected_tags_switch_shows_companies_projects_and_contacts(testapp, dbsession):
    import datetime

    user = models.user.User(
        name="selected-tags-switch-user",
        password="admin",
        fullname="Selected Tags Switch User",
        email="selected.tags.switch.user@example.com",
        role="admin",
    )
    dbsession.add(user)
    dbsession.flush()

    company = models.company.Company(
        name="Selected Tags Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company.created_by = user

    project = models.project.Project(
        name="Selected Tags Project",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="PL",
        website="",
        color="",
        deadline=datetime.datetime.now(),
        stage="",
        delivery_method="",
    )
    project.created_by = user

    company_contact = models.contact.Contact(
        name="Selected Tags Company Contact",
        role="",
        phone="",
        email="",
        color="",
    )
    company_contact.created_by = user
    company_contact.company = company

    project_contact = models.contact.Contact(
        name="Selected Tags Project Contact",
        role="",
        phone="",
        email="",
        color="",
    )
    project_contact.created_by = user
    project_contact.project = project

    company_tag = models.tag.Tag(name="SelectedTagsCompanyTag")
    company_tag.created_by = user
    company_tag.companies.append(company)

    project_tag = models.tag.Tag(name="SelectedTagsProjectTag")
    project_tag.created_by = user
    project_tag.projects.append(project)

    dbsession.add_all(
        [
            company,
            project,
            company_contact,
            project_contact,
            company_tag,
            project_tag,
        ]
    )
    user.selected_tags.append(company_tag)
    user.selected_tags.append(project_tag)
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "selected-tags-switch-user"
    form["password"] = "admin"
    form.submit(status=303)

    companies_page = testapp.get(
        f"/user/{user.name}/selected_tags/companies",
        status=200,
    )
    assert "Selected Tags Company" in companies_page.text
    assert "Selected Tags Project" not in companies_page.text

    projects_page = testapp.get(
        f"/user/{user.name}/selected_tags/projects",
        status=200,
    )
    assert "Selected Tags Project" in projects_page.text
    assert "Selected Tags Company" not in projects_page.text

    contacts_page = testapp.get(
        f"/user/{user.name}/selected_tags/contacts",
        params={"category": ""},
        status=200,
    )
    assert "Selected Tags Company Contact" in contacts_page.text
    assert "Selected Tags Project Contact" in contacts_page.text


def test_select_all_tags_bulk_updates_selected_tags_table(testapp, dbsession):
    user = models.user.User(
        name="bulk-select-tags-user",
        password="admin",
        fullname="Bulk Select Tags User",
        email="bulk.select.tags@example.com",
        role="admin",
    )

    tag_a = models.tag.Tag(name="Bulk Select Tag A")
    tag_a.created_by = user
    tag_b = models.tag.Tag(name="Bulk Select Tag B")
    tag_b.created_by = user

    dbsession.add_all([user, tag_a, tag_b])
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = user.name
    form["password"] = "admin"
    form.submit(status=303)

    tags_page = testapp.get("/tag", status=200)
    csrf_token = _extract_hx_csrf_token(tags_page.text)

    response = testapp.post(
        "/tag?_select_all=1",
        {"checked": "true"},
        headers={"X-CSRF-Token": csrf_token},
        status=200,
    )
    assert response.headers.get("HX-Refresh") == "true"

    selected_tag_ids = (
        dbsession.execute(
            select(models.selected_tags.c.tag_id).where(
                models.selected_tags.c.user_id == user.id
            )
        )
        .scalars()
        .all()
    )
    assert set(selected_tag_ids) == {tag_a.id, tag_b.id}

    response = testapp.post(
        "/tag?_select_all=1",
        {"checked": "false"},
        headers={"X-CSRF-Token": csrf_token},
        status=200,
    )
    assert response.headers.get("HX-Refresh") == "true"

    selected_tag_ids = (
        dbsession.execute(
            select(models.selected_tags.c.tag_id).where(
                models.selected_tags.c.user_id == user.id
            )
        )
        .scalars()
        .all()
    )
    assert selected_tag_ids == []


def test_select_all_project_companies_updates_selected_companies(testapp, dbsession):
    import datetime

    user = models.user.User(
        name="bulk-select-project-companies-user",
        password="admin",
        fullname="Bulk Select Project Companies User",
        email="bulk.select.project.companies@example.com",
        role="admin",
    )

    company = models.company.Company(
        name="Bulk Select Project Company",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company.created_by = user

    project = models.project.Project(
        name="Bulk Select Project",
        street="",
        postcode="",
        city="",
        subdivision="",
        country="",
        website="",
        color="",
        deadline=datetime.datetime.now(),
        stage="",
        delivery_method="",
    )
    project.created_by = user

    association = models.Activity(stage="", role="")
    association.company = company
    association.project = project

    dbsession.add_all([user, company, project, association])
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = user.name
    form["password"] = "admin"
    form.submit(status=303)

    select_all_url = f"/project/{project.id}/{project.slug}/companies?_select_all=1"

    project_companies_page = testapp.get(
        f"/project/{project.id}/{project.slug}/companies", status=200
    )
    csrf_token = _extract_hx_csrf_token(project_companies_page.text)

    response = testapp.post(
        select_all_url,
        {"checked": "true"},
        headers={"X-CSRF-Token": csrf_token},
        status=200,
    )
    assert response.headers.get("HX-Refresh") == "true"

    selected_company_ids = (
        dbsession.execute(
            select(models.selected_companies.c.company_id).where(
                models.selected_companies.c.user_id == user.id
            )
        )
        .scalars()
        .all()
    )
    assert set(selected_company_ids) == {company.id}

    selected_project_ids = (
        dbsession.execute(
            select(models.selected_projects.c.project_id).where(
                models.selected_projects.c.user_id == user.id
            )
        )
        .scalars()
        .all()
    )
    assert selected_project_ids == []

    response = testapp.post(
        select_all_url,
        {"checked": "false"},
        headers={"X-CSRF-Token": csrf_token},
        status=200,
    )
    assert response.headers.get("HX-Refresh") == "true"

    selected_company_ids = (
        dbsession.execute(
            select(models.selected_companies.c.company_id).where(
                models.selected_companies.c.user_id == user.id
            )
        )
        .scalars()
        .all()
    )
    assert selected_company_ids == []


def test_company_website_autofill_supports_developer_descriptors(
    testapp, dbsession, monkeypatch
):
    os.environ["GEMINI_API_KEY"] = "dummy"
    from marker.utils import website_autofill

    def mock_invoke(self, prompt):
        if "Developer" in prompt:
            return type("Resp", (), {"content": '{"name": "Alfa Developer"}'})()
        else:
            return type("Resp", (), {"content": '{"name": "Alfa Deweloper"}'})()

    def make_loader(descriptor):
        return lambda self: [type("Doc", (), {"page_content": f"Alfa {descriptor}"})()]

    def mock_invoke(self, prompt):
        if "Deweloper" in prompt:
            return type("Resp", (), {"content": '{"name": "Alfa Deweloper"}'})()
        else:
            return type("Resp", (), {"content": '{"name": "Alfa Developer"}'})()

    monkeypatch.setattr(
        "langchain_google_genai.ChatGoogleGenerativeAI.invoke",
        mock_invoke,
    )

    user = models.user.User(
        name="company-autofill-descriptor-editor",
        password="admin",
        fullname="Company Autofill Descriptor Editor",
        email="company.autofill.descriptor@example.com",
        role="editor",
    )
    dbsession.add(user)
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "company-autofill-descriptor-editor"
    form["password"] = "admin"
    form.submit(status=303)

    monkeypatch.setattr(
        website_autofill,
        "location_details",
        lambda **kwargs: None,
    )

    for descriptor in ("Deweloper", "Developer"):
        monkeypatch.setattr(
            "langchain_community.document_loaders.WebBaseLoader.load",
            make_loader(descriptor),
        )
        response = testapp.get(
            "/company/add/website_autofill",
            params={"website": f"https://example.com/kontakt/"},
            status=200,
        )
        fields = response.json["fields"]

        assert fields["name"] == f"Alfa {descriptor}"


def test_company_website_autofill_prefers_company_like_descriptor_casing(
    testapp, dbsession, monkeypatch
):
    os.environ["GEMINI_API_KEY"] = "dummy"
    from marker.utils import website_autofill

    monkeypatch.setattr(
        "langchain_community.document_loaders.WebBaseLoader.load",
        lambda self: [
            type("Doc", (), {"page_content": "alfa developer Alfa Developer"})()
        ],
    )
    monkeypatch.setattr(
        "langchain_google_genai.ChatGoogleGenerativeAI.invoke",
        lambda self, prompt: type(
            "Resp", (), {"content": '{"name": "Alfa Developer"}'}
        )(),
    )

    user = models.user.User(
        name="company-autofill-descriptor-casing-editor",
        password="admin",
        fullname="Company Autofill Descriptor Casing Editor",
        email="company.autofill.descriptor.casing@example.com",
        role="editor",
    )
    dbsession.add(user)
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "company-autofill-descriptor-casing-editor"
    form["password"] = "admin"
    form.submit(status=303)

    monkeypatch.setattr(
        website_autofill,
        "location_details",
        lambda **kwargs: None,
    )

    response = testapp.get(
        "/company/add/website_autofill",
        params={"website": "https://example.com/kontakt/"},
        status=200,
    )
    fields = response.json["fields"]

    assert fields["name"] == "Alfa Developer"


def test_company_website_autofill_extracts_adjacent_name_street_postcode_city(
    testapp, dbsession, monkeypatch
):
    os.environ["GEMINI_API_KEY"] = "dummy"
    from marker.utils import website_autofill

    monkeypatch.setattr(
        "langchain_community.document_loaders.WebBaseLoader.load",
        lambda self: [
            type(
                "Doc",
                (),
                {
                    "page_content": "Nowa Przestrzeń Developer Kwiatowa 12 00-123 Warszawa"
                },
            )()
        ],
    )
    monkeypatch.setattr(
        "langchain_google_genai.ChatGoogleGenerativeAI.invoke",
        lambda self, prompt: type(
            "Resp",
            (),
            {
                "content": '{"name": "Nowa Przestrzeń Developer", "street": "Kwiatowa 12", "postcode": "00-123", "city": "Warszawa"}'
            },
        )(),
    )

    user = models.user.User(
        name="company-autofill-address-block-editor",
        password="admin",
        fullname="Company Autofill Address Block Editor",
        email="company.autofill.address.block@example.com",
        role="editor",
    )
    dbsession.add(user)
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "company-autofill-address-block-editor"
    form["password"] = "admin"
    form.submit(status=303)

    monkeypatch.setattr(
        website_autofill,
        "location_details",
        lambda **kwargs: None,
    )

    response = testapp.get(
        "/company/add/website_autofill",
        params={"website": "https://example.com/kontakt/"},
        status=200,
    )
    fields = response.json["fields"]

    assert fields["name"] == "Nowa Przestrzeń Developer"
    assert fields["street"] == "Kwiatowa 12"
    assert fields["postcode"] == "00-123"
    assert fields["city"] == "Warszawa"


def test_company_website_autofill_includes_trade_prefix_from_previous_line(
    testapp, dbsession, monkeypatch
):
    os.environ["GEMINI_API_KEY"] = "dummy"
    from marker.utils import website_autofill

    # Patch will be set per test case below

    user = models.user.User(
        name="company-autofill-prefix-editor",
        password="admin",
        fullname="Company Autofill Prefix Editor",
        email="company.autofill.prefix@example.com",
        role="editor",
    )
    dbsession.add(user)
    dbsession.flush()

    login_page = testapp.get("/login", status=200)
    form = login_page.forms[0]
    form["username"] = "company-autofill-prefix-editor"
    form["password"] = "admin"
    form.submit(status=303)

    monkeypatch.setattr(
        website_autofill,
        "location_details",
        lambda **kwargs: None,
    )

    html_cases = (
        (
            "FHU",
            "FHU Alfa",
        ),
        (
            "Przedsiębiorstwo Handlowo-Usługowe",
            "Przedsiębiorstwo Handlowo-Usługowe Alfa",
        ),
    )

    for prefix_line, expected_name in html_cases:
        monkeypatch.setattr(
            "langchain_community.document_loaders.WebBaseLoader.load",
            lambda self: [
                type(
                    "Doc",
                    (),
                    {"page_content": f"{prefix_line} Alfa Kwiatowa 12 00-123 Warszawa"},
                )()
            ],
        )
        monkeypatch.setattr(
            "langchain_google_genai.ChatGoogleGenerativeAI.invoke",
            lambda self, prompt, expected_name=expected_name: type(
                "Resp",
                (),
                {
                    "content": f'{{"name": "{expected_name}", "street": "Kwiatowa 12", "postcode": "00-123", "city": "Warszawa"}}'
                },
            )(),
        )

        response = testapp.get(
            "/company/add/website_autofill",
            params={"website": "https://example.com/kontakt/"},
            status=200,
        )
        fields = response.json["fields"]

        assert fields["name"] == expected_name
        assert fields["street"] == "Kwiatowa 12"
        assert fields["postcode"] == "00-123"
        assert fields["city"] == "Warszawa"


def test_company_website_autofill_error(testapp, dbsession, monkeypatch):
    os.environ["GEMINI_API_KEY"] = "dummy"
    from marker.utils import website_autofill

    # Patch the LLM call to raise an exception
    monkeypatch.setattr(
        "langchain_community.document_loaders.WebBaseLoader.load",
        lambda self: [type("Doc", (), {"page_content": "irrelevant"})()],
    )
    monkeypatch.setattr(
        "langchain_google_genai.ChatGoogleGenerativeAI.invoke",
        lambda self, prompt: (_ for _ in ()).throw(RuntimeError("LLM error!")),
    )
    monkeypatch.setattr(
        website_autofill,
        "location_details",
        lambda **kwargs: None,
    )
    from marker import models

    user = models.user.User(
        name="company-autofill-error-editor",
        password="admin",
        fullname="Company Autofill Error Editor",
        email="company.autofill.error@example.com",
        role="editor",
    )
    dbsession.add(user)
    dbsession.flush()
    _login_as_editor(testapp, "company-autofill-error-editor", "admin")
    resp = testapp.get(
        "/company/add/website_autofill",
        params={"website": "https://fail.example.com"},
        status=502,
    )
    assert resp.json["error"] == "LLM error!"
    assert resp.json["fields"] == {}


def test_company_website_autofill_error_long_response(testapp, dbsession, monkeypatch):
    os.environ["GEMINI_API_KEY"] = "dummy"
    from marker import models
    from marker.utils import website_autofill

    monkeypatch.setattr(
        "langchain_community.document_loaders.WebBaseLoader.load",
        lambda self: [type("Doc", (), {"page_content": "irrelevant"})()],
    )
    # Simulate a long error message with 'Response:'
    long_error = "Some error. Response: " + ("x" * 500)
    monkeypatch.setattr(
        "langchain_google_genai.ChatGoogleGenerativeAI.invoke",
        lambda self, prompt: (_ for _ in ()).throw(RuntimeError(long_error)),
    )
    monkeypatch.setattr(
        website_autofill,
        "location_details",
        lambda **kwargs: None,
    )
    user = models.user.User(
        name="company-autofill-error-long-editor",
        password="admin",
        fullname="Company Autofill Error Long Editor",
        email="company.autofill.error.long@example.com",
        role="editor",
    )
    dbsession.add(user)
    dbsession.flush()
    _login_as_editor(testapp, "company-autofill-error-long-editor", "admin")
    resp = testapp.get(
        "/company/add/website_autofill",
        params={"website": "https://fail.example.com"},
        status=502,
    )
    assert resp.json["error"].startswith("Some error.")
    assert resp.json["fields"] == {}


def test_company_website_autofill_error_flash_truncate(testapp, dbsession, monkeypatch):
    os.environ["GEMINI_API_KEY"] = "dummy"
    from marker import models
    from marker.utils import website_autofill

    monkeypatch.setattr(
        "langchain_community.document_loaders.WebBaseLoader.load",
        lambda self: [type("Doc", (), {"page_content": "irrelevant"})()],
    )
    # Simulate a very long error message (over 500 bytes)
    very_long_error = "x" * 1000
    monkeypatch.setattr(
        "langchain_google_genai.ChatGoogleGenerativeAI.invoke",
        lambda self, prompt: (_ for _ in ()).throw(RuntimeError(very_long_error)),
    )
    monkeypatch.setattr(
        website_autofill,
        "location_details",
        lambda **kwargs: None,
    )
    user = models.user.User(
        name="company-autofill-error-flash-editor",
        password="admin",
        fullname="Company Autofill Error Flash Editor",
        email="company.autofill.error.flash@example.com",
        role="editor",
    )
    dbsession.add(user)
    dbsession.flush()
    _login_as_editor(testapp, "company-autofill-error-flash-editor", "admin")
    resp = testapp.get(
        "/company/add/website_autofill",
        params={"website": "https://fail.example.com"},
        status=502,
    )
    assert resp.json["error"].startswith("x")
    assert resp.json["fields"] == {}


def test_company_add_ai_saves_contacts(testapp, dbsession, monkeypatch):
    os.environ["GEMINI_API_KEY"] = "dummy"
    from marker import models
    from marker.utils import website_autofill
    from marker.views import company as company_views

    monkeypatch.setattr(
        "langchain_community.document_loaders.WebBaseLoader.load",
        lambda self: [type("Doc", (), {"page_content": "Acme Corp Jan Kowalski CEO"})()],
    )

    def mock_invoke(self, prompt):
        if "Extract a list of contacts" in prompt:
            return type(
                "Resp",
                (),
                {
                    "content": '[{"name": "Jan Kowalski", "role": "CEO", "phone": "+48123456789", "email": "jan@acme.com"}]'
                },
            )()
        return type("Resp", (), {"content": '{"name": "Acme Corp", "city": "Warszawa", "country": "PL"}'})()

    monkeypatch.setattr(
        "langchain_google_genai.ChatGoogleGenerativeAI.invoke",
        mock_invoke,
    )
    monkeypatch.setattr(website_autofill, "location_details", lambda **kwargs: None)
    monkeypatch.setattr(company_views, "location_details", lambda **kwargs: None)

    user = models.user.User(
        name="company-add-ai-contacts-editor",
        password="admin",
        fullname="Company Add AI Contacts Editor",
        email="company.add.ai.contacts@example.com",
        role="editor",
    )
    dbsession.add(user)
    dbsession.flush()
    _login_as_editor(testapp, "company-add-ai-contacts-editor", "admin")

    ai_page = testapp.get("/company/add/ai", status=200)
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(ai_page.text, "html.parser")
    csrf_input = soup.find("input", {"name": "csrf_token"})
    assert csrf_input is not None
    csrf_token = csrf_input["value"]

    resp = testapp.post(
        "/company/add/ai",
        params={"website": "https://acme.example.com", "csrf_token": csrf_token},
        status=303,
    )
    resp.follow(status=200)

    company = dbsession.execute(
        select(models.company.Company).where(
            models.company.Company.name == "Acme Corp"
        )
    ).scalar_one_or_none()
    assert company is not None
    assert len(company.contacts) == 1
    contact = company.contacts[0]
    assert contact.name == "Jan Kowalski"
    assert contact.role == "CEO"
    assert contact.phone == "+48123456789"
    assert contact.email == "jan@acme.com"


def test_project_add_ai_saves_contacts(testapp, dbsession, monkeypatch):
    os.environ["GEMINI_API_KEY"] = "dummy"
    from marker import models
    from marker.utils import website_autofill
    from marker.views import project as project_views

    monkeypatch.setattr(
        "langchain_community.document_loaders.WebBaseLoader.load",
        lambda self: [type("Doc", (), {"page_content": "Budowex Anna Nowak PM"})()],
    )

    def mock_invoke(self, prompt):
        if "Extract a list of contacts" in prompt:
            return type(
                "Resp",
                (),
                {
                    "content": '[{"name": "Anna Nowak", "role": "PM", "phone": "+48987654321", "email": "anna@budowex.com"}]'
                },
            )()
        return type("Resp", (), {"content": '{"name": "Budowex", "city": "Krakow", "country": "PL", "stage": "", "delivery_method": ""}'})()

    monkeypatch.setattr(
        "langchain_google_genai.ChatGoogleGenerativeAI.invoke",
        mock_invoke,
    )
    monkeypatch.setattr(website_autofill, "location_details", lambda **kwargs: None)
    monkeypatch.setattr(project_views, "location_details", lambda **kwargs: None)

    user = models.user.User(
        name="project-add-ai-contacts-editor",
        password="admin",
        fullname="Project Add AI Contacts Editor",
        email="project.add.ai.contacts@example.com",
        role="editor",
    )
    dbsession.add(user)
    dbsession.flush()
    _login_as_editor(testapp, "project-add-ai-contacts-editor", "admin")

    ai_page = testapp.get("/project/add/ai", status=200)
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(ai_page.text, "html.parser")
    csrf_input = soup.find("input", {"name": "csrf_token"})
    assert csrf_input is not None
    csrf_token = csrf_input["value"]

    resp = testapp.post(
        "/project/add/ai",
        params={"website": "https://budowex.example.com", "csrf_token": csrf_token},
        status=303,
    )
    resp.follow(status=200)

    project = dbsession.execute(
        select(models.project.Project).where(
            models.project.Project.name == "Budowex"
        )
    ).scalar_one_or_none()
    assert project is not None
    assert len(project.contacts) == 1
    contact = project.contacts[0]
    assert contact.name == "Anna Nowak"
    assert contact.role == "PM"
    assert contact.phone == "+48987654321"
    assert contact.email == "anna@budowex.com"


def test_company_add_ai_saves_tags(testapp, dbsession, monkeypatch):
    os.environ["GEMINI_API_KEY"] = "dummy"
    from marker import models
    from marker.utils import website_autofill
    from marker.views import company as company_views

    monkeypatch.setattr(
        "langchain_community.document_loaders.WebBaseLoader.load",
        lambda self: [type("Doc", (), {"page_content": "TagCo offers construction and civil engineering services."})()],
    )

    def mock_invoke(self, prompt):
        if "Extract up to 20 tags" in prompt:
            return type("Resp", (), {"content": '["Construction", "Civil engineering"]'})()
        if "Extract a list of contacts" in prompt:
            return type("Resp", (), {"content": "[]"})()
        return type("Resp", (), {"content": '{"name": "TagCo", "city": "Gdansk", "country": "PL"}'})()

    monkeypatch.setattr("langchain_google_genai.ChatGoogleGenerativeAI.invoke", mock_invoke)
    monkeypatch.setattr(website_autofill, "location_details", lambda **kwargs: None)
    monkeypatch.setattr(company_views, "location_details", lambda **kwargs: None)

    user = models.user.User(
        name="company-add-ai-tags-editor",
        password="admin",
        fullname="Company Add AI Tags Editor",
        email="company.add.ai.tags@example.com",
        role="editor",
    )
    dbsession.add(user)
    dbsession.flush()
    _login_as_editor(testapp, "company-add-ai-tags-editor", "admin")

    ai_page = testapp.get("/company/add/ai", status=200)
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(ai_page.text, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]

    resp = testapp.post(
        "/company/add/ai",
        params={"website": "https://tagco.example.com", "csrf_token": csrf_token},
        status=303,
    )
    resp.follow(status=200)

    company = dbsession.execute(
        select(models.company.Company).where(models.company.Company.name == "TagCo")
    ).scalar_one_or_none()
    assert company is not None
    tag_names = {t.name for t in company.tags}
    assert "Construction" in tag_names
    assert "Civil engineering" in tag_names


def test_company_add_ai_reuses_existing_tag(testapp, dbsession, monkeypatch):
    """When the LLM returns a tag that already exists in the DB, the existing Tag row is reused."""
    os.environ["GEMINI_API_KEY"] = "dummy"
    from marker import models
    from marker.utils import website_autofill
    from marker.views import company as company_views

    # Pre-create a tag that should be reused
    existing_tag = models.tag.Tag("Architecture")
    dbsession.add(existing_tag)
    dbsession.flush()
    existing_tag_id = existing_tag.id

    monkeypatch.setattr(
        "langchain_community.document_loaders.WebBaseLoader.load",
        lambda self: [type("Doc", (), {"page_content": "ArchFirm provides architecture services."})()],
    )

    def mock_invoke(self, prompt):
        if "Extract up to 20 tags" in prompt:
            return type("Resp", (), {"content": '["Architecture"]'})()
        if "Extract a list of contacts" in prompt:
            return type("Resp", (), {"content": "[]"})()
        return type("Resp", (), {"content": '{"name": "ArchFirm", "city": "Poznan", "country": "PL"}'})()

    monkeypatch.setattr("langchain_google_genai.ChatGoogleGenerativeAI.invoke", mock_invoke)
    monkeypatch.setattr(website_autofill, "location_details", lambda **kwargs: None)
    monkeypatch.setattr(company_views, "location_details", lambda **kwargs: None)

    user = models.user.User(
        name="company-add-ai-reuse-tag-editor",
        password="admin",
        fullname="Company Add AI Reuse Tag Editor",
        email="company.add.ai.reusetag@example.com",
        role="editor",
    )
    dbsession.add(user)
    dbsession.flush()
    _login_as_editor(testapp, "company-add-ai-reuse-tag-editor", "admin")

    ai_page = testapp.get("/company/add/ai", status=200)
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(ai_page.text, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]

    testapp.post(
        "/company/add/ai",
        params={"website": "https://archfirm.example.com", "csrf_token": csrf_token},
        status=303,
    )

    company = dbsession.execute(
        select(models.company.Company).where(models.company.Company.name == "ArchFirm")
    ).scalar_one_or_none()
    assert company is not None
    assert len(company.tags) == 1
    # Must be the same row, not a duplicate
    assert company.tags[0].id == existing_tag_id


def test_project_add_ai_saves_tags(testapp, dbsession, monkeypatch):
    os.environ["GEMINI_API_KEY"] = "dummy"
    from marker import models
    from marker.utils import website_autofill
    from marker.views import project as project_views

    monkeypatch.setattr(
        "langchain_community.document_loaders.WebBaseLoader.load",
        lambda self: [type("Doc", (), {"page_content": "TagProject residential housing development."})()],
    )

    def mock_invoke(self, prompt):
        if "Extract up to 20 tags" in prompt:
            return type("Resp", (), {"content": '["Residential", "Housing"]'})()
        if "Extract a list of contacts" in prompt:
            return type("Resp", (), {"content": "[]"})()
        return type("Resp", (), {"content": '{"name": "TagProject", "city": "Lodz", "country": "PL", "stage": "", "delivery_method": ""}'})()

    monkeypatch.setattr("langchain_google_genai.ChatGoogleGenerativeAI.invoke", mock_invoke)
    monkeypatch.setattr(website_autofill, "location_details", lambda **kwargs: None)
    monkeypatch.setattr(project_views, "location_details", lambda **kwargs: None)

    user = models.user.User(
        name="project-add-ai-tags-editor",
        password="admin",
        fullname="Project Add AI Tags Editor",
        email="project.add.ai.tags@example.com",
        role="editor",
    )
    dbsession.add(user)
    dbsession.flush()
    _login_as_editor(testapp, "project-add-ai-tags-editor", "admin")

    ai_page = testapp.get("/project/add/ai", status=200)
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(ai_page.text, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]

    resp = testapp.post(
        "/project/add/ai",
        params={"website": "https://tagproject.example.com", "csrf_token": csrf_token},
        status=303,
    )
    resp.follow(status=200)

    project = dbsession.execute(
        select(models.project.Project).where(models.project.Project.name == "TagProject")
    ).scalar_one_or_none()
    assert project is not None
    tag_names = {t.name for t in project.tags}
    assert "Residential" in tag_names
    assert "Housing" in tag_names
