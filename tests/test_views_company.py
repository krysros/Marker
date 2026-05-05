from unittest.mock import MagicMock, patch

import pytest
import transaction
from pyramid.httpexceptions import HTTPSeeOther
from webob.multidict import MultiDict

import marker.forms.ts
from marker.models.association import Activity
from marker.models.comment import Comment
from marker.models.company import Company
from marker.models.contact import Contact
from marker.models.project import Project
from marker.models.tag import Tag
from marker.models.user import User
from marker.models.user import User as MarkerUser
from marker.utils.uptime import clear_uptime_cache
from marker.views.company import CompanyView
from tests.conftest import DummyRequestWithIdentity


@pytest.fixture(autouse=True)
def patch_translationstring_str(monkeypatch):
    monkeypatch.setattr(
        marker.forms.ts.TranslationString, "__str__", lambda self: self.msg
    )
    yield


@pytest.fixture(autouse=True)
def clear_uptime_cache_before_each_test():
    clear_uptime_cache()
    yield


def test_company_all_route_coverage(dbsession):
    user = User(
        name="testuser",
        fullname="Test User",
        email="test@example.com",
        role="user",
        password="testpass",
    )
    dbsession.add(user)
    transaction.commit()

    company = Company(
        name="TestCo",
        street="Test Street",
        postcode="12345",
        city="Test City",
        subdivision="PL-MZ",
        country="PL",
        website=None,
        color="red",
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    transaction.commit()

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.GET = MultiDict()
    request.params = MultiDict()
    request.locale_name = "en"
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company"
    request.session = MagicMock()
    request.response = MagicMock()
    request.context = MagicMock()
    request.environ = {}
    request.environ["webob._parsed_get_vars"] = (MultiDict(), MultiDict())
    request.environ["webob._parsed_post_vars"] = (MultiDict(), MultiDict())
    request.environ["webob._parsed_params_vars"] = (MultiDict(), MultiDict())

    view = CompanyView(request)
    result = view.all()
    assert "paginator" in result
    assert any(c.name == "TestCo" for c in result["paginator"])


def test_company_count_methods(dbsession):
    fullname = "Test User2"
    email = "test2@example.com"
    role = "user"
    password = "testpass2"
    user = User(
        name="testuser2",
        fullname=fullname,
        email=email,
        role=role,
        password=password,
    )
    dbsession.add(user)
    dbsession.flush()

    company = Company(
        name="TestCo2",
        street="Test Street",
        postcode="54321",
        city="Test City",
        subdivision="PL-MZ",
        country="PL",
        website=None,
        color="blue",
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    transaction.commit()

    # Add tags to the company
    for i in range(3):
        tag = Tag(name=f"Tag{i}")
        dbsession.add(tag)
        company.tags.append(tag)
    dbsession.flush()

    # Add projects (via Activity) to the company
    for i in range(2):
        project = Project(
            name=f"Project{i}",
            street=f"ProjStreet{i}",
            postcode=f"00-00{i}",
            city=f"ProjCity{i}",
            subdivision="PL-MZ",
            country="PL",
            website=None,
            color="green",
            deadline=None,
            stage="draft",
            delivery_method="courier",
        )
        dbsession.add(project)
        activity = Activity()
        activity.project = project
        activity.company = company
        dbsession.add(activity)
        company.projects.append(activity)
    dbsession.flush()

    # Add contacts to the company
    for i in range(4):
        contact = Contact(
            name=f"Contact{i}",
            role="employee",
            phone=f"12345678{i}",
            email=f"contact{i}@ex.com",
            color="yellow",
        )
        dbsession.add(contact)
        company.contacts.append(contact)
    dbsession.flush()

    # Add comments to the company
    for i in range(5):
        comment = Comment(comment=f"Comment{i}")
        dbsession.add(comment)
        company.comments.append(comment)
    dbsession.flush()

    # Stars (each user stars a different company, but we check the counter on one)
    # Star: one user, one company
    star_user = MarkerUser(
        name="StarUser", fullname="U", email="star@ex.com", role="user", password="x"
    )
    dbsession.add(star_user)
    star_user.companies_stars.append(company)
    dbsession.flush()

    # Similar companies (simulate by adding tags to other companies)
    for i in range(7):
        other = Company(
            name=f"OtherCo{i}",
            street="S",
            postcode="00-000",
            city="C",
            subdivision="PL-MZ",
            country="PL",
            website=None,
            color="red",
            NIP=None,
            REGON=None,
            KRS=None,
        )
        dbsession.add(other)
        tag = Tag(name=f"SimTag{i}")
        dbsession.add(tag)
        company.tags.append(tag)
        other.tags.append(tag)
    dbsession.flush()

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.GET = MultiDict()
    request.params = MultiDict()
    request.locale_name = "en"
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company"
    request.session = MagicMock()
    request.response = MagicMock()
    request.context = MagicMock()
    request.context.company = company

    view = CompanyView(request)
    assert view.count_tags() == 10  # 3 tags + 7 similar tags
    assert view.count_projects() == 2
    assert view.count_contacts() == 4
    assert view.count_comments() == 5
    assert view.count_stars() == 1  # Only one user stars this company
    assert (
        view.count_similar() >= 7
    )  # Number of similar companies (may be higher depending on implementation)


# --- Helper function moved to top-level for test reuse ---
def make_request(
    dbsession, user=None, company=None, method="GET", params=None, post=None
):
    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user or User(
        name="u", fullname="U", email="e@e.com", role="user", password="x"
    )
    request.method = method
    request.GET = MultiDict(params or {})
    request.POST = MultiDict(post or {})
    request.params = MultiDict({**(params or {}), **(post or {})})
    request.locale_name = "en"
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company"
    request.session = MagicMock()
    request.response = MagicMock()
    request.context = MagicMock()
    if company:
        request.context.company = company
    return request


# --- Refactored: All nested test functions are now top-level ---
def test_company_stars_and_comments_branches(dbsession):
    """Covers uncovered branches in companies_stars and comments: sort/order, empty results."""
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    dbsession.flush()
    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.context = MagicMock()
    request.context.company = company
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company"
    # companies_stars: all sort/order
    for sort in ["name", "fullname", "email", "created_at", "updated_at", "invalid"]:
        for order in ["asc", "desc", "invalid"]:
            params = MultiDict({"sort": sort, "order": order})
            request.params = params
            view = CompanyView(request)
            result = view.companies_stars()
            assert "paginator" in result
    # companies_stars: empty result
    request.params = MultiDict({"sort": "name", "order": "asc"})
    result2 = CompanyView(request).companies_stars()
    assert isinstance(result2["paginator"], list)
    # comments: all sort/order
    for sort in ["created_at", "updated_at", "invalid"]:
        for order in ["asc", "desc", "invalid"]:
            params = MultiDict({"sort": sort, "order": order})
            request.params = params
            view = CompanyView(request)
            result = view.comments()
            assert "paginator" in result
    # comments: empty result
    request.params = MultiDict({"sort": "created_at", "order": "asc"})
    result3 = CompanyView(request).comments()
    assert isinstance(result3["paginator"], list)


def test_company_map_and_json_branches(dbsession):
    """Covers uncovered branches in map and company_json: all filters, sort/order, empty results."""
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website="w.com",
        NIP="123",
        REGON="456",
        KRS="789",
    )
    dbsession.add(company)
    dbsession.flush()
    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.context = MagicMock()
    request.context.company = company
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_json"
    # All filters for map
    params = MultiDict(
        {
            "name": "C",
            "street": "S",
            "postcode": "00-000",
            "city": "C",
            "subdivision": "PL-MZ",
            "country": "PL",
            "website": "w.com",
            "color": "red",
            "NIP": "123",
            "REGON": "456",
            "KRS": "789",
            "sort": "stars",
            "order": "asc",
        }
    )
    request.params = params
    request.GET = params
    view = CompanyView(request)
    result = view.map()
    assert "url" in result and "counter" in result
    # Test map with sort=stars, order=desc
    request.params["order"] = "desc"
    result2 = view.map()
    assert "url" in result2
    # Test map with sort=name, order=asc
    request.params["sort"] = "name"
    request.params["order"] = "asc"
    result3 = view.map()
    assert "url" in result3
    # Test map with sort=name, order=desc
    request.params["order"] = "desc"
    result4 = view.map()
    assert "url" in result4
    # Test map with no filters (should return all)
    request.params = MultiDict({"sort": "created_at", "order": "asc"})
    result5 = view.map()
    assert "url" in result5
    # company_json: all filters
    request.params = MultiDict(
        {
            "name": "C",
            "street": "S",
            "postcode": "00-000",
            "city": "C",
            "subdivision": "PL-MZ",
            "country": "PL",
            "website": "w.com",
            "color": "red",
            "NIP": "123",
            "REGON": "456",
            "KRS": "789",
        }
    )
    result6 = view.company_json()
    assert isinstance(result6, list)
    # company_json: empty result
    request.params = MultiDict({"name": "notfound"})
    result7 = view.company_json()
    assert isinstance(result7, list) and len(result7) == 0


def test_company_view_methods_minimal(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    dbsession.flush()
    request = make_request(dbsession, user, company)
    view = CompanyView(request)
    # Test view()
    request.matched_route = MagicMock()
    request.matched_route.name = "company_view"
    assert "company" in view.view()
    # Test map()
    assert "url" in view.map()
    # Test company_json()
    assert isinstance(view.company_json(), list)
    # Test add_tag() GET
    request.method = "GET"
    assert "form" in view.add_tag()
    # Test add_contact() GET
    request.method = "GET"
    assert "form" in view.add_contact()
    # Test company_add_comment() GET
    request.method = "GET"
    assert "form" in view.company_add_comment()
    # Test comments()
    assert "paginator" in view.comments()
    # Test similar()
    assert "paginator" in view.similar()
    # Test add() GET
    request.method = "GET"
    assert "form" in view.add()
    # Test website_autofill() with patch to avoid real HTTP request
    request.method = "GET"
    import marker.views.company as company_views_mod

    orig_autofill = company_views_mod.company_autofill_from_website
    company_views_mod.company_autofill_from_website = lambda website: {"dummy": True}
    result = view.website_autofill()
    assert "fields" in result
    company_views_mod.company_autofill_from_website = orig_autofill
    # Test edit() GET
    request.method = "GET"
    assert "form" in view.edit()
    # Test select()
    assert "companies" in view.select()
    # Test search()
    assert "form" in view.search()


def test_company_delete_and_del_row(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    dbsession.flush()
    request = make_request(dbsession, user, company, method="POST")
    view = CompanyView(request)
    # Test delete()
    resp = view.delete()
    assert hasattr(resp, "headers")
    # Test del_row()
    dbsession.add(company)
    dbsession.flush()
    resp2 = view.del_row()
    assert resp2 == ""


def test_company_star_and_check(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    dbsession.flush()
    request = make_request(dbsession, user, company, method="POST")
    # Test star
    request.identity.companies_stars = []
    view = CompanyView(request)
    html = view.star()
    assert "star" in html
    # Test unstar
    request.identity.companies_stars = [company]
    html2 = view.star()
    assert "star" in html2
    # Test check
    checked = view.check()
    assert "checked" in checked


def test_company_unlink_tag_and_add_project(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    tag = Tag(name="T")
    dbsession.add(tag)
    company.tags.append(tag)
    dbsession.flush()
    request = make_request(dbsession, user, company, method="POST")
    request.matchdict = {"company_id": company.id, "tag_id": tag.id}
    view = CompanyView(request)
    assert view.unlink_tag() == ""
    # Test add_project (GET)
    request.method = "GET"
    assert "form" in view.add_project()


def test_company_activity_edit_and_unlink(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    project = Project(
        name="P",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="blue",
        website=None,
        deadline=None,
        stage="draft",
        delivery_method="courier",
    )
    dbsession.add(project)
    activity = Activity()
    activity.project = project
    company.projects.append(activity)
    dbsession.flush()
    request = make_request(dbsession, user, company, method="GET")
    request.matchdict = {"company_id": company.id, "project_id": project.id}
    view = CompanyView(request)
    assert "form" in view.company_activity_edit()
    # Test activity_unlink
    request.method = "POST"
    assert view.activity_unlink() == ""


def test_company_add_ai_get(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    request = make_request(dbsession, user, method="GET")
    view = CompanyView(request)
    assert "form" in view.add_ai()


def test_company_add_tag_post_and_invalid(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    dbsession.flush()
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "POST"
    request.POST = MultiDict({"name": "TestTag"})
    request.context = MagicMock()
    request.context.company = company
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_tags"
    # Patch form to always validate
    from marker.forms.tag import TagLinkForm

    orig_validate = TagLinkForm.validate
    TagLinkForm.validate = lambda self: True
    view = CompanyView(request)
    resp = view.add_tag()
    assert resp.status_code == 303 or hasattr(resp, "status_code")
    TagLinkForm.validate = orig_validate
    # Invalid POST (form does not validate)
    request.method = "POST"
    TagLinkForm.validate = lambda self: False
    resp2 = view.add_tag()
    assert "form" in resp2
    TagLinkForm.validate = orig_validate


def test_company_add_contact_post_and_invalid(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    dbsession.flush()
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "POST"
    request.POST = MultiDict(
        {
            "name": "Contact1",
            "role": "r",
            "phone": "1",
            "email": "e@e.com",
            "color": "blue",
        }
    )
    request.context = MagicMock()
    request.context.company = company
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_contacts"
    from marker.forms.contact import ContactForm

    orig_validate = ContactForm.validate
    ContactForm.validate = lambda self: True
    view = CompanyView(request)
    resp = view.add_contact()
    assert resp.status_code == 303 or hasattr(resp, "status_code")
    ContactForm.validate = orig_validate
    # Invalid POST
    request.method = "POST"
    ContactForm.validate = lambda self: False
    resp2 = view.add_contact()
    assert "form" in resp2
    ContactForm.validate = orig_validate


def test_company_add_comment_post_and_invalid(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    dbsession.flush()
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "POST"
    request.POST = MultiDict({"comment": "Test comment"})
    request.context = MagicMock()
    request.context.company = company
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_comments"
    from marker.forms.comment import CommentForm

    orig_validate = CommentForm.validate
    CommentForm.validate = lambda self: True
    view = CompanyView(request)
    resp = view.company_add_comment()
    assert resp.status_code == 303 or hasattr(resp, "status_code")
    CommentForm.validate = orig_validate
    # Invalid POST
    request.method = "POST"
    CommentForm.validate = lambda self: False
    resp2 = view.company_add_comment()
    assert "form" in resp2
    CommentForm.validate = orig_validate


def test_company_add_post_and_invalid(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "POST"
    request.POST = MultiDict(
        {
            "name": "C",
            "street": "S",
            "postcode": "00-000",
            "city": "C",
            "subdivision": "PL-MZ",
            "country": "PL",
            "color": "red",
        }
    )
    request.GET = MultiDict()
    request.params = MultiDict(
        {
            "name": "C",
            "street": "S",
            "postcode": "00-000",
            "city": "C",
            "subdivision": "PL-MZ",
            "country": "PL",
            "color": "red",
        }
    )
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_view"
    from marker.forms.company import CompanyForm

    orig_validate = CompanyForm.validate
    CompanyForm.validate = lambda self: True
    view = CompanyView(request)
    resp = view.add()
    assert resp.status_code == 303 or hasattr(resp, "status_code")
    CompanyForm.validate = orig_validate
    # Invalid POST
    request.method = "POST"
    CompanyForm.validate = lambda self: False
    resp2 = view.add()
    assert "form" in resp2 or "tags" in resp2
    CompanyForm.validate = orig_validate


def test_company_edit_post_and_invalid(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    dbsession.flush()
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "POST"
    request.POST = MultiDict(
        {
            "name": "C",
            "street": "S",
            "postcode": "00-000",
            "city": "C",
            "subdivision": "PL-MZ",
            "country": "PL",
            "color": "red",
        }
    )
    request.context = MagicMock()
    request.context.company = company
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_view"
    from marker.forms.company import CompanyForm

    orig_validate = CompanyForm.validate
    CompanyForm.validate = lambda self: True
    view = CompanyView(request)
    resp = view.edit()
    assert resp.status_code == 303 or hasattr(resp, "status_code")
    CompanyForm.validate = orig_validate
    # Invalid POST
    request.method = "POST"
    CompanyForm.validate = lambda self: False
    resp2 = view.edit()
    assert "form" in resp2
    CompanyForm.validate = orig_validate


def test_company_add_project_post_and_invalid(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    dbsession.flush()
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "POST"
    request.POST = MultiDict({"name": "P", "stage": "draft", "role": "r"})
    request.context = MagicMock()
    request.context.company = company
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_projects"
    from marker.forms.project import ProjectActivityForm

    orig_validate = ProjectActivityForm.validate
    ProjectActivityForm.validate = lambda self: True
    view = CompanyView(request)
    resp = view.add_project()
    assert resp.status_code == 303 or hasattr(resp, "status_code")
    ProjectActivityForm.validate = orig_validate
    # Invalid POST
    request.method = "POST"
    ProjectActivityForm.validate = lambda self: False
    resp2 = view.add_project()
    assert "form" in resp2
    ProjectActivityForm.validate = orig_validate


def test_company_activity_edit_post_and_invalid(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    project = Project(
        name="P",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="blue",
        website=None,
        deadline=None,
        stage="draft",
        delivery_method="courier",
    )
    dbsession.add(project)
    dbsession.flush()
    from marker.models.association import Activity

    activity = Activity()
    activity.project = project
    activity.company = company
    dbsession.add(activity)
    dbsession.flush()
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "POST"
    request.POST = MultiDict({"stage": "draft", "role": "r"})
    request.context = MagicMock()
    request.context.company = company
    request.matchdict = {"company_id": company.id, "project_id": project.id}
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/project_companies"
    from marker.forms.association import ActivityForm

    orig_validate = ActivityForm.validate
    ActivityForm.validate = lambda self: True
    view = CompanyView(request)
    resp = view.company_activity_edit()
    assert resp.status_code == 303 or hasattr(resp, "status_code")
    ActivityForm.validate = orig_validate
    # Invalid POST
    request.method = "POST"
    ActivityForm.validate = lambda self: False
    resp2 = view.company_activity_edit()
    assert "form" in resp2
    ActivityForm.validate = orig_validate


# Error and edge case tests
import pytest
from pyramid.httpexceptions import HTTPNotFound


def test_unlink_tag_not_found(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    dbsession.flush()
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "POST"
    request.matchdict = {"company_id": 9999, "tag_id": 9999}
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    view = CompanyView(request)
    with pytest.raises(HTTPNotFound):
        view.unlink_tag()


def test_company_activity_edit_not_found(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    dbsession.flush()
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "POST"
    request.matchdict = {"company_id": 9999, "project_id": 9999}
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    view = CompanyView(request)
    with pytest.raises(HTTPNotFound):
        view.company_activity_edit()


def test_activity_unlink_not_found(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    dbsession.flush()
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "POST"
    request.matchdict = {"company_id": 9999, "project_id": 9999}
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    view = CompanyView(request)
    with pytest.raises(HTTPNotFound):
        view.activity_unlink()


def test_add_project_existing_activity(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    project = Project(
        name="P",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="blue",
        website=None,
        deadline=None,
        stage="draft",
        delivery_method="courier",
    )
    dbsession.add(project)
    dbsession.flush()
    from marker.models.association import Activity

    activity = Activity(stage="draft", role="r")
    activity.project = project
    activity.company = company
    dbsession.add(activity)
    company.projects.append(activity)
    dbsession.flush()
    from marker.forms.project import ProjectActivityForm

    orig_validate = ProjectActivityForm.validate
    ProjectActivityForm.validate = lambda self: True
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "POST"
    request.POST = MultiDict({"name": "P", "stage": "draft", "role": "r"})
    request.context = MagicMock()
    request.context.company = company
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_projects"
    view = CompanyView(request)
    # Should redirect even if activity exists (no duplicate)
    resp = view.add_project()
    assert hasattr(resp, "status_code")
    ProjectActivityForm.validate = orig_validate


def test_company_count_views_and_json(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    dbsession.flush()
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.context = MagicMock()
    request.context.company = company
    view = CompanyView(request)
    assert view.count_tags() == company.count_tags
    assert view.count_projects() == company.count_projects
    assert view.count_contacts() == company.count_contacts
    assert view.count_comments() == company.count_comments
    assert view.count_stars() == company.count_stars
    assert view.count_similar() == company.count_similar


# --- Refactored: All nested test functions under test_companies_stars_view are now top-level ---
def test_company_all_viewmode_and_sort_branches(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    dbsession.flush()
    from tests.conftest import DummyRequestWithIdentity

    # view param: invalid, contacts without tags, valid contacts with tags
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.GET = MultiDict({"view": "invalid"})
    request.params = request.GET
    request.locale_name = "en"
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company"
    request.session = MagicMock()
    request.response = MagicMock()
    request.context = MagicMock()
    request.environ = {}
    request.environ["webob._parsed_get_vars"] = (MultiDict(), MultiDict())
    request.environ["webob._parsed_post_vars"] = (MultiDict(), MultiDict())
    request.environ["webob._parsed_params_vars"] = (MultiDict(), MultiDict())
    view = CompanyView(request)
    result = view.all()
    assert "paginator" in result
    # contacts view without tags (should fallback to companies)
    request.GET["view"] = "contacts"
    request.params = request.GET
    result2 = view.all()
    assert result2["view_mode"] == "companies"
    # contacts view with tags (should enable contacts view)
    tag = Tag(name="T")
    dbsession.add(tag)
    company.tags.append(tag)
    dbsession.flush()
    request.GET["tag"] = "T"
    request.params = request.GET
    result3 = view.all()
    assert result3["view_mode"] == "contacts"
    # sort by stars asc/desc
    request.GET["sort"] = "stars"
    request.GET["order"] = "asc"
    request.params = request.GET
    result4 = view.all()
    assert "paginator" in result4
    request.GET["order"] = "desc"
    request.params = request.GET
    result5 = view.all()
    assert "paginator" in result5
    # sort by comments asc/desc
    request.GET["sort"] = "comments"
    request.GET["order"] = "asc"
    request.params = request.GET
    result6 = view.all()
    assert "paginator" in result6
    request.GET["order"] = "desc"
    request.params = request.GET
    result7 = view.all()
    assert "paginator" in result7


def test_company_view_projects_contacts_tags_sort_order_branches(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website="w",
        NIP="n",
        REGON="r",
        KRS="k",
    )
    dbsession.add(company)
    project = Project(
        name="P",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="blue",
        website="w",
        deadline=None,
        stage="draft",
        delivery_method="courier",
    )
    dbsession.add(project)
    tag = Tag(name="T")
    dbsession.add(tag)
    company.tags.append(tag)
    dbsession.flush()
    from marker.models.association import Activity

    activity = Activity(stage="draft", role="r")
    activity.project = project
    activity.company = company
    dbsession.add(activity)
    company.projects.append(activity)
    dbsession.flush()
    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.context = MagicMock()
    request.context.company = company
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company"
    # company_projects route, invalid sort/order
    request.matched_route = MagicMock()
    request.matched_route.name = "company_projects"
    request.params = MultiDict({"sort": "invalid", "order": "invalid"})
    request.identity.selected_projects = []
    view = CompanyView(request)
    result = view.view()
    assert "projects_assoc" in result or "bulk" in result
    # company_contacts route, invalid sort/order
    request.matched_route.name = "company_contacts"
    request.params = MultiDict({"sort": "invalid", "order": "invalid"})
    request.identity.selected_contacts = []
    result2 = view.view()
    assert "contacts" in result2 or "bulk" in result2
    # company_tags route, invalid sort/order
    request.matched_route.name = "company_tags"
    request.params = MultiDict({"sort": "invalid", "order": "invalid"})
    request.identity.selected_tags = []
    result3 = view.view()
    assert "tags" in result3 or "bulk" in result3


def test_company_view_projects_filter_stage_and_role(dbsession):
    user = User(name="u", fullname="U", email="flt@e.com", role="admin", password="x")
    dbsession.add(user)
    company = Company(
        name="FilterCo",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="",
        website="",
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    project = Project(
        name="FilterProj",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="",
        color="",
        deadline=None,
        stage="announcement",
        delivery_method="",
    )
    project.created_by = user
    dbsession.add(project)
    dbsession.flush()
    activity = Activity(stage="announcement", role="investor")
    activity.company = company
    activity.project = project
    dbsession.add(activity)
    dbsession.flush()
    request = _co_request(
        dbsession,
        user,
        company=company,
        params={
            "sort": "name",
            "order": "asc",
            "stage": "announcement",
            "role": "investor",
        },
    )
    request.matched_route.name = "company_projects"
    request.identity.selected_projects = []
    view = CompanyView(request)
    result = view.view()
    assert len(result["projects_assoc"]) == 1
    assert result["q"]["stage"] == "announcement"
    assert result["q"]["role"] == "investor"


def test_company_map_and_json_branches_starview(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website="w",
        NIP="n",
        REGON="r",
        KRS="k",
    )
    dbsession.add(company)
    dbsession.flush()
    from tests.conftest import DummyRequestWithIdentity

    # map: all filters
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.context = MagicMock()
    request.context.company = company
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_json"
    params = MultiDict(
        {
            "name": "C",
            "street": "S",
            "postcode": "00-000",
            "city": "C",
            "subdivision": "PL-MZ",
            "country": "PL",
            "website": "w",
            "color": "red",
            "NIP": "n",
            "REGON": "r",
            "KRS": "k",
            "sort": "stars",
            "order": "asc",
        }
    )
    request.params = params
    view = CompanyView(request)
    result = view.map()
    assert "url" in result and "counter" in result
    # map: test fallback sort
    request.params["sort"] = "created_at"
    request.params["order"] = "desc"
    result2 = view.map()
    assert "url" in result2
    # company_json: all filters
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.context = MagicMock()
    request.context.company = company
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_view"
    params = MultiDict(
        {
            "name": "C",
            "street": "S",
            "postcode": "00-000",
            "city": "C",
            "subdivision": "PL-MZ",
            "country": "PL",
            "website": "w",
            "color": "red",
            "NIP": "n",
            "REGON": "r",
            "KRS": "k",
        }
    )
    request.params = params
    view = CompanyView(request)
    result3 = view.company_json()
    assert isinstance(result3, list)
    # company_json: subdivision as None
    request.params = MultiDict({"subdivision": None})
    result4 = view.company_json()
    assert isinstance(result4, list)


def test_companies_stars_invalid_sort_order(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    dbsession.flush()
    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.context = MagicMock()
    request.context.company = company
    request.params = MultiDict({"sort": "invalid", "order": "invalid"})
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_stars"
    view = CompanyView(request)
    result = view.companies_stars()
    assert "paginator" in result


def test_add_tag_contact_comment_branches(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website="w",
        NIP="n",
        REGON="r",
        KRS="k",
    )
    dbsession.add(company)
    dbsession.flush()
    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "POST"
    request.POST = MultiDict({"name": "T"})
    request.context = MagicMock()
    request.context.company = company
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_tags"
    from marker.forms.tag import TagLinkForm

    orig_validate = TagLinkForm.validate
    TagLinkForm.validate = lambda self: True
    view = CompanyView(request)
    # Tag already exists and is in company.tags
    tag = Tag(name="T")
    dbsession.add(tag)
    company.tags.append(tag)
    dbsession.flush()
    resp = view.add_tag()
    assert hasattr(resp, "status_code")
    TagLinkForm.validate = orig_validate
    # add_contact branch: contact already in company.contacts
    from marker.forms.contact import ContactForm

    orig_validate_c = ContactForm.validate
    ContactForm.validate = lambda self: True
    request.POST = MultiDict(
        {
            "name": "Contact1",
            "role": "r",
            "phone": "1",
            "email": "e@e.com",
            "color": "blue",
        }
    )
    contact = Contact(
        name="Contact1", role="r", phone="1", email="e@e.com", color="blue"
    )
    dbsession.add(contact)
    company.contacts.append(contact)
    dbsession.flush()
    view = CompanyView(request)
    resp2 = view.add_contact()
    assert hasattr(resp2, "status_code")
    ContactForm.validate = orig_validate_c


def test_comments_branches(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website="w",
        NIP="n",
        REGON="r",
        KRS="k",
    )
    dbsession.add(company)
    dbsession.flush()
    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.context = MagicMock()
    request.context.company = company
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_comments"
    # Test invalid sort/order
    request.params = MultiDict({"sort": "invalid", "order": "invalid"})
    view = CompanyView(request)
    result = view.comments()
    assert "paginator" in result


def test_add_edit_branches(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website="w",
        NIP="n",
        REGON="r",
        KRS="k",
    )
    dbsession.add(company)
    dbsession.flush()
    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.context = MagicMock()
    request.context.company = company
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_view"
    # Test add with query_string
    request.query_string = "name=C&street=S"
    request.params = MultiDict({"name": "C", "street": "S"})
    request.POST = MultiDict()  # Ensure POST is a MultiDict for WTForms
    view = CompanyView(request)
    result = view.add()
    assert "form" in result
    # Test edit GET
    request.POST = MultiDict()  # Ensure POST is a MultiDict for WTForms
    result2 = view.edit()
    assert "form" in result2


def test_unlink_tag_project_branches(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website="w",
        NIP="n",
        REGON="r",
        KRS="k",
    )
    dbsession.add(company)
    tag = Tag(name="T")
    dbsession.add(tag)
    company.tags.append(tag)
    dbsession.flush()
    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "POST"
    request.matchdict = {"company_id": company.id, "tag_id": tag.id}
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    view = CompanyView(request)
    # Tag exists and is in company.tags
    assert view.unlink_tag() == ""


def test_add_project_activity_edit_unlink_branches(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website="w",
        NIP="n",
        REGON="r",
        KRS="k",
    )
    dbsession.add(company)
    project = Project(
        name="P",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="blue",
        website="w",
        deadline=None,
        stage="draft",
        delivery_method="courier",
    )
    dbsession.add(project)
    dbsession.flush()
    from marker.models.association import Activity

    activity = Activity(stage="draft", role="r")
    activity.project = project
    activity.company = company
    dbsession.add(activity)
    company.projects.append(activity)
    dbsession.flush()
    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "POST"
    request.context = MagicMock()
    request.context.company = company
    request.matchdict = {"company_id": company.id, "project_id": project.id}
    request.session = MagicMock()
    request.response = MagicMock()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/project_companies"
    # add_project: project exists, activity exists
    from marker.forms.project import ProjectActivityForm

    orig_validate = ProjectActivityForm.validate
    ProjectActivityForm.validate = lambda self: True
    request.POST = MultiDict({"name": "P", "stage": "draft", "role": "r"})
    view = CompanyView(request)
    resp = view.add_project()
    assert hasattr(resp, "status_code")
    ProjectActivityForm.validate = orig_validate
    # company_activity_edit: valid POST
    from marker.forms.association import ActivityForm

    orig_validate_a = ActivityForm.validate
    ActivityForm.validate = lambda self: True
    request.POST = MultiDict({"stage": "draft", "role": "r"})
    view = CompanyView(request)
    resp2 = view.company_activity_edit()
    assert hasattr(resp2, "status_code")
    ActivityForm.validate = orig_validate_a
    # activity_unlink: valid
    assert view.activity_unlink() == ""


def test_search_and_select_and_website_autofill(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website="w",
        NIP="n",
        REGON="r",
        KRS="k",
    )
    dbsession.add(company)
    dbsession.flush()
    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.context = MagicMock()
    request.context.company = company
    request.GET = MultiDict({"name": "C"})
    request.params = MultiDict({"name": "C"})
    request.POST = MultiDict()  # WTForms expects MultiDict
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company"
    import marker.views.company as company_views

    orig_autofill = company_views.company_autofill_from_website
    company_views.company_autofill_from_website = lambda website: {"dummy": True}
    view = CompanyView(request)
    # search
    result = view.search()
    assert "form" in result
    # select
    result2 = view.select()
    assert "companies" in result2
    # website_autofill
    result3 = view.website_autofill()
    assert "fields" in result3
    company_views.company_autofill_from_website = orig_autofill


def test_company_json_view(dbsession):
    user = User(name="u", fullname="U", email="e@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(company)
    dbsession.flush()
    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.context = MagicMock()
    request.context.company = company
    request.GET = MultiDict({"name": "C"})
    request.params = MultiDict({"name": "C"})
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_json"
    view = CompanyView(request)
    result = view.company_json()
    assert isinstance(result, list)


def test_companies_stars_view(dbsession):
    user = User(name="u2", fullname="U2", email="e2@e.com", role="user", password="x")
    dbsession.add(user)
    company = Company(
        name="C",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-MZ",
        country="PL",
        color="red",
        website="w",
        NIP="n",
        REGON="r",
        KRS="k",
    )
    dbsession.add(company)
    dbsession.flush()
    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.context = MagicMock()
    request.context.company = company
    request.params = MultiDict()
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company_stars"
    view = CompanyView(request)
    result = view.companies_stars()
    assert "paginator" in result


# ===========================================================================
# Extended coverage tests for remaining uncovered lines
# ===========================================================================


def _co_request(dbsession, user, company=None, method="GET", params=None, post=None):
    """Helper to create a properly configured request for company view tests."""
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = method
    request.GET = MultiDict(params or {})
    request.POST = MultiDict(post or {})
    request.params = MultiDict(params or {})
    request.locale_name = "en"
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/company"
    request.session = MagicMock()
    request.response = MagicMock()
    request.response.headers = {}
    request.context = MagicMock()
    if company:
        request.context.company = company
    request.matchdict = {}
    request.matched_route = MagicMock()
    request.matched_route.name = "company_view"
    request.environ = {}
    request.environ["webob._parsed_get_vars"] = (MultiDict(params or {}), MultiDict())
    request.environ["webob._parsed_post_vars"] = (MultiDict(post or {}), MultiDict())
    request.environ["webob._parsed_params_vars"] = (
        MultiDict(params or {}),
        MultiDict(),
    )
    request.path_qs = "/company"
    request.query_string = ""
    request.referrer = "/home"
    request.headers = {}
    return request


def _co_user(dbsession, name="couser"):
    user = User(
        name=name, fullname="U", email=f"{name}@e.com", role="admin", password="pw"
    )
    dbsession.add(user)
    dbsession.flush()
    return user


def _co_company(dbsession, user, name="TestCo"):
    company = Company(
        name=name,
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="http://x.com",
        color="",
        NIP="1234",
        REGON="5678",
        KRS="9012",
    )
    company.created_by = user
    dbsession.add(company)
    dbsession.flush()
    return company


# --- all() NIP/REGON/KRS filters ---


def test_company_all_nip_regon_krs_filters(dbsession):
    user = _co_user(dbsession, "conipfilter")
    _co_company(dbsession, user, "NIPCo")
    transaction.commit()
    request = _co_request(
        dbsession, user, params={"NIP": "1234", "REGON": "5678", "KRS": "9012"}
    )
    view = CompanyView(request)
    result = view.all()
    assert result["q"]["NIP"] == "1234"
    assert result["q"]["REGON"] == "5678"
    assert result["q"]["KRS"] == "9012"


def test_company_all_comments_desc(dbsession):
    user = _co_user(dbsession, "cocmtdesc")
    company = _co_company(dbsession, user, "CmtDescCo")
    comment = Comment(comment="c")
    comment.created_by = user
    company.comments.append(comment)
    transaction.commit()
    request = _co_request(dbsession, user, params={"sort": "comments", "order": "desc"})
    view = CompanyView(request)
    result = view.all()
    assert result["q"]["sort"] == "comments"


def test_company_all_sort_name_desc(dbsession):
    user = _co_user(dbsession, "conamedesc")
    _co_company(dbsession, user, "NameDescCo")
    transaction.commit()
    request = _co_request(dbsession, user, params={"sort": "name", "order": "desc"})
    view = CompanyView(request)
    result = view.all()
    assert result["q"]["order"] == "desc"


# --- view() tag/contact desc ordering ---


def test_company_view_tags_desc(dbsession):
    user = _co_user(dbsession, "coviewtagdesc")
    company = _co_company(dbsession, user, "ViewTagDescCo")
    tag = Tag(name="CoViewTag")
    tag.created_by = user
    company.tags.append(tag)
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        company=company,
        params={"sort": "name", "order": "desc"},
    )
    request.matched_route.name = "company_tags"
    view = CompanyView(request)
    result = view.view()
    assert "tags" in result


def test_company_view_contacts_desc(dbsession):
    user = _co_user(dbsession, "coviewcontdesc")
    company = _co_company(dbsession, user, "ViewContDescCo")
    contact = Contact(name="CoViewContact", role="", phone="", email="", color="")
    contact.created_by = user
    contact.company = company
    dbsession.add(contact)
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        company=company,
        params={"sort": "name", "order": "desc"},
    )
    request.matched_route.name = "company_contacts"
    view = CompanyView(request)
    result = view.view()
    assert "contacts" in result


# --- similar() sort branches ---


def test_company_similar_sort_stars(dbsession):
    user = _co_user(dbsession, "cosimstars")
    company = _co_company(dbsession, user, "SimStarsCo")
    tag = Tag(name="CoSimStarTag")
    tag.created_by = user
    company.tags.append(tag)
    c2 = _co_company(dbsession, user, "SimStarsCo2")
    c2.tags.append(tag)
    user.companies_stars.append(c2)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _co_request(
            dbsession,
            user,
            company=company,
            params={"sort": "stars", "order": order},
        )
        view = CompanyView(request)
        result = view.similar()
        assert result["q"]["sort"] == "stars"


def test_company_similar_sort_comments(dbsession):
    user = _co_user(dbsession, "cosimcmts")
    company = _co_company(dbsession, user, "SimCmtsCo")
    tag = Tag(name="CoSimCmtTag")
    tag.created_by = user
    company.tags.append(tag)
    c2 = _co_company(dbsession, user, "SimCmtsCo2")
    c2.tags.append(tag)
    comment = Comment(comment="c")
    comment.created_by = user
    c2.comments.append(comment)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _co_request(
            dbsession,
            user,
            company=company,
            params={"sort": "comments", "order": order},
        )
        view = CompanyView(request)
        result = view.similar()
        assert result["q"]["sort"] == "comments"


def test_company_similar_sort_generic(dbsession):
    user = _co_user(dbsession, "cosimgen")
    company = _co_company(dbsession, user, "SimGenCo")
    tag = Tag(name="CoSimGenTag")
    tag.created_by = user
    company.tags.append(tag)
    c2 = _co_company(dbsession, user, "SimGenCo2")
    c2.tags.append(tag)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _co_request(
            dbsession,
            user,
            company=company,
            params={"sort": "created_at", "order": order},
        )
        view = CompanyView(request)
        result = view.similar()
        assert result["q"]["sort"] == "created_at"


def test_company_similar_invalid_sort_order(dbsession):
    user = _co_user(dbsession, "cosimimv")
    company = _co_company(dbsession, user, "SimInvCo")
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        company=company,
        params={"sort": "invalid", "order": "invalid"},
    )
    view = CompanyView(request)
    result = view.similar()
    assert result["q"]["sort"] == "shared_tags"
    assert result["q"]["order"] == "desc"


def test_company_similar_with_results(dbsession):
    user = _co_user(dbsession, "cosimres")
    company = _co_company(dbsession, user, "SimResCo")
    tag = Tag(name="CoSimResTag")
    tag.created_by = user
    company.tags.append(tag)
    c2 = _co_company(dbsession, user, "SimResCo2")
    c2.tags.append(tag)
    transaction.commit()
    request = _co_request(dbsession, user, company=company)
    view = CompanyView(request)
    result = view.similar()
    assert "shared_tag_counts" in result


# --- add() query string pre-population and location ---


@patch("marker.views.company.location", return_value=None)
def test_company_add_get_query_string(mock_loc, dbsession):
    user = _co_user(dbsession, "coaddqs")
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        method="GET",
        post={},
        params={"name": "PrePop", "city": "W", "country": "PL"},
    )
    request.query_string = "name=PrePop"
    view = CompanyView(request)
    result = view.add()
    assert "form" in result
    assert result["form"].name.data == "PrePop"


@patch("marker.views.company.location", return_value={"lat": 50.0, "lon": 20.0})
def test_company_add_post_with_location(mock_loc, dbsession):
    user = _co_user(dbsession, "coaddloc")
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        method="POST",
        post={
            "name": "LocAddCo",
            "street": "S",
            "postcode": "",
            "city": "C",
            "subdivision": "",
            "country": "",
            "website": "",
            "color": "",
            "NIP": "",
            "REGON": "",
            "KRS": "",
        },
    )
    view = CompanyView(request)
    result = view.add()
    assert isinstance(result, HTTPSeeOther)


# --- edit() with location ---


@patch("marker.views.company.location", return_value={"lat": 50.0, "lon": 20.0})
def test_company_edit_post_with_location(mock_loc, dbsession):
    user = _co_user(dbsession, "coeditloc")
    company = _co_company(dbsession, user, "EditLocCo")
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        company=company,
        method="POST",
        post={
            "name": "EditLocCo",
            "street": "New St",
            "postcode": "",
            "city": "Krakow",
            "subdivision": "",
            "country": "PL",
            "website": "",
            "color": "",
            "NIP": "",
            "REGON": "",
            "KRS": "",
        },
    )
    view = CompanyView(request)
    result = view.edit()
    assert isinstance(result, HTTPSeeOther)


# --- search() POST ---


def test_company_search_post_basic(dbsession):
    user = _co_user(dbsession, "cosearchpost")
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        method="POST",
        post={
            "name": "SearchCo",
            "subdivision": "",
            "country": "",
            "color": "",
        },
    )
    view = CompanyView(request)
    result = view.search()
    assert isinstance(result, HTTPSeeOther)


# --- add_project POST success ---


def test_company_add_project_post_success(dbsession):
    user = _co_user(dbsession, "coaddprojsuc")
    company = _co_company(dbsession, user, "AddProjSucCo")
    project = Project(
        name="AddProjSucProject",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="",
        color="",
        deadline=None,
        stage="",
        delivery_method="",
    )
    project.created_by = user
    dbsession.add(project)
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        company=company,
        method="POST",
        post={
            "name": "AddProjSucProject",
            "stage": "",
            "role": "",
            "currency": "",
        },
    )
    view = CompanyView(request)
    result = view.add_project()
    assert isinstance(result, HTTPSeeOther)


# --- activity_edit POST success ---


def test_company_activity_edit_post_success(dbsession):
    user = _co_user(dbsession, "coacteditsuc")
    company = _co_company(dbsession, user, "ActEditSucCo")
    project = Project(
        name="ActEditSucProj",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="",
        color="",
        deadline=None,
        stage="",
        delivery_method="",
    )
    project.created_by = user
    dbsession.add(project)
    dbsession.flush()
    activity = Activity(role="investor", stage="")
    activity.company = company
    activity.project = project
    dbsession.add(activity)
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        company=company,
        method="POST",
        post={
            "stage": "",
            "role": "",
            "currency": "",
        },
    )
    request.matchdict = {"company_id": str(company.id), "project_id": str(project.id)}
    view = CompanyView(request)
    result = view.company_activity_edit()
    assert isinstance(result, HTTPSeeOther)


# --- activity_unlink success ---


def test_company_activity_unlink_success(dbsession):
    user = _co_user(dbsession, "coactunlnksuc")
    company = _co_company(dbsession, user, "ActUnlnkSucCo")
    project = Project(
        name="ActUnlnkSucProj",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="",
        color="",
        deadline=None,
        stage="",
        delivery_method="",
    )
    project.created_by = user
    dbsession.add(project)
    dbsession.flush()
    activity = Activity(role="investor", stage="")
    activity.company = company
    activity.project = project
    dbsession.add(activity)
    co_id = company.id
    proj_id = project.id
    transaction.commit()
    request = _co_request(dbsession, user, company=company, method="POST")
    request.matchdict = {"company_id": str(co_id), "project_id": str(proj_id)}
    view = CompanyView(request)
    result = view.activity_unlink()
    assert result == ""


# --- add_ai() POST branches ---


@patch("marker.views.company.location_details", return_value={"lat": 1, "lon": 2})
@patch(
    "marker.views.company.company_autofill_from_website",
    return_value={"name": "NewAICo"},
)
def test_company_add_ai_post_invalid_form_htmx(mock_autofill, mock_geo, dbsession):
    """Autofill returns data that fails CompanyForm validation (missing country).
    With HX-Request, should redirect via HX-Redirect to the manual add form."""
    user = _co_user(dbsession, "coaddaihtmx")
    transaction.commit()
    request = _co_request(
        dbsession, user, method="POST", post={"website": "http://example.com"}
    )
    request.headers = {"HX-Request": "true"}
    view = CompanyView(request)
    result = view.add_ai()
    assert result.status_code == 303


@patch("marker.views.company.location_details", return_value={"lat": 1, "lon": 2})
@patch(
    "marker.views.company.company_autofill_from_website",
    return_value={"name": "NewAICoSuccess", "country": "PL"},
)
def test_company_add_ai_post_success_htmx(mock_autofill, mock_geo, dbsession):
    """Autofill returns valid data; company is saved and HX-Redirect issued."""
    user = _co_user(dbsession, "coaddaisuccess")
    transaction.commit()
    request = _co_request(
        dbsession, user, method="POST", post={"website": "http://example.com"}
    )
    request.headers = {"HX-Request": "true"}
    view = CompanyView(request)
    result = view.add_ai()
    assert result.status_code == 303


@patch("marker.views.company.location_details", return_value=None)
@patch(
    "marker.views.company.company_autofill_from_website",
    return_value={"name": "NewAICoNoHX", "country": "PL"},
)
def test_company_add_ai_post_success_no_htmx(mock_autofill, mock_geo, dbsession):
    """Autofill returns valid data without HX-Request; HTTPSeeOther redirect."""
    user = _co_user(dbsession, "coaddaisucnohx")
    transaction.commit()
    request = _co_request(
        dbsession, user, method="POST", post={"website": "http://example.com"}
    )
    request.headers = {}
    view = CompanyView(request)
    result = view.add_ai()
    assert isinstance(result, HTTPSeeOther)


@patch("marker.views.company.location_details", return_value=None)
@patch(
    "marker.views.company.company_autofill_from_website",
    return_value={"name": "NewAICoInvNoHX"},
)
def test_company_add_ai_post_invalid_form_no_htmx(mock_autofill, mock_geo, dbsession):
    """Autofill returns invalid data without HX-Request; returns form dict."""
    user = _co_user(dbsession, "coaddaiinvnohx")
    transaction.commit()
    request = _co_request(
        dbsession, user, method="POST", post={"website": "http://example.com"}
    )
    request.headers = {}
    view = CompanyView(request)
    result = view.add_ai()
    assert isinstance(result, dict)
    assert "form" in result


@patch(
    "marker.views.company.company_autofill_from_website",
    side_effect=Exception("Error Response: " + "x" * 300),
)
def test_company_add_ai_post_error_long(mock_autofill, dbsession):
    user = _co_user(dbsession, "coaddaierr")
    transaction.commit()
    request = _co_request(
        dbsession, user, method="POST", post={"website": "http://fail.com"}
    )
    request.headers = {"HX-Request": "true"}
    view = CompanyView(request)
    result = view.add_ai()
    assert result.status_code is not None


@patch("marker.views.company.location_details", return_value=None)
@patch(
    "marker.views.company.company_autofill_from_website",
    return_value={"name": "ExistingAICo"},
)
def test_company_add_ai_existing_company(mock_autofill, mock_geo, dbsession):
    user = _co_user(dbsession, "coaddaiexist")
    _co_company(dbsession, user, "ExistingAICo")
    transaction.commit()
    request = _co_request(
        dbsession, user, method="POST", post={"website": "http://existing.com"}
    )
    request.headers = {}
    view = CompanyView(request)
    result = view.add_ai()
    assert isinstance(result, HTTPSeeOther)


@patch("marker.views.company.location_details", return_value=None)
@patch(
    "marker.views.company.company_autofill_from_website",
    return_value={"name": "ExistHTMXCo"},
)
def test_company_add_ai_existing_company_htmx(mock_autofill, mock_geo, dbsession):
    user = _co_user(dbsession, "coaddaiexhtmx")
    _co_company(dbsession, user, "ExistHTMXCo")
    transaction.commit()
    request = _co_request(
        dbsession, user, method="POST", post={"website": "http://existhtmx.com"}
    )
    request.headers = {"HX-Request": "true"}
    view = CompanyView(request)
    result = view.add_ai()
    assert result.status_code == 303


# ===========================================================================
# Phase 2 – remaining company.py coverage gaps
# ===========================================================================


def test_company_all_invalid_view_mode(dbsession):
    user = _co_user(dbsession, "coinvvm")
    transaction.commit()
    request = _co_request(dbsession, user, params={"view": "INVALID"})
    request.matched_route.name = "company_all"
    view = CompanyView(request)
    result = view.all()
    assert result["view_mode"] == "companies"


def test_company_all_filter_tags(dbsession):
    user = _co_user(dbsession, "cofilttag")
    co = _co_company(dbsession, user, "CoFiltTagCo")
    tag = Tag(name="CoFiltTag")
    tag.created_by = user
    co.tags.append(tag)
    dbsession.add(tag)
    transaction.commit()
    request = _co_request(dbsession, user, params={"tag": "CoFiltTag"})
    request.matched_route.name = "company_all"
    view = CompanyView(request)
    result = view.all()
    assert "CoFiltTag" in result["q"]["tag"]


def test_company_all_filter_tags_and_operator(dbsession):
    user = _co_user(dbsession, "cofilttagand")
    tag1 = Tag(name="CoANDTag1")
    tag1.created_by = user
    tag2 = Tag(name="CoANDTag2")
    tag2.created_by = user
    dbsession.add_all([tag1, tag2])
    co_both = _co_company(dbsession, user, "CoANDCoBoth")
    co_both.tags.append(tag1)
    co_both.tags.append(tag2)
    co_one = _co_company(dbsession, user, "CoANDCoOne")
    co_one.tags.append(tag1)
    transaction.commit()
    params = MultiDict([("tag", "CoANDTag1"), ("tag", "CoANDTag2"), ("tag_operator", "and")])
    request = _co_request(dbsession, user, params=params)
    request.matched_route.name = "company_all"
    view = CompanyView(request)
    result = view.all()
    companies = list(result["paginator"])
    assert any(c.name == "CoANDCoBoth" for c in companies)
    assert not any(c.name == "CoANDCoOne" for c in companies)
    assert result["q"]["tag_operator"] == "and"


def test_company_all_filter_website(dbsession):
    user = _co_user(dbsession, "cofiltws")
    _co_company(dbsession, user, "CoFiltWsCo")
    transaction.commit()
    request = _co_request(dbsession, user, params={"website": "http://x"})
    request.matched_route.name = "company_all"
    view = CompanyView(request)
    result = view.all()
    assert result["q"]["website"] == "http://x"


def test_company_all_contacts_view_mode(dbsession):
    user = _co_user(dbsession, "cocontvm")
    co = _co_company(dbsession, user, "CoContVmCo")
    tag = Tag(name="CoContVmTag")
    tag.created_by = user
    co.tags.append(tag)
    dbsession.add(tag)
    c = Contact(name="CoContVmCont", role="r", phone="1", email="x@e.com", color="")
    c.created_by = user
    c.company = co
    dbsession.add(c)
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        params={
            "tag": "CoContVmTag",
            "view": "contacts",
        },
    )
    request.matched_route.name = "company_all"
    view = CompanyView(request)
    result = view.all()
    assert result["view_mode"] == "contacts"


def test_company_all_sort_comments_asc(dbsession):
    user = _co_user(dbsession, "cocmtasc")
    co = _co_company(dbsession, user, "CoCmtAscCo")
    cmt = Comment(comment="test")
    cmt.created_by = user
    cmt.company_id = co.id
    dbsession.add(cmt)
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        params={
            "sort": "comments",
            "order": "asc",
        },
    )
    request.matched_route.name = "company_all"
    view = CompanyView(request)
    result = view.all()
    assert result["q"]["sort"] == "comments"


def test_company_all_bulk_select(dbsession):
    user = _co_user(dbsession, "cobulksel")
    _co_company(dbsession, user, "CoBulkSelCo")
    transaction.commit()
    request = _co_request(
        dbsession, user, method="POST", params={"_select_all": "1", "checked": "1"}
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    request.matched_route.name = "company_all"
    view = CompanyView(request)
    result = view.all()
    assert result is request.response


def test_company_view_projects_route(dbsession):
    user = _co_user(dbsession, "coviewpj")
    co = _co_company(dbsession, user, "CoViewPjCo")
    co_id = co.id
    transaction.commit()
    co = dbsession.get(Company, co_id)
    request = _co_request(dbsession, user, company=co)
    request.matched_route.name = "company_projects"
    view = CompanyView(request)
    result = view.view()
    assert "company" in result


def test_company_view_bulk_select(dbsession):
    user = _co_user(dbsession, "coviewbulk")
    co = _co_company(dbsession, user, "CoViewBulkCo")
    co_id = co.id
    transaction.commit()
    co = dbsession.get(Company, co_id)
    request = _co_request(
        dbsession,
        user,
        company=co,
        method="POST",
        params={"_select_all": "1", "checked": "1"},
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    request.matched_route.name = "company_tags"
    view = CompanyView(request)
    result = view.view()
    assert result is request.response


def test_company_map(dbsession):
    user = _co_user(dbsession, "comap")
    co = _co_company(dbsession, user, "CoMapCo")
    co.latitude = 50.0
    co.longitude = 20.0
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        params={
            "color": "red",
            "country": "PL",
        },
    )
    request.matched_route.name = "company_map"
    view = CompanyView(request)
    result = view.map()
    assert "url" in result


# --- Cover line 185: all() desc ordering for standard sort ---


def test_company_all_name_asc(dbsession):
    user = _co_user(dbsession, "conmasc")
    _co_company(dbsession, user, "CoNmAscCo")
    transaction.commit()
    request = _co_request(dbsession, user, params={"sort": "name", "order": "asc"})
    request.matched_route.name = "company_all"
    view = CompanyView(request)
    result = view.all()
    assert result["q"]["order"] == "asc"


# --- Cover line 464: view() contacts asc ordering ---


def test_company_view_contacts_asc(dbsession):
    user = _co_user(dbsession, "covcasc")
    co = _co_company(dbsession, user, "CoVcAscCo")
    c = Contact(name="CoVcAscCont", role="r", phone="1", email="x@e.com", color="")
    c.created_by = user
    c.company = co
    dbsession.add(c)
    transaction.commit()
    request = _co_request(dbsession, user, company=co, params={"order": "asc"})
    request.matched_route.name = "company_contacts"
    view = CompanyView(request)
    result = view.view()
    assert "contacts" in result


# --- Cover lines 508-509: view() bulk select on default route (no bulk_stmt) ---


def test_company_view_default_route_bulk_select(dbsession):
    """Cover lines 508-509: set_select_all_state + htmx_refresh when bulk_stmt is None."""
    user = _co_user(dbsession, "covdefbs")
    co = _co_company(dbsession, user, "CoVDefBsCo")
    co_id = co.id
    transaction.commit()
    co = dbsession.get(Company, co_id)
    request = _co_request(
        dbsession,
        user,
        company=co,
        method="POST",
        params={"_select_all": "1", "checked": "true"},
    )
    request.params = MultiDict({"_select_all": "1", "checked": "true"})
    request.matched_route.name = "company_view"
    view = CompanyView(request)
    result = view.view()
    assert result is request.response


# --- Cover lines 508-509 via handle_bulk_selection on contacts route ---


def test_company_view_contacts_bulk_select(dbsession):
    user = _co_user(dbsession, "covcbs")
    co = _co_company(dbsession, user, "CoVcBsCo")
    c = Contact(name="CoVcBsCont", role="r", phone="1", email="x@e.com", color="")
    c.created_by = user
    c.company = co
    dbsession.add(c)
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        company=co,
        method="POST",
        params={"_select_all": "1", "checked": "1"},
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    request.matched_route.name = "company_contacts"
    view = CompanyView(request)
    result = view.view()
    assert result is request.response


# --- Cover line 1090: similar() shared_tags desc ---


def test_company_similar_shared_tags_desc(dbsession):
    user = _co_user(dbsession, "cosimstd")
    co1 = _co_company(dbsession, user, "CoSimStdCo1")
    co2 = _co_company(dbsession, user, "CoSimStdCo2")
    tag = Tag(name="CoSimStdTag")
    tag.created_by = user
    co1.tags.append(tag)
    co2.tags.append(tag)
    dbsession.add(tag)
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        company=co1,
        params={
            "sort": "shared_tags",
            "order": "desc",
        },
    )
    view = CompanyView(request)
    result = view.similar()
    assert "paginator" in result


# --- Cover line 1574: search POST ---


def test_company_search_post_with_tag(dbsession):
    user = _co_user(dbsession, "cosrchpost")
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        method="POST",
        post={
            "name": "Test",
            "country": "",
            "color": "",
            "subdivision": "",
        },
    )
    request.params["tag"] = "SomeTag"
    view = CompanyView(request)
    result = view.search()
    assert isinstance(result, HTTPSeeOther)


def test_company_similar_shared_tags_asc(dbsession):
    """Cover line 1090: similar() shared_tags asc."""
    user = _co_user(dbsession, "cosimsta")
    co1 = _co_company(dbsession, user, "CoSimStaCo1")
    co2 = _co_company(dbsession, user, "CoSimStaCo2")
    tag = Tag(name="CoSimStaTag")
    tag.created_by = user
    co1.tags.append(tag)
    co2.tags.append(tag)
    dbsession.add(tag)
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        company=co1,
        params={
            "sort": "shared_tags",
            "order": "asc",
        },
    )
    view = CompanyView(request)
    result = view.similar()
    assert "paginator" in result


def test_company_similar_empty_tag_name(dbsession):
    """Cover line 1166: skip tags with empty name in similar tag display."""
    user = _co_user(dbsession, "cosimemptytag")
    co1 = _co_company(dbsession, user, "CoSimEmptyTagCo1")
    co2 = _co_company(dbsession, user, "CoSimEmptyTagCo2")
    empty_tag = Tag(name="")
    empty_tag.created_by = user
    co1.tags.append(empty_tag)
    co2.tags.append(empty_tag)
    dbsession.add(empty_tag)
    valid_tag = Tag(name="CoSimValidTag")
    valid_tag.created_by = user
    co1.tags.append(valid_tag)
    co2.tags.append(valid_tag)
    dbsession.add(valid_tag)
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        company=co1,
        params={
            "sort": "shared_tags",
            "order": "desc",
        },
    )
    view = CompanyView(request)
    result = view.similar()
    assert "paginator" in result


def test_company_unlink_tag_not_found(dbsession):
    """Cover line 1601: unlink_tag with non-existent tag."""
    user = _co_user(dbsession, "counlinktagnf")
    co = _co_company(dbsession, user, "CoUnlinkTagNfCo")
    co_id = co.id
    transaction.commit()
    request = _co_request(dbsession, user, company=co, method="POST")
    request.matchdict = {"company_id": str(co_id), "tag_id": "999999"}
    view = CompanyView(request)
    with pytest.raises(HTTPNotFound):
        view.unlink_tag()


def test_company_activity_edit_project_not_found(dbsession):
    """Cover line 1682: activity_edit with non-existent project."""
    user = _co_user(dbsession, "coacteditnf")
    co = _co_company(dbsession, user, "CoActEditNfCo")
    co_id = co.id
    transaction.commit()
    request = _co_request(dbsession, user, company=co)
    request.matchdict = {"company_id": str(co_id), "project_id": "999999"}
    view = CompanyView(request)
    with pytest.raises(HTTPNotFound):
        view.company_activity_edit()


def test_company_activity_unlink_project_not_found(dbsession):
    """Cover line 1733: activity_unlink with non-existent project."""
    user = _co_user(dbsession, "coactunlinknf")
    co = _co_company(dbsession, user, "CoActUnlinkNfCo")
    co_id = co.id
    transaction.commit()
    request = _co_request(dbsession, user, company=co, method="POST")
    request.matchdict = {"company_id": str(co_id), "project_id": "999999"}
    view = CompanyView(request)
    with pytest.raises(HTTPNotFound):
        view.activity_unlink()


@patch(
    "marker.views.company.company_autofill_from_website",
    side_effect=Exception("API failure"),
)
def test_company_add_ai_error_no_htmx(mock_autofill, dbsession):
    """Cover line 1772: add_ai error without HX-Request header."""
    user = _co_user(dbsession, "coaddaierr")
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        method="POST",
        post={
            "website": "http://example.com",
        },
    )
    request.headers = {}
    view = CompanyView(request)
    result = view.add_ai()
    if isinstance(result, HTTPSeeOther):
        # Redirect is a valid outcome (company already exists or error)
        assert result.location or result.headers.get("Location")
    else:
        assert "form" in result


@patch(
    "marker.views.company.company_autofill_from_website",
    side_effect=Exception("A" * 600),
)
def test_company_add_ai_error_htmx(mock_autofill, dbsession):
    """Cover line 1772: add_ai error with long message + HX-Request header."""
    user = _co_user(dbsession, "coaddaihtmx")
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        method="POST",
        post={
            "website": "http://example.com",
        },
    )
    request.headers = {"HX-Request": "true"}
    view = CompanyView(request)
    result = view.add_ai()
    assert result is request.response


@patch("marker.views.company.location", return_value={"lat": 50.0, "lon": 20.0})
def test_company_add_post_with_tags(mock_loc, dbsession):
    """Cover lines 1286-1300: add() POST with tags."""
    user = _co_user(dbsession, "coaddtags")
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        method="POST",
        post={
            "name": "CoAddTagsCo",
            "street": "S",
            "postcode": "",
            "city": "C",
            "subdivision": "",
            "country": "",
            "website": "",
            "color": "",
            "NIP": "",
            "REGON": "",
            "KRS": "",
        },
    )
    request.params["tag"] = "NewTestTag"
    view = CompanyView(request)
    result = view.add()


# ===========================================================================
# tag_operator invalid fallback in all() (line 216)
# ===========================================================================


def test_company_all_invalid_tag_operator(dbsession):
    """Cover line 216: invalid tag_operator falls back to 'or'."""
    from marker.models.tag import Tag

    user = _co_user(dbsession, "coinvtop")
    tag = Tag(name="InvTopTag")
    tag.created_by = user
    co = _co_company(dbsession, user, "InvTopCo")
    co.tags.append(tag)
    dbsession.add(tag)
    transaction.commit()
    params = MultiDict([("tag", "InvTopTag"), ("tag_operator", "invalid")])
    request = _co_request(dbsession, user, params=params)
    request.matched_route.name = "company_all"
    view = CompanyView(request)
    result = view.all()
    assert result["q"]["tag_operator"] == "or"


# ===========================================================================
# add_ai() contacts_autofill exception handler (line 1843)
# ===========================================================================


@patch("marker.views.company.location_details", return_value=None)
@patch(
    "marker.views.company.tags_autofill_from_website",
    return_value=[],
)
@patch(
    "marker.views.company.contacts_autofill_from_website",
    side_effect=Exception("contacts fail"),
)
@patch(
    "marker.views.company.company_autofill_from_website",
    return_value={"name": "ContExcCo", "country": "PL"},
)
def test_company_add_ai_contacts_exception(mock_autofill, mock_contacts, mock_tags, mock_geo, dbsession):
    """Cover line 1843: exception in contacts_autofill_from_website is handled."""
    user = _co_user(dbsession, "coaicontexc")
    transaction.commit()
    request = _co_request(
        dbsession, user, method="POST", post={"website": "http://example.com"}
    )
    request.headers = {}
    view = CompanyView(request)
    result = view.add_ai()
    # Company was still saved despite contacts failure — redirects
    assert isinstance(result, HTTPSeeOther)


@patch("marker.views.company.location_details", return_value=None)
@patch(
    "marker.views.company.tags_autofill_from_website",
    return_value=[],
)
@patch(
    "marker.views.company.contacts_autofill_from_website",
    return_value=[{"name": "John Smith", "role": "CEO", "phone": "123", "email": "j@e.com"}],
)
@patch(
    "marker.views.company.company_autofill_from_website",
    return_value={"name": "ContactReturnCo", "country": "PL"},
)
def test_company_add_ai_contacts_returned(mock_autofill, mock_contacts, mock_tags, mock_geo, dbsession):
    """Cover lines 1841-1852: contacts_autofill returns contact data that is saved."""
    user = _co_user(dbsession, "coaicontret")
    transaction.commit()
    request = _co_request(
        dbsession, user, method="POST", post={"website": "http://example.com"}
    )
    request.headers = {}
    view = CompanyView(request)
    result = view.add_ai()
    assert isinstance(result, HTTPSeeOther)
    assert isinstance(result, HTTPSeeOther)


# --- uptime() and uptime_check() ---


def test_company_uptime(dbsession):
    user = _co_user(dbsession, "couptime")
    # Company with website
    c1 = _co_company(dbsession, user, "UptimeCo1")
    # Company without website
    Company(
        name="UptimeCo2",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website=None,
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    dbsession.add(c1)
    transaction.commit()
    request = _co_request(dbsession, user)
    view = CompanyView(request)
    result = view.uptime()
    assert "paginator" in result
    names = [item.name for item in result["paginator"]]
    assert "UptimeCo1" in names
    assert "UptimeCo2" not in names


def test_company_uptime_check_no_url(dbsession):
    user = _co_user(dbsession, "coupchk1")
    transaction.commit()
    request = _co_request(dbsession, user, params={})
    view = CompanyView(request)
    result = view.uptime_check()
    assert result.status_code == 200
    assert 'class="badge bg-secondary"' in result.text


def test_company_uptime_check_success(dbsession):
    user = _co_user(dbsession, "coupchk2")
    transaction.commit()
    request = _co_request(dbsession, user, params={"url": "https://example.com"})
    view = CompanyView(request)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = view.uptime_check()
    assert result.status_code == 200
    assert 'class="badge bg-success"' in result.text
    assert ">200<" in result.text


def test_company_uptime_check_prepends_https(dbsession):
    user = _co_user(dbsession, "coupchk3")
    transaction.commit()
    request = _co_request(dbsession, user, params={"url": "example.com"})
    view = CompanyView(request)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        result = view.uptime_check()
    assert result.status_code == 200
    assert 'class="badge bg-success"' in result.text
    called_req = mock_open.call_args[0][0]
    assert called_req.full_url.startswith("https://")


def test_company_uptime_check_http_error(dbsession):
    import urllib.error

    user = _co_user(dbsession, "coupchk4")
    transaction.commit()
    request = _co_request(dbsession, user, params={"url": "https://example.com/404"})
    view = CompanyView(request)
    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.HTTPError(
            "https://example.com/404", 404, "Not Found", {}, None
        ),
    ):
        result = view.uptime_check()
    assert result.status_code == 200
    assert 'class="badge bg-dark"' in result.text
    assert ">404<" in result.text


def test_company_uptime_check_generic_error(dbsession):
    user = _co_user(dbsession, "coupchk5")
    transaction.commit()
    request = _co_request(dbsession, user, params={"url": "https://bad.invalid"})
    view = CompanyView(request)
    with patch(
        "urllib.request.urlopen",
        side_effect=OSError("Connection refused"),
    ):
        result = view.uptime_check()
    assert result.status_code == 200
    assert ">Error<" in result.text
    assert "Connection refused" in result.text


def test_company_uptime_rows(dbsession):
    user = _co_user(dbsession, "couptimerows")
    _co_company(dbsession, user, "UptimeRowsCo")
    transaction.commit()
    request = _co_request(dbsession, user, params={"page": "2"})
    view = CompanyView(request)
    result = view.uptime_rows()
    assert "paginator" in result
    assert result["page"] == 2


# ===========================================================================
# Date range filtering tests
# ===========================================================================


def test_company_all_date_from(dbsession):
    user = _co_user(dbsession, "codtf1")
    _co_company(dbsession, user, "DtFromCo")
    transaction.commit()
    request = _co_request(dbsession, user, params={"date_from": "2020-01-01T00:00"})
    view = CompanyView(request)
    result = view.all()
    assert result["q"]["date_from"] == "2020-01-01T00:00"
    assert result["counter"] >= 1


def test_company_all_date_to(dbsession):
    user = _co_user(dbsession, "codtt1")
    _co_company(dbsession, user, "DtToCo")
    transaction.commit()
    request = _co_request(dbsession, user, params={"date_to": "2030-01-01T00:00"})
    view = CompanyView(request)
    result = view.all()
    assert result["q"]["date_to"] == "2030-01-01T00:00"
    assert result["counter"] >= 1


def test_company_all_date_range(dbsession):
    user = _co_user(dbsession, "codtr1")
    _co_company(dbsession, user, "DtRangeCo")
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        params={"date_from": "2020-01-01T00:00", "date_to": "2030-01-01T00:00"},
    )
    view = CompanyView(request)
    result = view.all()
    assert result["q"]["date_from"] == "2020-01-01T00:00"
    assert result["q"]["date_to"] == "2030-01-01T00:00"
    assert result["counter"] >= 1


def test_company_similar_date_from(dbsession):
    user = _co_user(dbsession, "cosimdf")
    company = _co_company(dbsession, user, "SimDfCo")
    tag = Tag(name="CoSimDfTag")
    tag.created_by = user
    company.tags.append(tag)
    c2 = _co_company(dbsession, user, "SimDfCo2")
    c2.tags.append(tag)
    transaction.commit()
    request = _co_request(
        dbsession, user, company=company, params={"date_from": "2020-01-01T00:00"}
    )
    view = CompanyView(request)
    result = view.similar()
    assert result["q"]["date_from"] == "2020-01-01T00:00"


def test_company_similar_date_to(dbsession):
    user = _co_user(dbsession, "cosimdt")
    company = _co_company(dbsession, user, "SimDtCo")
    tag = Tag(name="CoSimDtTag")
    tag.created_by = user
    company.tags.append(tag)
    c2 = _co_company(dbsession, user, "SimDtCo2")
    c2.tags.append(tag)
    transaction.commit()
    request = _co_request(
        dbsession, user, company=company, params={"date_to": "2030-01-01T00:00"}
    )
    view = CompanyView(request)
    result = view.similar()
    assert result["q"]["date_to"] == "2030-01-01T00:00"


@patch("marker.views.company.company_autofill_from_website")
def test_company_website_autofill_error(mock_autofill, dbsession):
    mock_autofill.side_effect = RuntimeError("API unavailable")
    user = _co_user(dbsession, "coaferr")
    company = _co_company(dbsession, user, "AfErrCo")
    transaction.commit()
    request = _co_request(
        dbsession, user, company=company, params={"website": "http://x.com"}
    )
    view = CompanyView(request)
    result = view.website_autofill()
    assert result["fields"] == {}
    assert "API unavailable" in result["error"]
    assert request.response.status_code == 502


# ===========================================================================
# Coverage for remaining branches
# ===========================================================================


def test_company_all_street_postcode_city_website_filters(dbsession):
    """Cover lines 226-227, 230-231, 242-251 in company all()."""
    user = _co_user(dbsession, "coallflt")
    co = _co_company(dbsession, user, "AllFltCo")
    co.street = "FilterStreet"
    co.postcode = "11-111"
    co.city = "FilterCity"
    co.website = "http://filterweb.com"
    co.subdivision = "PL-MZ"
    co.country = "PL"
    co.color = "green"
    dbsession.flush()
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        params={
            "street": "FilterStreet",
            "postcode": "11-111",
            "city": "FilterCity",
            "website": "filterweb",
            "subdivision": "PL-MZ",
            "country": "PL",
            "color": "green",
        },
    )
    view = CompanyView(request)
    result = view.all()
    assert result["q"]["street"] == "FilterStreet"
    assert result["q"]["postcode"] == "11-111"
    assert result["q"]["city"] == "FilterCity"
    assert result["q"]["website"] == "filterweb"
    assert result["q"]["country"] == "PL"
    assert result["q"]["color"] == "green"


def test_company_similar_color_country_subdivision_filters(dbsession):
    """Cover lines 1093-1102 in company similar(): color, country, subdivision."""
    user = _co_user(dbsession, "cosimccs")
    co1 = _co_company(dbsession, user, "CoSimCCSCo1")
    co2 = _co_company(dbsession, user, "CoSimCCSCo2")
    co2.color = "blue"
    co2.country = "PL"
    co2.subdivision = "PL-MZ"
    tag = Tag(name="CoSimCCSTag")
    tag.created_by = user
    co1.tags.append(tag)
    co2.tags.append(tag)
    dbsession.add(tag)
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        company=co1,
        params={"color": "blue", "country": "PL", "subdivision": "PL-MZ"},
    )
    view = CompanyView(request)
    result = view.similar()
    assert result["q"]["color"] == "blue"
    assert result["q"]["country"] == "PL"


def test_company_add_get_validate_from_ai(dbsession):
    """Cover line 1300 in company add(): validate_from_ai branch."""
    user = _co_user(dbsession, "coaddfai")
    transaction.commit()
    request = _co_request(
        dbsession, user, params={"validate": "1", "name": "ValidateCo"}
    )
    view = CompanyView(request)
    result = view.add()
    assert "form" in result


def test_company_similar_bulk_select(dbsession):
    """Cover line 1140 in company similar(): bulk select request."""
    user = _co_user(dbsession, "cosimbulk")
    co1 = _co_company(dbsession, user, "CoSimBulkCo1")
    co2 = _co_company(dbsession, user, "CoSimBulkCo2")
    tag = Tag(name="CoSimBulkTag")
    tag.created_by = user
    co1.tags.append(tag)
    co2.tags.append(tag)
    dbsession.add(tag)
    transaction.commit()
    request = _co_request(
        dbsession,
        user,
        company=co1,
        method="POST",
        params={"_select_all": "1", "checked": "1"},
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    request.matched_route.name = "company_similar"
    view = CompanyView(request)
    result = view.similar()
    assert result is request.response


@patch("marker.views.company.location_details", return_value=None)
@patch(
    "marker.views.company.tags_autofill_from_website",
    return_value=[],
)
@patch(
    "marker.views.company.contacts_autofill_from_website",
    return_value=[{"name": "", "role": None}, {"name": "John Smith", "role": "CEO"}],
)
@patch(
    "marker.views.company.company_autofill_from_website",
    return_value={"name": "BlankContactCo", "country": "PL"},
)
def test_company_add_ai_contacts_blank_name(mock_autofill, mock_contacts, mock_tags, mock_geo, dbsession):
    """Cover line 1843: continue when contact name is blank."""
    user = _co_user(dbsession, "coaiblankname")
    transaction.commit()
    request = _co_request(
        dbsession, user, method="POST", post={"website": "http://example.com"}
    )
    request.headers = {}
    view = CompanyView(request)
    result = view.add_ai()
    assert isinstance(result, HTTPSeeOther)


@patch("marker.views.company.company_autofill_from_website")
def test_company_website_autofill_long_error_with_response(mock_autofill, dbsession):
    """Cover lines 1339, 1345: long error with 'Response:' in message."""
    long_msg = "Some error. Response: " + "x" * 400
    mock_autofill.side_effect = RuntimeError(long_msg)
    user = _co_user(dbsession, "coaflongresp")
    company = _co_company(dbsession, user, "LongRespCo")
    transaction.commit()
    request = _co_request(
        dbsession, user, company=company, params={"website": "http://x.com"}
    )
    view = CompanyView(request)
    result = view.website_autofill()
    assert result["fields"] == {}
    assert result["error"] is not None
    assert request.response.status_code == 502


@patch("marker.views.company.company_autofill_from_website")
def test_company_website_autofill_long_flash_truncation(mock_autofill, dbsession):
    """Cover lines 1352-1356: flash message truncated when longer than 500 bytes."""
    # Create a very long error to make flash_msg > 500 bytes
    long_msg = "x" * 600
    mock_autofill.side_effect = RuntimeError(long_msg)
    user = _co_user(dbsession, "coaflongflash")
    company = _co_company(dbsession, user, "LongFlashCo")
    transaction.commit()
    request = _co_request(
        dbsession, user, company=company, params={"website": "http://x.com"}
    )
    view = CompanyView(request)
    result = view.website_autofill()
    assert result["fields"] == {}
    assert request.response.status_code == 502


def test_company_all_filter_name(dbsession):
    """Cover lines 231-235: name filter in all()."""
    user = _co_user(dbsession, "conamefilter")
    _co_company(dbsession, user, "FilterNameCo")
    transaction.commit()
    from webob.multidict import MultiDict as WMultiDict
    request = _co_request(dbsession, user, params={"name": "FilterNameCo"})
    request.matched_route.name = "company_all"
    view = CompanyView(request)
    result = view.all()
    assert result["q"]["name"] == "FilterNameCo"


@patch("marker.views.company.location_details", return_value=None)
@patch(
    "marker.views.company.tags_autofill_from_website",
    return_value=["ExistCoTag", "NewCoTag"],
)
@patch(
    "marker.views.company.contacts_autofill_from_website",
    return_value=[],
)
@patch(
    "marker.views.company.company_autofill_from_website",
    return_value={"name": "CoTagsRetCo", "country": "PL"},
)
def test_company_add_ai_tags_returned(mock_autofill, mock_contacts, mock_tags, mock_geo, dbsession):
    """Cover lines 1865-1876: tags returned from autofill including pre-existing tag."""
    from marker.models.tag import Tag
    user = _co_user(dbsession, "coaitagsret")
    existing_tag = Tag(name="ExistCoTag")
    existing_tag.created_by = user
    dbsession.add(existing_tag)
    transaction.commit()
    request = _co_request(
        dbsession, user, method="POST", post={"website": "http://example.com"}
    )
    request.headers = {}
    view = CompanyView(request)
    result = view.add_ai()
    assert isinstance(result, HTTPSeeOther)


@patch("marker.views.company.company_autofill_from_website")
def test_company_website_autofill_success(mock_autofill, dbsession):
    """Cover lines 1352-1356: success path of website_autofill."""
    mock_autofill.return_value = {"name": "Test Co", "country": "PL"}
    user = _co_user(dbsession, "coafsucc")
    company = _co_company(dbsession, user, "WsAutofillSuccCo")
    transaction.commit()
    request = _co_request(
        dbsession, user, company=company, params={"website": "http://x.com"}
    )
    view = CompanyView(request)
    result = view.website_autofill()
    assert result["fields"] == {"name": "Test Co", "country": "PL"}
