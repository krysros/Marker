from unittest.mock import MagicMock
from webob.multidict import MultiDict
from marker.models.user import User
from marker.models.company import Company
from marker.views.company import CompanyView
from tests.conftest import DummyRequestWithIdentity

def test_company_all_route_coverage(dbsession):
    user = User(
        name="testuser",
        fullname="Test User",
        email="test@example.com",
        role="user",
        password="testpass"
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
        court=None,
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
