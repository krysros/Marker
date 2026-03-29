from unittest.mock import MagicMock

import pytest
import transaction
from webob.multidict import MultiDict

from marker.models.association import Activity
from marker.models.comment import Comment
from marker.models.company import Company
from marker.models.contact import Contact
from marker.models.project import Project
from marker.models.tag import Tag
from marker.models.user import User
from marker.models.user import User as MarkerUser
from marker.views.company import CompanyView
from tests.conftest import DummyRequestWithIdentity


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
        # Test website_autofill()
        request.method = "GET"
        assert "fields" in view.website_autofill()
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
