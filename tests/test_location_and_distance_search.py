from unittest.mock import MagicMock, patch
import pytest
import transaction
from webob.multidict import MultiDict
from marker.models.company import Company
from marker.models.contact import Contact
from marker.models.project import Project
from marker.models.tag import Tag
from marker.models.user import User
from marker.views.company import CompanyView
from marker.views.project import ProjectView
from marker.views.contact import ContactView
from tests.conftest import DummyRequestWithIdentity


def make_test_request(dbsession, user, params=None):
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.GET = MultiDict(params or {})
    request.POST = MultiDict()
    request.params = MultiDict(params or {})
    request.locale_name = "en"
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/some-route"
    request.session = MagicMock()
    request.response = MagicMock()
    request.context = MagicMock()
    request.environ = {}
    request.environ["webob._parsed_get_vars"] = (MultiDict(params or {}), MultiDict())
    request.environ["webob._parsed_post_vars"] = (MultiDict(), MultiDict())
    request.environ["webob._parsed_params_vars"] = (
        MultiDict(params or {}),
        MultiDict(),
    )
    return request


@pytest.fixture
def test_data(dbsession):
    # Ensure there is a user
    user = User(
        name="testuser_loc",
        fullname="Location Test User",
        email="loc_test@example.com",
        role="user",
        password="testpassword",
    )
    user.companies_stars = []
    user.selected_companies = []
    user.selected_contacts = []
    user.selected_tags = []
    dbsession.add(user)

    # Tag to enable view_mode contacts toggle if needed
    tag = Tag(name="testtag")
    dbsession.add(tag)

    # Company with valid coordinates (Warsaw: 52.2297, 21.0122)
    company_warsaw = Company(
        name="Warsaw Company",
        street="Aleje Jerozolimskie",
        postcode="00-001",
        city="Warsaw",
        subdivision="PL-MZ",
        country="PL",
        website=None,
        color="red",
        NIP=None,
        REGON=None,
        KRS=None,
    )
    company_warsaw.latitude = 52.2297
    company_warsaw.longitude = 21.0122
    company_warsaw.tags.append(tag)
    dbsession.add(company_warsaw)

    # Company outside Warsaw (Krakow: 50.0647, 19.9450 - about 250km away)
    company_krakow = Company(
        name="Krakow Company",
        street="Florianska",
        postcode="31-019",
        city="Krakow",
        subdivision="PL-MA",
        country="PL",
        website=None,
        color="blue",
        NIP=None,
        REGON=None,
        KRS=None,
    )
    company_krakow.latitude = 50.0647
    company_krakow.longitude = 19.9450
    company_krakow.tags.append(tag)
    dbsession.add(company_krakow)

    # Company with missing coordinates
    company_nocoords = Company(
        name="No Coords Company",
        street="Unknown",
        postcode="00-000",
        city="Unknown",
        subdivision="PL-MZ",
        country="PL",
        website=None,
        color="green",
        NIP=None,
        REGON=None,
        KRS=None,
    )
    company_nocoords.tags.append(tag)
    dbsession.add(company_nocoords)

    # Project with valid coordinates (Warsaw: 52.2297, 21.0122)
    project_warsaw = Project(
        name="Warsaw Project",
        street="Aleje Jerozolimskie",
        postcode="00-001",
        city="Warsaw",
        subdivision="PL-MZ",
        country="PL",
        website=None,
        color="red",
        deadline=None,
        stage="draft",
        delivery_method="courier",
    )
    project_warsaw.latitude = 52.2297
    project_warsaw.longitude = 21.0122
    project_warsaw.tags.append(tag)
    dbsession.add(project_warsaw)

    # Project outside Warsaw (Krakow: 50.0647, 19.9450)
    project_krakow = Project(
        name="Krakow Project",
        street="Florianska",
        postcode="31-019",
        city="Krakow",
        subdivision="PL-MA",
        country="PL",
        website=None,
        color="blue",
        deadline=None,
        stage="draft",
        delivery_method="courier",
    )
    project_krakow.latitude = 50.0647
    project_krakow.longitude = 19.9450
    project_krakow.tags.append(tag)
    dbsession.add(project_krakow)

    # Project with missing coordinates
    project_nocoords = Project(
        name="No Coords Project",
        street="Unknown",
        postcode="00-000",
        city="Unknown",
        subdivision="PL-MZ",
        country="PL",
        website=None,
        color="green",
        deadline=None,
        stage="draft",
        delivery_method="courier",
    )
    project_nocoords.tags.append(tag)
    dbsession.add(project_nocoords)

    # Contact associated with Warsaw Company
    contact_warsaw_co = Contact(
        "Warsaw Co Contact",
        "employee",
        None,
        None,
        None,
    )
    contact_warsaw_co.company = company_warsaw
    dbsession.add(contact_warsaw_co)

    # Contact associated with Krakow Company
    contact_krakow_co = Contact(
        "Krakow Co Contact",
        "employee",
        None,
        None,
        None,
    )
    contact_krakow_co.company = company_krakow
    dbsession.add(contact_krakow_co)

    # Contact associated with Warsaw Project
    contact_warsaw_proj = Contact(
        "Warsaw Proj Contact",
        "employee",
        None,
        None,
        None,
    )
    contact_warsaw_proj.project = project_warsaw
    dbsession.add(contact_warsaw_proj)

    # Contact associated with Krakow Project
    contact_krakow_proj = Contact(
        "Krakow Proj Contact",
        "employee",
        None,
        None,
        None,
    )
    contact_krakow_proj.project = project_krakow
    dbsession.add(contact_krakow_proj)

    # Contact with no coordinates (either company has no coords or no association)
    contact_nocoords = Contact(
        "No Coords Contact",
        "employee",
        None,
        None,
        None,
    )
    dbsession.add(contact_nocoords)

    # Contact associated with company_nocoords (has tag but no coords)
    contact_co_nocoords = Contact(
        "Co No Coords Contact",
        "employee",
        None,
        None,
        None,
    )
    contact_co_nocoords.company = company_nocoords
    dbsession.add(contact_co_nocoords)

    # Contact associated with project_nocoords (has tag but no coords)
    contact_proj_nocoords = Contact(
        "Proj No Coords Contact",
        "employee",
        None,
        None,
        None,
    )
    contact_proj_nocoords.project = project_nocoords
    dbsession.add(contact_proj_nocoords)

    transaction.commit()
    return user, tag


# Helper to mock location response
def mock_location_warsaw(q):
    if q == "Warszawa":
        return {"lat": 52.2297, "lon": 21.0122}
    return None


@patch("marker.views.company.location", side_effect=mock_location_warsaw)
def test_company_view_location_filtering(mock_loc, dbsession, test_data):
    user, tag = test_data

    # 1. Test filtering by location parameter (Warsaw, 50km radius)
    request = make_test_request(
        dbsession, user, {"location": "Warszawa", "distance": "50", "tag": tag.name}
    )
    view = CompanyView(request)
    res = view.all()
    assert "paginator" in res
    assert any(c.name == "Warsaw Company" for c in res["paginator"])
    assert not any(c.name == "Krakow Company" for c in res["paginator"])
    assert not any(c.name == "No Coords Company" for c in res["paginator"])

    # 2. Test filtering by lat/lon directly (Warsaw coords)
    request_lat_lon = make_test_request(
        dbsession,
        user,
        {"lat": "52.2297", "lon": "21.0122", "distance": "50", "tag": tag.name},
    )
    view_lat_lon = CompanyView(request_lat_lon)
    res_lat_lon = view_lat_lon.all()
    assert any(c.name == "Warsaw Company" for c in res_lat_lon["paginator"])
    assert not any(c.name == "Krakow Company" for c in res_lat_lon["paginator"])

    # 3. Test invalid lat/lon exceptions handling
    request_invalid_coords = make_test_request(
        dbsession, user, {"lat": "abc", "lon": "def", "distance": "50", "tag": tag.name}
    )
    view_invalid = CompanyView(request_invalid_coords)
    res_invalid = view_invalid.all()
    # It should fall back to no filtering, showing everything
    assert len(res_invalid["paginator"]) >= 3

    # 4. Test invalid distance value exceptions handling
    request_invalid_dist = make_test_request(
        dbsession,
        user,
        {
            "lat": "52.2297",
            "lon": "21.0122",
            "distance": "invalid_dist",
            "tag": tag.name,
        },
    )
    view_invalid_dist = CompanyView(request_invalid_dist)
    res_invalid_dist = view_invalid_dist.all()
    # Should fallback to default 50km
    assert any(c.name == "Warsaw Company" for c in res_invalid_dist["paginator"])
    assert not any(c.name == "Krakow Company" for c in res_invalid_dist["paginator"])

    # 5. Test view contacts mode in company view with location
    request_contacts = make_test_request(
        dbsession,
        user,
        {"location": "Warszawa", "distance": "50", "tag": tag.name, "view": "contacts"},
    )
    view_contacts = CompanyView(request_contacts)
    res_contacts = view_contacts.all()
    assert any(c.name == "Warsaw Co Contact" for c in res_contacts["paginator"])
    assert not any(c.name == "Krakow Co Contact" for c in res_contacts["paginator"])

    # 6. Test location query returning empty result (unresolved address)
    request_empty_loc = make_test_request(
        dbsession, user, {"location": "NowhereLand", "tag": tag.name}
    )
    view_empty_loc = CompanyView(request_empty_loc)
    res_empty_loc = view_empty_loc.all()
    assert len(res_empty_loc["paginator"]) >= 3


@patch("marker.views.project.location", side_effect=mock_location_warsaw)
def test_project_view_location_filtering(mock_loc, dbsession, test_data):
    user, tag = test_data

    # 1. Test projects filtering by location parameter (Warsaw, 50km radius)
    request = make_test_request(
        dbsession, user, {"location": "Warszawa", "distance": "50", "tag": tag.name}
    )
    view = ProjectView(request)
    res = view.all()
    assert "paginator" in res
    assert any(p.name == "Warsaw Project" for p in res["paginator"])
    assert not any(p.name == "Krakow Project" for p in res["paginator"])

    # 2. Test projects filtering by lat/lon directly (Warsaw coords)
    request_lat_lon = make_test_request(
        dbsession,
        user,
        {"lat": "52.2297", "lon": "21.0122", "distance": "50", "tag": tag.name},
    )
    view_lat_lon = ProjectView(request_lat_lon)
    res_lat_lon = view_lat_lon.all()
    assert any(p.name == "Warsaw Project" for p in res_lat_lon["paginator"])
    assert not any(p.name == "Krakow Project" for p in res_lat_lon["paginator"])

    # 3. Test invalid lat/lon exceptions handling
    request_invalid_coords = make_test_request(
        dbsession, user, {"lat": "abc", "lon": "def", "distance": "50", "tag": tag.name}
    )
    view_invalid = ProjectView(request_invalid_coords)
    res_invalid = view_invalid.all()
    assert len(res_invalid["paginator"]) >= 3

    # 4. Test invalid distance value exceptions handling
    request_invalid_dist = make_test_request(
        dbsession,
        user,
        {
            "lat": "52.2297",
            "lon": "21.0122",
            "distance": "invalid_dist",
            "tag": tag.name,
        },
    )
    view_invalid_dist = ProjectView(request_invalid_dist)
    res_invalid_dist = view_invalid_dist.all()
    assert any(p.name == "Warsaw Project" for p in res_invalid_dist["paginator"])
    assert not any(p.name == "Krakow Project" for p in res_invalid_dist["paginator"])

    # 5. Test view contacts mode in project view with location
    request_contacts = make_test_request(
        dbsession,
        user,
        {"location": "Warszawa", "distance": "50", "tag": tag.name, "view": "contacts"},
    )
    view_contacts = ProjectView(request_contacts)
    res_contacts = view_contacts.all()
    assert any(c.name == "Warsaw Proj Contact" for c in res_contacts["paginator"])
    assert not any(c.name == "Krakow Proj Contact" for c in res_contacts["paginator"])


@patch("marker.views.contact.location", side_effect=mock_location_warsaw)
def test_contact_view_location_filtering(mock_loc, dbsession, test_data):
    user, tag = test_data

    # 1. Test contacts filtering by location parameter (Warsaw, 50km radius)
    request = make_test_request(
        dbsession,
        user,
        {
            "location": "Warszawa",
            "distance": "50",
            "tag": tag.name,
            "target": "contacts",
        },
    )
    view = ContactView(request)
    res = view.search_tags_results()
    assert "paginator" in res
    assert any(c.name == "Warsaw Co Contact" for c in res["paginator"])
    assert any(c.name == "Warsaw Proj Contact" for c in res["paginator"])
    assert not any(c.name == "Krakow Co Contact" for c in res["paginator"])
    assert not any(c.name == "Krakow Proj Contact" for c in res["paginator"])

    # 2. Test contacts filtering by lat/lon directly (Warsaw coords)
    request_lat_lon = make_test_request(
        dbsession,
        user,
        {
            "lat": "52.2297",
            "lon": "21.0122",
            "distance": "50",
            "tag": tag.name,
            "target": "contacts",
        },
    )
    view_lat_lon = ContactView(request_lat_lon)
    res_lat_lon = view_lat_lon.search_tags_results()
    assert any(c.name == "Warsaw Co Contact" for c in res_lat_lon["paginator"])
    assert any(c.name == "Warsaw Proj Contact" for c in res_lat_lon["paginator"])
    assert not any(c.name == "Krakow Co Contact" for c in res_lat_lon["paginator"])

    # 3. Test invalid lat/lon exceptions handling
    request_invalid_coords = make_test_request(
        dbsession,
        user,
        {
            "lat": "abc",
            "lon": "def",
            "distance": "50",
            "tag": tag.name,
            "target": "contacts",
        },
    )
    view_invalid = ContactView(request_invalid_coords)
    res_invalid = view_invalid.search_tags_results()
    assert len(res_invalid["paginator"]) >= 4

    # 4. Test invalid distance value exceptions handling
    request_invalid_dist = make_test_request(
        dbsession,
        user,
        {
            "lat": "52.2297",
            "lon": "21.0122",
            "distance": "invalid_dist",
            "tag": tag.name,
            "target": "contacts",
        },
    )
    view_invalid_dist = ContactView(request_invalid_dist)
    res_invalid_dist = view_invalid_dist.search_tags_results()
    assert any(c.name == "Warsaw Co Contact" for c in res_invalid_dist["paginator"])

    # 5. Test location query returning empty result (unresolved address)
    request_empty_loc = make_test_request(
        dbsession,
        user,
        {"location": "NowhereLand", "tag": tag.name, "target": "contacts"},
    )
    view_empty_loc = ContactView(request_empty_loc)
    res_empty_loc = view_empty_loc.search_tags_results()
    assert len(res_empty_loc["paginator"]) >= 4


# Test exceptional scenario: geodesic raising an exception during distance calculation
@patch("marker.views.company.location", side_effect=mock_location_warsaw)
@patch("marker.views.company.geodesic")
def test_company_view_geodesic_exception(mock_geodesic, mock_loc, dbsession, test_data):
    user, tag = test_data
    # Force geodesic to raise an exception
    mock_geodesic.side_effect = Exception("Calculation failed")

    request = make_test_request(
        dbsession, user, {"location": "Warszawa", "distance": "50", "tag": tag.name}
    )
    view = CompanyView(request)
    res = view.all()
    # The results should not fail; instead the failed calculation items are skipped
    assert "paginator" in res
    assert len(res["paginator"]) == 0


@patch("marker.views.project.location", side_effect=mock_location_warsaw)
@patch("marker.views.project.geodesic")
def test_project_view_geodesic_exception(mock_geodesic, mock_loc, dbsession, test_data):
    user, tag = test_data
    mock_geodesic.side_effect = Exception("Calculation failed")

    request = make_test_request(
        dbsession, user, {"location": "Warszawa", "distance": "50", "tag": tag.name}
    )
    view = ProjectView(request)
    res = view.all()
    assert "paginator" in res
    assert len(res["paginator"]) == 0


@patch("marker.views.contact.location", side_effect=mock_location_warsaw)
@patch("marker.views.contact.geodesic")
def test_contact_view_geodesic_exception(mock_geodesic, mock_loc, dbsession, test_data):
    user, tag = test_data
    mock_geodesic.side_effect = Exception("Calculation failed")

    request = make_test_request(
        dbsession,
        user,
        {
            "location": "Warszawa",
            "distance": "50",
            "tag": tag.name,
            "target": "contacts",
        },
    )
    view = ContactView(request)
    res = view.search_tags_results()
    assert "paginator" in res
    assert len(res["paginator"]) == 0


# Test bulk selection mode scenario
@patch("marker.views.company.location", side_effect=mock_location_warsaw)
@patch("marker.views.company.is_bulk_select_request", return_value=True)
def test_company_view_bulk_select(mock_bulk, mock_loc, dbsession, test_data):
    user, tag = test_data

    # 1. Bulk select Companies view
    request = make_test_request(
        dbsession,
        user,
        {
            "location": "Warszawa",
            "distance": "50",
            "tag": tag.name,
            "view": "companies",
        },
    )
    view = CompanyView(request)
    res = view.all()
    # Should execute handle_bulk_selection logic (which returns a WebOb Response or similar)
    assert res is not None

    # 2. Bulk select Contacts view in Company view
    request_contacts = make_test_request(
        dbsession,
        user,
        {"location": "Warszawa", "distance": "50", "tag": tag.name, "view": "contacts"},
    )
    view_contacts = CompanyView(request_contacts)
    res_contacts = view_contacts.all()
    assert res_contacts is not None


@patch("marker.views.project.location", side_effect=mock_location_warsaw)
@patch("marker.views.project.is_bulk_select_request", return_value=True)
def test_project_view_bulk_select(mock_bulk, mock_loc, dbsession, test_data):
    user, tag = test_data

    # 1. Bulk select Projects view
    request = make_test_request(
        dbsession,
        user,
        {"location": "Warszawa", "distance": "50", "tag": tag.name, "view": "projects"},
    )
    view = ProjectView(request)
    res = view.all()
    assert res is not None

    # 2. Bulk select Contacts view in Project view
    request_contacts = make_test_request(
        dbsession,
        user,
        {"location": "Warszawa", "distance": "50", "tag": tag.name, "view": "contacts"},
    )
    view_contacts = ProjectView(request_contacts)
    res_contacts = view_contacts.all()
    assert res_contacts is not None


@patch("marker.views.contact.location", side_effect=mock_location_warsaw)
@patch("marker.views.contact.is_bulk_select_request", return_value=True)
def test_contact_view_bulk_select(mock_bulk, mock_loc, dbsession, test_data):
    user, tag = test_data

    request = make_test_request(
        dbsession,
        user,
        {
            "location": "Warszawa",
            "distance": "50",
            "tag": tag.name,
            "target": "contacts",
        },
    )
    view = ContactView(request)
    res = view.search_tags_results()
    assert res is not None


@patch("marker.views.company.location", side_effect=mock_location_warsaw)
@patch("marker.views.company.geodesic")
def test_company_view_geodesic_exception_extended(
    mock_geodesic, mock_loc, dbsession, test_data
):
    user, tag = test_data
    mock_geodesic.side_effect = Exception("Calculation failed")

    # 1. Normal mode with view=contacts
    request_contacts = make_test_request(
        dbsession,
        user,
        {"location": "Warszawa", "distance": "50", "tag": tag.name, "view": "contacts"},
    )
    view = CompanyView(request_contacts)
    res = view.all()
    assert "paginator" in res
    assert len(res["paginator"]) == 0

    # 2. Bulk select mode with view=companies
    with patch("marker.views.company.is_bulk_select_request", return_value=True):
        request_bulk_co = make_test_request(
            dbsession, user, {"location": "Warszawa", "distance": "50", "tag": tag.name}
        )
        view = CompanyView(request_bulk_co)
        res = view.all()
        assert res is not None

    # 3. Bulk select mode with view=contacts
    with patch("marker.views.company.is_bulk_select_request", return_value=True):
        request_bulk_contacts = make_test_request(
            dbsession,
            user,
            {
                "location": "Warszawa",
                "distance": "50",
                "tag": tag.name,
                "view": "contacts",
            },
        )
        view = CompanyView(request_bulk_contacts)
        res = view.all()
        assert res is not None


@patch("marker.views.project.location", side_effect=mock_location_warsaw)
@patch("marker.views.project.geodesic")
def test_project_view_geodesic_exception_extended(
    mock_geodesic, mock_loc, dbsession, test_data
):
    user, tag = test_data
    mock_geodesic.side_effect = Exception("Calculation failed")

    # 1. Normal mode with view=contacts
    request_contacts = make_test_request(
        dbsession,
        user,
        {"location": "Warszawa", "distance": "50", "tag": tag.name, "view": "contacts"},
    )
    view = ProjectView(request_contacts)
    res = view.all()
    assert "paginator" in res
    assert len(res["paginator"]) == 0

    # 2. Bulk select mode with view=projects
    with patch("marker.views.project.is_bulk_select_request", return_value=True):
        request_bulk_proj = make_test_request(
            dbsession, user, {"location": "Warszawa", "distance": "50", "tag": tag.name}
        )
        view = ProjectView(request_bulk_proj)
        res = view.all()
        assert res is not None

    # 3. Bulk select mode with view=contacts
    with patch("marker.views.project.is_bulk_select_request", return_value=True):
        request_bulk_contacts = make_test_request(
            dbsession,
            user,
            {
                "location": "Warszawa",
                "distance": "50",
                "tag": tag.name,
                "view": "contacts",
            },
        )
        view = ProjectView(request_bulk_contacts)
        res = view.all()
        assert res is not None


@patch("marker.views.contact.location", side_effect=mock_location_warsaw)
@patch("marker.views.contact.geodesic")
def test_contact_view_geodesic_exception_extended(
    mock_geodesic, mock_loc, dbsession, test_data
):
    user, tag = test_data
    mock_geodesic.side_effect = Exception("Calculation failed")

    # Bulk select mode
    with patch("marker.views.contact.is_bulk_select_request", return_value=True):
        request = make_test_request(
            dbsession,
            user,
            {
                "location": "Warszawa",
                "distance": "50",
                "tag": tag.name,
                "target": "contacts",
            },
        )
        view = ContactView(request)
        res = view.search_tags_results()
        assert res is not None
