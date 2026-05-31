import transaction
from webob.multidict import MultiDict
from unittest.mock import MagicMock
from marker.models.company import Company
from marker.models.project import Project
from marker.models.user import User
from marker.views.company import CompanyView
from marker.views.project import ProjectView
from tests.conftest import DummyRequestWithIdentity


def test_company_no_location_filter(dbsession):
    user = User(
        name="testuser_noloc",
        fullname="Test User Noloc",
        email="test_noloc@example.com",
        role="user",
        password="testpass_noloc",
    )
    dbsession.add(user)
    transaction.commit()

    # Company 1: Has latitude and longitude
    c1 = Company(
        name="CoWithLoc",
        street="Street 1",
        postcode="12345",
        city="City 1",
        subdivision="PL-MZ",
        country="PL",
        website=None,
        color="red",
        NIP=None,
        REGON=None,
        KRS=None,
    )
    c1.latitude = 52.2297
    c1.longitude = 21.0122

    # Company 2: Missing longitude (no location)
    c2 = Company(
        name="CoNoLong",
        street="Street 2",
        postcode="12345",
        city="City 2",
        subdivision="PL-MZ",
        country="PL",
        website=None,
        color="blue",
        NIP=None,
        REGON=None,
        KRS=None,
    )
    c2.latitude = 52.2297
    c2.longitude = None

    # Company 3: Missing both (no location)
    c3 = Company(
        name="CoNoLoc",
        street="Street 3",
        postcode="12345",
        city="City 3",
        subdivision="PL-MZ",
        country="PL",
        website=None,
        color="green",
        NIP=None,
        REGON=None,
        KRS=None,
    )
    c3.latitude = None
    c3.longitude = None

    # Company 4: Missing latitude (no location)
    c4 = Company(
        name="CoNoLat",
        street="Street 4",
        postcode="12345",
        city="City 4",
        subdivision="PL-MZ",
        country="PL",
        website=None,
        color="yellow",
        NIP=None,
        REGON=None,
        KRS=None,
    )
    c4.latitude = None
    c4.longitude = 21.0122

    dbsession.add_all([c1, c2, c3, c4])
    transaction.commit()

    # Test case 1: no_location = "1" -> Filter active
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.GET = MultiDict({"no_location": "1"})
    request.params = MultiDict({"no_location": "1"})
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
    names = [c.name for c in result["paginator"]]
    assert "CoNoLong" in names
    assert "CoNoLoc" in names
    assert "CoNoLat" in names
    assert "CoWithLoc" not in names

    # Test case 2: no_location not set -> No filter
    request_unfiltered = DummyRequestWithIdentity()
    request_unfiltered.dbsession = dbsession
    request_unfiltered.identity = user
    request_unfiltered.method = "GET"
    request_unfiltered.GET = MultiDict()
    request_unfiltered.params = MultiDict()
    request_unfiltered.locale_name = "en"
    request_unfiltered.translate = lambda x: x
    request_unfiltered.route_url = lambda *a, **kw: "/company"
    request_unfiltered.session = MagicMock()
    request_unfiltered.response = MagicMock()
    request_unfiltered.context = MagicMock()
    request_unfiltered.environ = {}
    request_unfiltered.environ["webob._parsed_get_vars"] = (MultiDict(), MultiDict())
    request_unfiltered.environ["webob._parsed_post_vars"] = (MultiDict(), MultiDict())
    request_unfiltered.environ["webob._parsed_params_vars"] = (MultiDict(), MultiDict())

    view_unfiltered = CompanyView(request_unfiltered)
    result_unfiltered = view_unfiltered.all()
    names_unfiltered = [c.name for c in result_unfiltered["paginator"]]
    assert "CoWithLoc" in names_unfiltered
    assert "CoNoLong" in names_unfiltered
    assert "CoNoLoc" in names_unfiltered
    assert "CoNoLat" in names_unfiltered


def test_project_no_location_filter(dbsession):
    user = User(
        name="testuser_noloc2",
        fullname="Test User Noloc2",
        email="test_noloc2@example.com",
        role="user",
        password="testpass_noloc2",
    )
    dbsession.add(user)
    transaction.commit()

    # Project 1: Has latitude and longitude
    p1 = Project(
        name="ProjWithLoc",
        street="Street 1",
        postcode="12345",
        city="City 1",
        subdivision="PL-MZ",
        country="PL",
        website=None,
        color="red",
        deadline=None,
        stage="draft",
        delivery_method="courier",
    )
    p1.latitude = 52.2297
    p1.longitude = 21.0122

    # Project 2: Missing longitude (no location)
    p2 = Project(
        name="ProjNoLong",
        street="Street 2",
        postcode="12345",
        city="City 2",
        subdivision="PL-MZ",
        country="PL",
        website=None,
        color="blue",
        deadline=None,
        stage="draft",
        delivery_method="courier",
    )
    p2.latitude = 52.2297
    p2.longitude = None

    # Project 3: Missing both (no location)
    p3 = Project(
        name="ProjNoLoc",
        street="Street 3",
        postcode="12345",
        city="City 3",
        subdivision="PL-MZ",
        country="PL",
        website=None,
        color="green",
        deadline=None,
        stage="draft",
        delivery_method="courier",
    )
    p3.latitude = None
    p3.longitude = None

    # Project 4: Missing latitude (no location)
    p4 = Project(
        name="ProjNoLat",
        street="Street 4",
        postcode="12345",
        city="City 4",
        subdivision="PL-MZ",
        country="PL",
        website=None,
        color="yellow",
        deadline=None,
        stage="draft",
        delivery_method="courier",
    )
    p4.latitude = None
    p4.longitude = 21.0122

    dbsession.add_all([p1, p2, p3, p4])
    transaction.commit()

    # Test case 1: no_location = "1" -> Filter active
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.GET = MultiDict({"no_location": "1"})
    request.params = MultiDict({"no_location": "1"})
    request.locale_name = "en"
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/project"
    request.session = MagicMock()
    request.response = MagicMock()
    request.context = MagicMock()
    request.environ = {}
    request.environ["webob._parsed_get_vars"] = (MultiDict(), MultiDict())
    request.environ["webob._parsed_post_vars"] = (MultiDict(), MultiDict())
    request.environ["webob._parsed_params_vars"] = (MultiDict(), MultiDict())

    view = ProjectView(request)
    result = view.all()
    assert "paginator" in result
    names = [p.name for p in result["paginator"]]
    assert "ProjNoLong" in names
    assert "ProjNoLoc" in names
    assert "ProjNoLat" in names
    assert "ProjWithLoc" not in names

    # Test case 2: no_location not set -> No filter
    request_unfiltered = DummyRequestWithIdentity()
    request_unfiltered.dbsession = dbsession
    request_unfiltered.identity = user
    request_unfiltered.method = "GET"
    request_unfiltered.GET = MultiDict()
    request_unfiltered.params = MultiDict()
    request_unfiltered.locale_name = "en"
    request_unfiltered.translate = lambda x: x
    request_unfiltered.route_url = lambda *a, **kw: "/project"
    request_unfiltered.session = MagicMock()
    request_unfiltered.response = MagicMock()
    request_unfiltered.context = MagicMock()
    request_unfiltered.environ = {}
    request_unfiltered.environ["webob._parsed_get_vars"] = (MultiDict(), MultiDict())
    request_unfiltered.environ["webob._parsed_post_vars"] = (MultiDict(), MultiDict())
    request_unfiltered.environ["webob._parsed_params_vars"] = (MultiDict(), MultiDict())

    view_unfiltered = ProjectView(request_unfiltered)
    result_unfiltered = view_unfiltered.all()
    names_unfiltered = [p.name for p in result_unfiltered["paginator"]]
    assert "ProjWithLoc" in names_unfiltered
    assert "ProjNoLong" in names_unfiltered
    assert "ProjNoLoc" in names_unfiltered
    assert "ProjNoLat" in names_unfiltered
