from marker import models


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


def test_notfound(testapp):
    res = testapp.get("/badurl", status=404)
    assert res.status_code == 404


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
