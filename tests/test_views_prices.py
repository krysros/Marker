"""Tests for marker/views/prices.py"""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest
import transaction
from webob.multidict import MultiDict

import marker.forms.ts
from marker.models.association import Activity
from marker.models.company import Company
from marker.models.project import Project
from marker.models.user import User
from marker.views.prices import PricesView
from tests.conftest import DummyRequestWithIdentity


@pytest.fixture(autouse=True)
def patch_translationstring_str(monkeypatch):
    monkeypatch.setattr(
        marker.forms.ts.TranslationString, "__str__", lambda self: self.msg
    )
    yield


def _user(dbsession, name="valuser"):
    user = User(
        name=name,
        fullname="Test User",
        email=f"{name}@e.com",
        role="admin",
        password="pw",
    )
    dbsession.add(user)
    dbsession.flush()
    return user


def _make_activity(
    dbsession,
    user,
    company_name="ValCo",
    project_name="ValProj",
    stage="",
    role="investor",
    currency="PLN",
    value_net=None,
    value_gross=None,
    usable_area=None,
):
    company = Company(
        name=company_name,
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    company.created_by = user
    dbsession.add(company)
    dbsession.flush()

    project = Project(
        name=project_name,
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="",
        color="",
        deadline=None,
        stage=stage,
        delivery_method="",
        usable_area=usable_area,
    )
    project.created_by = user
    dbsession.add(project)
    dbsession.flush()

    activity = Activity(
        company_id=company.id,
        project_id=project.id,
        stage=stage,
        role=role,
        currency=currency,
        value_net=value_net,
        value_gross=value_gross,
    )
    dbsession.add(activity)
    dbsession.flush()
    return company, project, activity


def _req(dbsession, user, params=None):
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = "GET"
    request.GET = MultiDict(params or {})
    request.POST = MultiDict()
    request.params = MultiDict(params or {})
    request.locale_name = "en"
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/prices"
    request.session = MagicMock()
    request.response = MagicMock()
    request.response.headers = {}
    request.context = MagicMock()
    request.matchdict = {}
    request.matched_route = MagicMock()
    request.matched_route.name = "prices_all"
    request.environ = {}
    request.environ["webob._parsed_get_vars"] = (MultiDict(params or {}), MultiDict())
    request.environ["webob._parsed_post_vars"] = (MultiDict(), MultiDict())
    request.environ["webob._parsed_params_vars"] = (
        MultiDict(params or {}),
        MultiDict(),
    )
    request.path_qs = "/prices"
    request.query_string = ""
    request.referrer = "/home"
    request.headers = {}
    return request


def test_values_all_empty(dbsession):
    user = _user(dbsession)
    transaction.commit()
    request = _req(dbsession, user)
    view = PricesView(request)
    result = view.all()
    assert "paginator" in result
    assert "counter" in result
    assert result["counter"] == 0


def test_values_all_with_activity(dbsession):
    user = _user(dbsession, "valwithact")
    _make_activity(
        dbsession, user, "ValWithActCo", "ValWithActProj", value_net=Decimal("100000")
    )
    transaction.commit()
    request = _req(dbsession, user)
    view = PricesView(request)
    result = view.all()
    assert result["counter"] == 1
    assert len(result["paginator"]) == 1


def test_values_all_unit_prices_calculated(dbsession):
    user = _user(dbsession, "valunitprice")
    _make_activity(
        dbsession,
        user,
        "ValUnitCo",
        "ValUnitProj",
        value_net=Decimal("1000.00"),
        value_gross=Decimal("1230.00"),
        usable_area=Decimal("10.00"),
    )
    transaction.commit()
    request = _req(dbsession, user)
    view = PricesView(request)
    result = view.all()
    row = result["paginator"][0]
    assert row.unit_price_net == Decimal("100.00")
    assert row.unit_price_gross == Decimal("123.00")


def test_values_all_no_unit_prices_without_usable_area(dbsession):
    user = _user(dbsession, "valnousarea")
    _make_activity(
        dbsession,
        user,
        "ValNoUsAreaCo",
        "ValNoUsAreaProj",
        value_net=Decimal("100000"),
        value_gross=Decimal("123000"),
        usable_area=None,
    )
    transaction.commit()
    request = _req(dbsession, user)
    view = PricesView(request)
    result = view.all()
    row = result["paginator"][0]
    assert row.unit_price_net is None
    assert row.unit_price_gross is None


def test_values_all_filter_stage(dbsession):
    user = _user(dbsession, "valfstage")
    _make_activity(dbsession, user, "ValFStageCo", "ValFStageProj", stage="tender")
    _make_activity(
        dbsession, user, "ValFStageCo2", "ValFStageProj2", stage="construction"
    )
    transaction.commit()
    request = _req(dbsession, user, params={"stage": "tender"})
    view = PricesView(request)
    result = view.all()
    assert result["counter"] == 1
    assert result["q"]["stage"] == "tender"


def test_values_all_filter_role(dbsession):
    user = _user(dbsession, "valfrole")
    _make_activity(dbsession, user, "ValFRoleCo", "ValFRoleProj", role="investor")
    _make_activity(dbsession, user, "ValFRoleCo2", "ValFRoleProj2", role="designer")
    transaction.commit()
    request = _req(dbsession, user, params={"role": "investor"})
    view = PricesView(request)
    result = view.all()
    assert result["counter"] == 1
    assert result["q"]["role"] == "investor"


def test_values_all_filter_currency(dbsession):
    user = _user(dbsession, "valfcurr")
    _make_activity(dbsession, user, "ValFCurrCo", "ValFCurrProj", currency="PLN")
    _make_activity(dbsession, user, "ValFCurrCo2", "ValFCurrProj2", currency="EUR")
    transaction.commit()
    request = _req(dbsession, user, params={"currency": "PLN"})
    view = PricesView(request)
    result = view.all()
    assert result["counter"] == 1
    assert result["q"]["currency"] == "PLN"


def test_values_all_no_unit_price_when_values_none(dbsession):
    user = _user(dbsession, "valnoval")
    _make_activity(
        dbsession,
        user,
        "ValNoValCo",
        "ValNoValProj",
        value_net=None,
        value_gross=None,
        usable_area=Decimal("100.00"),
    )
    transaction.commit()
    request = _req(dbsession, user)
    view = PricesView(request)
    result = view.all()
    row = result["paginator"][0]
    assert row.unit_price_net is None
    assert row.unit_price_gross is None


# --- sorting tests ---


def test_sort_project_name_asc(dbsession):
    user = _user(dbsession, "sortpnasc")
    _make_activity(dbsession, user, "SortPNAsc_Co1", "Zebra Project")
    _make_activity(dbsession, user, "SortPNAsc_Co2", "Apple Project")
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "project_name", "order": "asc"})
    result = PricesView(request).all()
    names = [r.project.name for r in result["paginator"]]
    assert names == sorted(names)


def test_sort_project_name_desc(dbsession):
    user = _user(dbsession, "sortpndesc")
    _make_activity(dbsession, user, "SortPNDesc_Co1", "Zebra Project D")
    _make_activity(dbsession, user, "SortPNDesc_Co2", "Apple Project D")
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "project_name", "order": "desc"})
    result = PricesView(request).all()
    names = [r.project.name for r in result["paginator"]]
    assert names == sorted(names, reverse=True)


def test_sort_company_name_asc(dbsession):
    user = _user(dbsession, "sortcoasc")
    _make_activity(dbsession, user, "Zebra Company", "SortCo_P1")
    _make_activity(dbsession, user, "Apple Company", "SortCo_P2")
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "company_name", "order": "asc"})
    result = PricesView(request).all()
    names = [r.company.name for r in result["paginator"]]
    assert names == sorted(names)


def test_sort_company_name_desc(dbsession):
    user = _user(dbsession, "sortcodesc")
    _make_activity(dbsession, user, "Zebra Company D", "SortCoD_P1")
    _make_activity(dbsession, user, "Apple Company D", "SortCoD_P2")
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "company_name", "order": "desc"})
    result = PricesView(request).all()
    names = [r.company.name for r in result["paginator"]]
    assert names == sorted(names, reverse=True)


def test_sort_currency_asc(dbsession):
    user = _user(dbsession, "sortcurasc")
    _make_activity(dbsession, user, "SortCurAsc_Co1", "SortCurAsc_P1", currency="USD")
    _make_activity(dbsession, user, "SortCurAsc_Co2", "SortCurAsc_P2", currency="EUR")
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "currency", "order": "asc"})
    result = PricesView(request).all()
    currencies = [r.activity.currency for r in result["paginator"]]
    assert currencies == sorted(currencies)


def test_sort_currency_desc(dbsession):
    user = _user(dbsession, "sortcurdesc")
    _make_activity(
        dbsession, user, "SortCurDesc_Co1", "SortCurDesc_P1", currency="USD"
    )
    _make_activity(
        dbsession, user, "SortCurDesc_Co2", "SortCurDesc_P2", currency="EUR"
    )
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "currency", "order": "desc"})
    result = PricesView(request).all()
    currencies = [r.activity.currency for r in result["paginator"]]
    assert currencies == sorted(currencies, reverse=True)


def test_sort_stage_asc(dbsession):
    # stage codes stored in DB: "construction", "tender"
    # English msgids (used by test translate stub): "Construction", "Tender"
    # Alphabetical: Construction (C) < Tender (T) → construction first when asc
    user = _user(dbsession, "sortstageasc")
    _make_activity(
        dbsession, user, "SortStAsc_Co1", "SortStAsc_P1", stage="construction"
    )
    _make_activity(
        dbsession, user, "SortStAsc_Co2", "SortStAsc_P2", stage="tender"
    )
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "stage", "order": "asc"})
    result = PricesView(request).all()
    stages = [r.activity.stage for r in result["paginator"]]
    assert stages == ["construction", "tender"]


def test_sort_stage_desc(dbsession):
    user = _user(dbsession, "sortstagedesc")
    _make_activity(
        dbsession, user, "SortStDesc_Co1", "SortStDesc_P1", stage="construction"
    )
    _make_activity(
        dbsession, user, "SortStDesc_Co2", "SortStDesc_P2", stage="tender"
    )
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "stage", "order": "desc"})
    result = PricesView(request).all()
    stages = [r.activity.stage for r in result["paginator"]]
    assert stages == ["tender", "construction"]


def test_sort_role_asc(dbsession):
    # role codes stored in DB: "designer", "investor"
    # English msgids (used by test translate stub): "Designer", "Investor"
    # Alphabetical: Designer (D) < Investor (I) → designer first when asc
    user = _user(dbsession, "sortroleasc")
    _make_activity(
        dbsession, user, "SortRoAsc_Co1", "SortRoAsc_P1", role="designer"
    )
    _make_activity(
        dbsession, user, "SortRoAsc_Co2", "SortRoAsc_P2", role="investor"
    )
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "role", "order": "asc"})
    result = PricesView(request).all()
    roles = [r.activity.role for r in result["paginator"]]
    assert roles == ["designer", "investor"]


def test_sort_role_desc(dbsession):
    user = _user(dbsession, "sortroledesc")
    _make_activity(
        dbsession, user, "SortRoDesc_Co1", "SortRoDesc_P1", role="designer"
    )
    _make_activity(
        dbsession, user, "SortRoDesc_Co2", "SortRoDesc_P2", role="investor"
    )
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "role", "order": "desc"})
    result = PricesView(request).all()
    roles = [r.activity.role for r in result["paginator"]]
    assert roles == ["investor", "designer"]


def test_sort_value_net_asc(dbsession):
    user = _user(dbsession, "sortvnasc")
    _make_activity(
        dbsession, user, "SortVNAsc_Co1", "SortVNAsc_P1", value_net=Decimal("5000")
    )
    _make_activity(
        dbsession, user, "SortVNAsc_Co2", "SortVNAsc_P2", value_net=Decimal("1000")
    )
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "value_net", "order": "asc"})
    result = PricesView(request).all()
    values = [r.activity.value_net for r in result["paginator"]]
    assert values == sorted(values)


def test_sort_value_net_desc(dbsession):
    user = _user(dbsession, "sortvndesc")
    _make_activity(
        dbsession, user, "SortVNDesc_Co1", "SortVNDesc_P1", value_net=Decimal("5000")
    )
    _make_activity(
        dbsession, user, "SortVNDesc_Co2", "SortVNDesc_P2", value_net=Decimal("1000")
    )
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "value_net", "order": "desc"})
    result = PricesView(request).all()
    values = [r.activity.value_net for r in result["paginator"]]
    assert values == sorted(values, reverse=True)


def test_sort_value_gross_asc(dbsession):
    user = _user(dbsession, "sortvgasc")
    _make_activity(
        dbsession,
        user,
        "SortVGAsc_Co1",
        "SortVGAsc_P1",
        value_gross=Decimal("6150"),
    )
    _make_activity(
        dbsession,
        user,
        "SortVGAsc_Co2",
        "SortVGAsc_P2",
        value_gross=Decimal("1230"),
    )
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "value_gross", "order": "asc"})
    result = PricesView(request).all()
    values = [r.activity.value_gross for r in result["paginator"]]
    assert values == sorted(values)


def test_sort_value_gross_desc(dbsession):
    user = _user(dbsession, "sortvgdesc")
    _make_activity(
        dbsession,
        user,
        "SortVGDesc_Co1",
        "SortVGDesc_P1",
        value_gross=Decimal("6150"),
    )
    _make_activity(
        dbsession,
        user,
        "SortVGDesc_Co2",
        "SortVGDesc_P2",
        value_gross=Decimal("1230"),
    )
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "value_gross", "order": "desc"})
    result = PricesView(request).all()
    values = [r.activity.value_gross for r in result["paginator"]]
    assert values == sorted(values, reverse=True)


def test_sort_unit_price_net_asc(dbsession):
    user = _user(dbsession, "sortupnasc")
    # unit_price_net = value_net / usable_area: 200/10=20 vs 500/100=5 → 5 first
    _make_activity(
        dbsession,
        user,
        "SortUPNAsc_Co1",
        "SortUPNAsc_P1",
        value_net=Decimal("200"),
        usable_area=Decimal("10"),
    )
    _make_activity(
        dbsession,
        user,
        "SortUPNAsc_Co2",
        "SortUPNAsc_P2",
        value_net=Decimal("500"),
        usable_area=Decimal("100"),
    )
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "unit_price_net", "order": "asc"})
    result = PricesView(request).all()
    unit_prices = [r.unit_price_net for r in result["paginator"]]
    assert unit_prices == sorted(unit_prices)


def test_sort_unit_price_net_desc(dbsession):
    user = _user(dbsession, "sortupndesc")
    # unit_price_net: 200/10=20 vs 500/100=5 → 20 first
    _make_activity(
        dbsession,
        user,
        "SortUPNDesc_Co1",
        "SortUPNDesc_P1",
        value_net=Decimal("200"),
        usable_area=Decimal("10"),
    )
    _make_activity(
        dbsession,
        user,
        "SortUPNDesc_Co2",
        "SortUPNDesc_P2",
        value_net=Decimal("500"),
        usable_area=Decimal("100"),
    )
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "unit_price_net", "order": "desc"})
    result = PricesView(request).all()
    unit_prices = [r.unit_price_net for r in result["paginator"]]
    assert unit_prices == sorted(unit_prices, reverse=True)


def test_sort_unit_price_gross_asc(dbsession):
    user = _user(dbsession, "sortupgasc")
    # unit_price_gross: 246/10=24.6 vs 615/100=6.15 → 6.15 first
    _make_activity(
        dbsession,
        user,
        "SortUPGAsc_Co1",
        "SortUPGAsc_P1",
        value_gross=Decimal("246"),
        usable_area=Decimal("10"),
    )
    _make_activity(
        dbsession,
        user,
        "SortUPGAsc_Co2",
        "SortUPGAsc_P2",
        value_gross=Decimal("615"),
        usable_area=Decimal("100"),
    )
    transaction.commit()
    request = _req(
        dbsession, user, params={"sort": "unit_price_gross", "order": "asc"}
    )
    result = PricesView(request).all()
    unit_prices = [r.unit_price_gross for r in result["paginator"]]
    assert unit_prices == sorted(unit_prices)


def test_sort_unit_price_gross_desc(dbsession):
    user = _user(dbsession, "sortupgdesc")
    # unit_price_gross: 246/10=24.6 vs 615/100=6.15 → 24.6 first
    _make_activity(
        dbsession,
        user,
        "SortUPGDesc_Co1",
        "SortUPGDesc_P1",
        value_gross=Decimal("246"),
        usable_area=Decimal("10"),
    )
    _make_activity(
        dbsession,
        user,
        "SortUPGDesc_Co2",
        "SortUPGDesc_P2",
        value_gross=Decimal("615"),
        usable_area=Decimal("100"),
    )
    transaction.commit()
    request = _req(
        dbsession, user, params={"sort": "unit_price_gross", "order": "desc"}
    )
    result = PricesView(request).all()
    unit_prices = [r.unit_price_gross for r in result["paginator"]]
    assert unit_prices == sorted(unit_prices, reverse=True)


# ===========================================================================
# Filter branches in all() – lines 55, 98-167
# ===========================================================================


def test_prices_all_filter_stage(dbsession):
    user = _user(dbsession, "filterstage")
    _make_activity(dbsession, user, "FiltStCo", "FiltStProj", stage="tender")
    transaction.commit()
    request = _req(dbsession, user, params={"stage": "tender"})
    result = PricesView(request).all()
    assert result["q"]["stage"] == "tender"


def test_prices_all_filter_role(dbsession):
    user = _user(dbsession, "filterrole")
    _make_activity(dbsession, user, "FiltRoCo", "FiltRoProj", role="investor")
    transaction.commit()
    request = _req(dbsession, user, params={"role": "investor"})
    result = PricesView(request).all()
    assert result["q"]["role"] == "investor"


def test_prices_all_filter_currency(dbsession):
    user = _user(dbsession, "filtercurr")
    _make_activity(dbsession, user, "FiltCurrCo", "FiltCurrProj", currency="EUR")
    transaction.commit()
    request = _req(dbsession, user, params={"currency": "EUR"})
    result = PricesView(request).all()
    assert result["q"]["currency"] == "EUR"


def test_prices_all_filter_value_net_range(dbsession):
    user = _user(dbsession, "filtervnrange")
    _make_activity(
        dbsession, user, "FiltVNCo", "FiltVNProj",
        value_net=Decimal("500"), value_gross=Decimal("615")
    )
    transaction.commit()
    request = _req(
        dbsession, user,
        params={"value_net_from": "100", "value_net_to": "1000"}
    )
    result = PricesView(request).all()
    assert result["q"]["value_net_from"] == "100"
    assert result["q"]["value_net_to"] == "1000"


def test_prices_all_filter_value_gross_range(dbsession):
    user = _user(dbsession, "filtervgrange")
    _make_activity(
        dbsession, user, "FiltVGCo", "FiltVGProj",
        value_net=Decimal("500"), value_gross=Decimal("615")
    )
    transaction.commit()
    request = _req(
        dbsession, user,
        params={"value_gross_from": "100", "value_gross_to": "1000"}
    )
    result = PricesView(request).all()
    assert result["q"]["value_gross_from"] == "100"
    assert result["q"]["value_gross_to"] == "1000"


def test_prices_all_filter_unit_price_net_range(dbsession):
    user = _user(dbsession, "filtrupnrange")
    _make_activity(
        dbsession, user, "FiltUPNCo", "FiltUPNProj",
        value_net=Decimal("1000"), usable_area=Decimal("100")
    )
    transaction.commit()
    request = _req(
        dbsession, user,
        params={"unit_price_net_from": "5", "unit_price_net_to": "50"}
    )
    result = PricesView(request).all()
    assert result["q"]["unit_price_net_from"] == "5"
    assert result["q"]["unit_price_net_to"] == "50"


def test_prices_all_filter_unit_price_gross_range(dbsession):
    user = _user(dbsession, "filtrupgrange")
    _make_activity(
        dbsession, user, "FiltUPGCo", "FiltUPGProj",
        value_gross=Decimal("1230"), usable_area=Decimal("100")
    )
    transaction.commit()
    request = _req(
        dbsession, user,
        params={"unit_price_gross_from": "5", "unit_price_gross_to": "50"}
    )
    result = PricesView(request).all()
    assert result["q"]["unit_price_gross_from"] == "5"
    assert result["q"]["unit_price_gross_to"] == "50"


def test_prices_all_filter_object_category(dbsession):
    user = _user(dbsession, "filtrobcat")
    _, proj, _ = _make_activity(dbsession, user, "FiltObCatCo", "FiltObCatProj")
    proj.object_category = "uslugi"
    dbsession.flush()
    transaction.commit()
    request = _req(dbsession, user, params={"object_category": "uslugi"})
    result = PricesView(request).all()
    assert result["q"]["object_category"] == "uslugi"


# ===========================================================================
# export() – lines 252-382
# ===========================================================================


def test_prices_export_basic(dbsession):
    user = _user(dbsession, "exportbasic")
    _make_activity(
        dbsession, user, "ExportBasicCo", "ExportBasicProj",
        value_net=Decimal("100"), value_gross=Decimal("123"),
        usable_area=Decimal("50")
    )
    transaction.commit()
    request = _req(dbsession, user)
    result = PricesView(request).export()
    assert "vnd.openxmlformats-officedocument" in result.content_type


def test_prices_export_with_filters(dbsession):
    user = _user(dbsession, "exportfilt")
    _, proj, _ = _make_activity(
        dbsession, user, "ExportFiltCo", "ExportFiltProj",
        value_net=Decimal("200"), value_gross=Decimal("246"),
        currency="PLN", role="investor", stage="tender",
        usable_area=Decimal("100")
    )
    proj.object_category = "uslugi"
    dbsession.flush()
    transaction.commit()
    request = _req(
        dbsession, user,
        params={
            "stage": "tender",
            "role": "investor",
            "currency": "PLN",
            "value_net_from": "100",
            "value_net_to": "500",
            "value_gross_from": "100",
            "value_gross_to": "500",
            "unit_price_net_from": "0",
            "unit_price_net_to": "50",
            "unit_price_gross_from": "0",
            "unit_price_gross_to": "50",
            "object_category": "uslugi",
            "sort": "value_net",
            "order": "desc",
        }
    )
    result = PricesView(request).export()
    assert "vnd.openxmlformats-officedocument" in result.content_type


def test_prices_export_ods(dbsession):
    user = _user(dbsession, "exportods")
    _make_activity(dbsession, user, "ExportOdsCo", "ExportOdsProj")
    transaction.commit()
    request = _req(dbsession, user, params={"format": "ods"})
    result = PricesView(request).export()
    assert "oasis.opendocument" in result.content_type


def test_prices_all_invalid_order(dbsession):
    """Cover line 55: _order reset when invalid value passed."""
    user = _user(dbsession, "invalidorder")
    transaction.commit()
    request = _req(dbsession, user, params={"order": "invalid"})
    result = PricesView(request).all()
    assert result["q"]["order"] == "asc"


def test_prices_all_invalid_decimal_filters(dbsession):
    """Cover except/pass branches (lines 101-102, 108-109, 115-116, 122-123,
    132-133, 142-143, 152-153, 162-163): invalid decimal values are silently ignored."""
    user = _user(dbsession, "invaliddec")
    transaction.commit()
    request = _req(dbsession, user, params={
        "value_net_from": "abc",
        "value_net_to": "abc",
        "value_gross_from": "abc",
        "value_gross_to": "abc",
        "unit_price_net_from": "abc",
        "unit_price_net_to": "abc",
        "unit_price_gross_from": "abc",
        "unit_price_gross_to": "abc",
    })
    result = PricesView(request).all()
    assert "value_net_from" not in result["q"]


def test_prices_export_invalid_order(dbsession):
    """Cover line 307 in export(): _order reset when invalid value passed."""
    user = _user(dbsession, "exportinvord")
    transaction.commit()
    request = _req(dbsession, user, params={"order": "invalid"})
    result = PricesView(request).export()
    assert "vnd.openxmlformats-officedocument" in result.content_type


def test_prices_export_invalid_decimal_filters(dbsession):
    """Cover except/pass branches 272-273, 283-284 in export()."""
    user = _user(dbsession, "exportinvdec")
    _make_activity(dbsession, user, "ExpInvDecCo", "ExpInvDecProj")
    transaction.commit()
    request = _req(dbsession, user, params={
        "value_net_from": "bad",
        "unit_price_net_from": "bad",
    })
    result = PricesView(request).export()
    assert "vnd.openxmlformats-officedocument" in result.content_type
