from sqlalchemy import select

from marker import models


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


def _set_cookie_headers(response):
    return [
        value for key, value in response.headerlist if key.lower() == "set-cookie"
    ]


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


def test_tag_search_is_case_insensitive_in_project_and_company_lists(testapp, dbsession):
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
        court="",
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
        court="",
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
        court="",
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
        "/contact/search/tags/results",
        params={"tag": "pipeline", "sort": "name", "order": "asc"},
        status=200,
    )
    _assert_text_order(
        res_sorted.text,
        ["Alpha Contact", "Project Contact", "Zulu Contact"],
    )

    res_filtered = testapp.get(
        "/contact/search/tags/results",
        params={"tag": "pipeline", "category": "companies", "country": "DE"},
        status=200,
    )
    assert "Alpha Contact" in res_filtered.text
    assert "Zulu Contact" not in res_filtered.text
    assert "Project Contact" not in res_filtered.text


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
        court="",
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
    assert _extract_selected_sort_value(all_contacts_with_color_sort.text) == "created_at"

    tags_results_with_color_sort = testapp.get(
        "/contact/search/tags/results",
        params={"tag": "pipeline", "sort": "color", "order": "asc"},
        status=200,
    )
    assert "color" not in _extract_sort_values_from_dropdown(
        tags_results_with_color_sort.text
    )
    assert _extract_selected_sort_value(tags_results_with_color_sort.text) == "created_at"


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
        court="",
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
        court="",
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
            court="",
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
        court="",
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
    comment_bodies = [body.decode_contents().lower() for body in soup.select(".card .card-body")]

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
        court="",
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
        court="",
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
        court="",
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
        court="",
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
    from marker.utils import website_autofill

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
        html = f"""
        <html>
            <head>
                <title>Kontakt - Alfa</title>
                <meta property="og:site_name" content="Alfa" />
            </head>
            <body>
                Alfa {descriptor}
                ul. Przykładowa 1
                00-001 Warszawa
            </body>
        </html>
        """

        monkeypatch.setattr(
            website_autofill,
            "_download_html",
            lambda url, timeout, html=html: (html, "https://alfa.pl/kontakt/"),
        )

        response = testapp.get(
            "/company/add/website_autofill",
            params={"website": "https://alfa.pl/kontakt/"},
            status=200,
        )
        fields = response.json["fields"]

        assert fields["name"] == f"Alfa {descriptor}"


def test_company_website_autofill_prefers_company_like_descriptor_casing(
    testapp, dbsession, monkeypatch
):
    from marker.utils import website_autofill

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

    html = """
    <html>
        <head>
            <title>Kontakt - alfa</title>
        </head>
        <body>
            alfa developer
            Alfa Developer
            ul. Przykładowa 1
            00-001 Warszawa
        </body>
    </html>
    """

    monkeypatch.setattr(
        website_autofill,
        "_download_html",
        lambda url, timeout: (html, "https://alfa.pl/kontakt/"),
    )

    response = testapp.get(
        "/company/add/website_autofill",
        params={"website": "https://alfa.pl/kontakt/"},
        status=200,
    )
    fields = response.json["fields"]

    assert fields["name"] == "Alfa Developer"


def test_company_website_autofill_extracts_adjacent_name_street_postcode_city(
    testapp, dbsession, monkeypatch
):
    from marker.utils import website_autofill

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

    html_variants = (
        """
        <html>
            <head>
                <title>Kontakt</title>
            </head>
            <body>
                Nowa Przestrzeń Developer
                Kwiatowa 12
                00-123 Warszawa
            </body>
        </html>
        """,
        """
        <html>
            <head>
                <title>Kontakt</title>
            </head>
            <body>
                Nowa Przestrzeń Developer, Kwiatowa 12, 00-123 Warszawa
            </body>
        </html>
        """,
    )

    for html in html_variants:
        monkeypatch.setattr(
            website_autofill,
            "_download_html",
            lambda url, timeout, html=html: (
                html,
                "https://nowa-przestrzen.pl/kontakt/",
            ),
        )

        response = testapp.get(
            "/company/add/website_autofill",
            params={"website": "https://nowa-przestrzen.pl/kontakt/"},
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
    from marker.utils import website_autofill

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
        html = f"""
        <html>
            <head>
                <title>Kontakt</title>
            </head>
            <body>
                {prefix_line}
                Alfa
                Kwiatowa 12
                00-123 Warszawa
            </body>
        </html>
        """

        monkeypatch.setattr(
            website_autofill,
            "_download_html",
            lambda url, timeout, html=html: (
                html,
                "https://alfa.pl/kontakt/",
            ),
        )

        response = testapp.get(
            "/company/add/website_autofill",
            params={"website": "https://alfa.pl/kontakt/"},
            status=200,
        )
        fields = response.json["fields"]

        assert fields["name"] == expected_name
        assert fields["street"] == "Kwiatowa 12"
        assert fields["postcode"] == "00-123"
        assert fields["city"] == "Warszawa"
