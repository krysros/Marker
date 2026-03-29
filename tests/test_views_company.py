from unittest.mock import MagicMock

from webob.multidict import MultiDict

from marker.models.company import Company
from marker.models.user import User
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
    import transaction

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
        # court removed
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
    user = User(
        name="testuser2",
        fullname="Test User2",
        email="test2@example.com",
        role="user",
        password="testpass2",
    )
    dbsession.add(user)
    import transaction

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

    # Add related objects
    from marker.models.tag import Tag
    from marker.models.project import Project
    from marker.models.comment import Comment
    from marker.models.user import User as MarkerUser
    from marker.models.association import Activity
    from marker.models.contact import Contact

    # Tags
    for i in range(3):
        tag = Tag(name=f"Tag{i}")
        dbsession.add(tag)
        company.tags.append(tag)
    dbsession.flush()

    # Projects (via Activity)
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
        company.projects.append(activity)
    dbsession.flush()

    # Contacts
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

    # Comments
    for i in range(5):
        comment = Comment(comment=f"Comment{i}")
        dbsession.add(comment)
        company.comments.append(comment)
    dbsession.flush()

    # Stars (each user stars a different company, but we check the counter on one)
    # Star: one user, one company
    star_user = MarkerUser(name="StarUser", fullname="U", email="star@ex.com", role="user", password="x")
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
    assert view.count_tags() == 10  # 3 + 7 (sim tags)
    assert view.count_projects() == 2
    assert view.count_contacts() == 4
    assert view.count_comments() == 5
    assert view.count_stars() == 1  # Only one user stars this company
    assert view.count_similar() >= 7  # number of similar companies (may be higher depending on implementation)
