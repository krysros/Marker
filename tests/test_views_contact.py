"""Tests for marker/views/contact.py"""

import io
from unittest.mock import MagicMock, patch

import pytest
import transaction
from pyramid.httpexceptions import HTTPFound, HTTPSeeOther
from webob.multidict import MultiDict

import marker.forms.ts
from marker.models.company import Company
from marker.models.contact import Contact
from marker.models.project import Project
from marker.models.tag import Tag
from marker.models.user import User
from marker.views.contact import ContactView
from tests.conftest import DummyRequestWithIdentity


@pytest.fixture(autouse=True)
def patch_translationstring_str(monkeypatch):
    monkeypatch.setattr(
        marker.forms.ts.TranslationString, "__str__", lambda self: self.msg
    )
    yield


def _make_user(dbsession, name="contuser"):
    user = User(
        name=name, fullname="U", email=f"{name}@e.com", role="admin", password="pw"
    )
    dbsession.add(user)
    dbsession.flush()
    return user


def _make_contact(dbsession, user, name="TestContact", company=None, project=None):
    contact = Contact(name=name, role="dev", phone="123", email="a@b.com", color="")
    contact.created_by = user
    if company:
        contact.company = company
    if project:
        contact.project = project
    dbsession.add(contact)
    dbsession.flush()
    return contact


def _make_company(dbsession, user, name="ContTestCo"):
    company = Company(
        name=name,
        street="S",
        postcode="00-000",
        city="City",
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
    return company


def _make_project(dbsession, user, name="ContTestProj"):
    project = Project(
        name=name,
        street="S",
        postcode="00-000",
        city="City",
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
    return project


def _make_request(dbsession, user, contact=None, method="GET", params=None, post=None):
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = method
    request.GET = MultiDict(params or {})
    request.POST = MultiDict(post or {})
    request.params = MultiDict(params or {})
    request.locale_name = "en"
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/contact"
    request.session = MagicMock()
    request.response = MagicMock()
    request.response.headers = {}
    request.context = MagicMock()
    if contact:
        request.context.contact = contact
    request.matchdict = {}
    request.matched_route = MagicMock()
    request.matched_route.name = "contact_all"
    request.environ = {}
    request.environ["webob._parsed_get_vars"] = (MultiDict(params or {}), MultiDict())
    request.environ["webob._parsed_post_vars"] = (MultiDict(post or {}), MultiDict())
    request.environ["webob._parsed_params_vars"] = (
        MultiDict(params or {}),
        MultiDict(),
    )
    request.path_qs = "/contact"
    request.query_string = ""
    request.referrer = "/home"
    return request


# --- all() ---


def test_contact_all_default(dbsession):
    user = _make_user(dbsession)
    _make_contact(dbsession, user)
    transaction.commit()
    request = _make_request(dbsession, user)
    view = ContactView(request)
    result = view.all()
    assert "paginator" in result
    assert "counter" in result


def test_contact_all_with_filters(dbsession):
    user = _make_user(dbsession, "contfilt")
    _make_contact(dbsession, user, "FilterContact")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "name": "Filter",
            "role": "dev",
            "phone": "123",
            "email": "a@b",
            "color": "",
            "sort": "name",
            "order": "asc",
        },
    )
    view = ContactView(request)
    result = view.all()
    assert result["q"]["name"] == "Filter"


def test_contact_all_category_companies(dbsession):
    user = _make_user(dbsession, "contcatco")
    company = _make_company(dbsession, user)
    _make_contact(dbsession, user, "CoCont", company=company)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={"category": "companies", "country": "PL", "subdivision": "PL-14"},
    )
    view = ContactView(request)
    result = view.all()
    assert "paginator" in result


def test_contact_all_category_projects(dbsession):
    user = _make_user(dbsession, "contcatpr")
    project = _make_project(dbsession, user)
    _make_contact(dbsession, user, "PrCont", project=project)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={"category": "projects", "country": "PL", "subdivision": "PL-14"},
    )
    view = ContactView(request)
    result = view.all()
    assert "paginator" in result


def test_contact_all_no_category_country(dbsession):
    """Default category with country/subdivision filter (no specific category)."""
    user = _make_user(dbsession, "contnocatcountry")
    company = _make_company(dbsession, user)
    _make_contact(dbsession, user, "NoCatCont", company=company)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={"country": "PL", "subdivision": "PL-14"},
    )
    view = ContactView(request)
    result = view.all()
    assert result["q"]["country"] == "PL"


def test_contact_all_sort_city_projects(dbsession):
    """Sort by city with category=projects."""
    user = _make_user(dbsession, "contsortcityproj")
    project = _make_project(dbsession, user)
    _make_contact(dbsession, user, "SortCityPrCont", project=project)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _make_request(
            dbsession,
            user,
            params={"category": "projects", "sort": "city", "order": order},
        )
        view = ContactView(request)
        result = view.all()
        assert result["q"]["sort"] == "city"


def test_contact_all_sort_city_companies(dbsession):
    """Sort by city with category=companies."""
    user = _make_user(dbsession, "contsortcityco")
    company = _make_company(dbsession, user)
    _make_contact(dbsession, user, "SortCityCoCont", company=company)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _make_request(
            dbsession,
            user,
            params={"category": "companies", "sort": "city", "order": order},
        )
        view = ContactView(request)
        result = view.all()
        assert result["q"]["sort"] == "city"


def test_contact_all_sort_city_no_category(dbsession):
    """Sort by city/country/subdivision without specific category (coalesce branch)."""
    user = _make_user(dbsession, "contsortcitynocat")
    company = _make_company(dbsession, user)
    _make_contact(dbsession, user, "SortCityNoCatCont", company=company)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _make_request(
            dbsession,
            user,
            params={"sort": "city", "order": order},
        )
        view = ContactView(request)
        result = view.all()
        assert result["q"]["sort"] == "city"


def test_contact_all_sort_category_name(dbsession):
    """Sort by category_name (coalesce Project.name/Company.name)."""
    user = _make_user(dbsession, "contsortcatnm")
    company = _make_company(dbsession, user)
    _make_contact(dbsession, user, "SortCatNmCont", company=company)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _make_request(
            dbsession,
            user,
            params={"sort": "category_name", "order": order},
        )
        view = ContactView(request)
        result = view.all()
        assert result["q"]["sort"] == "category_name"


def test_contact_all_sort_default_desc(dbsession):
    """Standard sort field with desc order."""
    user = _make_user(dbsession, "contsortdefdesc")
    _make_contact(dbsession, user, "SortDefDescCont")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={"sort": "name", "order": "desc"},
    )
    view = ContactView(request)
    result = view.all()
    assert result["q"]["order"] == "desc"


# --- count() ---


def test_contact_count(dbsession):
    user = _make_user(dbsession, "contcount")
    _make_contact(dbsession, user, "CountContact")
    transaction.commit()
    request = _make_request(dbsession, user)
    view = ContactView(request)
    result = view.count()
    assert isinstance(result, int)
    assert result >= 1


# --- view() ---


@patch("marker.views.contact.vcard_template")
def test_contact_view(mock_vcard_tmpl, dbsession):
    mock_template = MagicMock()
    mock_template.render.return_value = "BEGIN:VCARD\nEND:VCARD"
    mock_vcard_tmpl.return_value = mock_template
    user = _make_user(dbsession, "contview")
    contact = _make_contact(dbsession, user, "ViewContact")
    transaction.commit()
    request = _make_request(dbsession, user, contact=contact)
    view = ContactView(request)
    result = view.view()
    assert "contact" in result
    assert result["title"] == "ViewContact"


# --- edit() ---


def test_contact_edit_get(dbsession):
    user = _make_user(dbsession, "conteditget")
    contact = _make_contact(dbsession, user, "EditGetCont")
    transaction.commit()
    request = _make_request(dbsession, user, contact=contact, method="GET", post={})
    view = ContactView(request)
    result = view.edit()
    assert "form" in result


def test_contact_edit_post(dbsession):
    user = _make_user(dbsession, "conteditpost")
    contact = _make_contact(dbsession, user, "EditPostCont")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        contact=contact,
        method="POST",
        post={
            "name": "EditPostCont",
            "role": "mgr",
            "phone": "999",
            "email": "new@e.com",
            "color": "",
        },
    )
    view = ContactView(request)
    result = view.edit()
    assert isinstance(result, HTTPSeeOther)


# --- delete() ---


def test_contact_delete(dbsession):
    user = _make_user(dbsession, "contdel")
    contact = _make_contact(dbsession, user, "DelCont")
    transaction.commit()
    request = _make_request(dbsession, user, contact=contact, method="POST")
    request.response = MagicMock()
    view = ContactView(request)
    result = view.delete()
    assert result.status_code == 303


# --- del_row() ---


def test_contact_del_row(dbsession):
    user = _make_user(dbsession, "contdelrow")
    contact = _make_contact(dbsession, user, "DelRowCont")
    transaction.commit()
    request = _make_request(dbsession, user, contact=contact, method="POST")
    view = ContactView(request)
    result = view.del_row()
    assert result == ""


# --- search() ---


def test_contact_search_get(dbsession):
    user = _make_user(dbsession, "contsearchget")
    transaction.commit()
    request = _make_request(dbsession, user, method="GET", post={})
    view = ContactView(request)
    result = view.search()
    assert "form" in result


def test_contact_search_post(dbsession):
    user = _make_user(dbsession, "contsearchpost")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        method="POST",
        post={
            "name": "SearchCont",
            "role": "",
            "phone": "",
            "email": "",
            "color": "",
        },
    )
    view = ContactView(request)
    result = view.search()
    assert isinstance(result, HTTPSeeOther)


# --- search_tags() ---


def test_contact_search_tags_get(dbsession):
    user = _make_user(dbsession, "contsearchtagsget")
    transaction.commit()
    request = _make_request(
        dbsession, user, method="GET", params={"target": "contacts", "tag": "TagA"}
    )
    view = ContactView(request)
    result = view.search_tags()
    assert "tags" in result
    assert result["target"] == "contacts"


def test_contact_search_tags_post(dbsession):
    user = _make_user(dbsession, "contsearchtagspost")
    transaction.commit()
    request = _make_request(
        dbsession, user, method="POST", params={"target": "contacts", "tag": "TagA"}
    )
    view = ContactView(request)
    result = view.search_tags()
    assert isinstance(result, HTTPSeeOther)


# --- search_tags_results() ---


def test_contact_search_tags_results_no_tags(dbsession):
    user = _make_user(dbsession, "contstrnotags")
    transaction.commit()
    request = _make_request(dbsession, user, params={"target": "contacts"})
    view = ContactView(request)
    result = view.search_tags_results()
    assert isinstance(result, HTTPSeeOther)


def test_contact_search_tags_results_companies_redirect(dbsession):
    user = _make_user(dbsession, "contstrco")
    transaction.commit()
    request = _make_request(
        dbsession, user, params={"target": "companies", "tag": "T1"}
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert isinstance(result, HTTPSeeOther)


def test_contact_search_tags_results_projects_redirect(dbsession):
    user = _make_user(dbsession, "contstrpr")
    transaction.commit()
    request = _make_request(dbsession, user, params={"target": "projects", "tag": "T1"})
    view = ContactView(request)
    result = view.search_tags_results()
    assert isinstance(result, HTTPSeeOther)


def test_contact_search_tags_results_contacts(dbsession):
    user = _make_user(dbsession, "contstrcon")
    company = _make_company(dbsession, user)
    tag = Tag(name="ContSTRTag")
    tag.created_by = user
    dbsession.add(tag)
    company.tags.append(tag)
    _make_contact(dbsession, user, "STRContact", company=company)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "ContSTRTag",
            "sort": "name",
            "order": "asc",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert "paginator" in result
    assert "counter" in result


def test_contact_search_tags_results_sort_city(dbsession):
    """Geographic sort in search_tags_results."""
    user = _make_user(dbsession, "contstrsortcity")
    company = _make_company(dbsession, user)
    tag = Tag(name="CitySTRTag")
    tag.created_by = user
    dbsession.add(tag)
    company.tags.append(tag)
    _make_contact(dbsession, user, "CitySTRCont", company=company)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "CitySTRTag",
            "sort": "city",
            "order": "desc",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["sort"] == "city"


def test_contact_search_tags_get_with_operator(dbsession):
    user = _make_user(dbsession, "contsearchtagsop")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        method="GET",
        params={"target": "contacts", "tag": "TagX", "tag_operator": "and"},
    )
    view = ContactView(request)
    result = view.search_tags()
    assert result["tag_operator"] == "and"


def test_contact_search_tags_results_and_operator_companies_redirect(dbsession):
    user = _make_user(dbsession, "contstrandcored")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={"target": "companies", "tag": "T1", "tag_operator": "and"},
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert isinstance(result, HTTPSeeOther)


def test_contact_search_tags_results_and_operator_contacts(dbsession):
    user = _make_user(dbsession, "contstrandcon")
    tag1 = Tag(name="ANDTag1")
    tag1.created_by = user
    tag2 = Tag(name="ANDTag2")
    tag2.created_by = user
    dbsession.add_all([tag1, tag2])
    company_both = _make_company(dbsession, user, "ANDCoBoth")
    company_both.tags.append(tag1)
    company_both.tags.append(tag2)
    company_one = _make_company(dbsession, user, "ANDCoOne")
    company_one.tags.append(tag1)
    contact_both = _make_contact(dbsession, user, "ANDContactBoth", company=company_both)
    _make_contact(dbsession, user, "ANDContactOne", company=company_one)
    transaction.commit()
    params = MultiDict([("target", "contacts"), ("tag", "ANDTag1"), ("tag", "ANDTag2"), ("tag_operator", "and")])
    request = _make_request(dbsession, user, params=params)
    view = ContactView(request)
    result = view.search_tags_results()
    contacts = list(result["paginator"])
    assert any(c.name == "ANDContactBoth" for c in contacts)
    assert not any(c.name == "ANDContactOne" for c in contacts)


# --- search_tags_input() ---


def test_contact_search_tags_input(dbsession):
    user = _make_user(dbsession, "contstagsinput")
    transaction.commit()
    request = _make_request(dbsession, user)
    view = ContactView(request)
    result = view.search_tags_input()
    assert "row_id" in result
    assert "value" in result


# --- search_tags_input_remove() ---


def test_contact_search_tags_input_remove(dbsession):
    user = _make_user(dbsession, "contstagsinputrm")
    transaction.commit()
    request = _make_request(dbsession, user)
    view = ContactView(request)
    result = view.search_tags_input_remove()


# ===========================================================================
# Phase 2 – remaining contact.py coverage gaps
# ===========================================================================


def test_contact_all_invalid_sort(dbsession):
    user = _make_user(dbsession, "continvsrt")
    transaction.commit()
    request = _make_request(dbsession, user, params={"sort": "INVALID"})
    view = ContactView(request)
    result = view.all()
    assert result["q"]["sort"] == "created_at"


def test_contact_all_filter_role_phone(dbsession):
    user = _make_user(dbsession, "controleph")
    co = _make_company(dbsession, user, "ContRolePhCo")
    _make_contact(dbsession, user, "ContRolePh", company=co)
    transaction.commit()
    request = _make_request(dbsession, user, params={"role": "dev", "phone": "123"})
    view = ContactView(request)
    result = view.all()
    assert result["q"]["role"] == "dev"
    assert result["q"]["phone"] == "123"


def test_contact_all_projects_country(dbsession):
    user = _make_user(dbsession, "contprojcntry")
    proj = _make_project(dbsession, user, "ContProjCntryP")
    _make_contact(dbsession, user, "ContProjCntryCont", project=proj)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "category": "projects",
            "country": "PL",
        },
    )
    view = ContactView(request)
    result = view.all()
    assert result["q"]["category"] == "projects"
    assert result["q"]["country"] == "PL"


def test_contact_all_no_category_country_subdivision(dbsession):
    user = _make_user(dbsession, "contncgeo")
    co = _make_company(dbsession, user, "ContNCGeoCo")
    _make_contact(dbsession, user, "ContNCGeoCont", company=co)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "country": "PL",
            "subdivision": "PL-14",
        },
    )
    view = ContactView(request)
    result = view.all()
    assert result["q"]["country"] == "PL"


def test_contact_all_filter_color(dbsession):
    user = _make_user(dbsession, "contcolor")
    co = _make_company(dbsession, user, "ContColorCo")
    c = Contact(name="ContColorCont", role="r", phone="1", email="x@e.com", color="red")
    c.created_by = user
    c.company = co
    dbsession.add(c)
    transaction.commit()
    request = _make_request(dbsession, user, params={"color": "red"})
    view = ContactView(request)
    result = view.all()
    assert result["q"]["color"] == "red"


def test_contact_view_vcard(dbsession):
    user = _make_user(dbsession, "contvcard")
    co = _make_company(dbsession, user, "ContVcardCo")
    contact = _make_contact(dbsession, user, "ContVcardCont", company=co)
    contact_id = contact.id
    transaction.commit()
    request = _make_request(dbsession, user)
    request.matched_route.name = "contact_view"
    contact = dbsession.get(Contact, contact_id)
    request.context.contact = contact
    view = ContactView(request)
    result = view.view()
    assert "vcard" in result


def test_contact_search_tags_results_invalid_sort_order(dbsession):
    user = _make_user(dbsession, "contstaginvsrt")
    tag = Tag(name="InvSortTag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "InvSortCo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "InvSortCont", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "InvSortTag",
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["sort"] == "created_at"


def test_contact_search_tags_results_sort_city_projects(dbsession):
    user = _make_user(dbsession, "contstcityp")
    tag = Tag(name="CityPTag")
    tag.created_by = user
    dbsession.add(tag)
    proj = _make_project(dbsession, user, "CityPProj")
    tag.projects.append(proj)
    _make_contact(dbsession, user, "CityPCont", project=proj)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "CityPTag",
            "sort": "city",
            "order": "asc",
            "category": "projects",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["sort"] == "city"


def test_contact_search_tags_results_sort_city_companies(dbsession):
    user = _make_user(dbsession, "contstcityco")
    tag = Tag(name="CityCTag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "CityCCo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "CityCC", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "CityCTag",
            "sort": "city",
            "order": "desc",
            "category": "companies",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["sort"] == "city"


def test_contact_search_tags_results_sort_city_no_category(dbsession):
    user = _make_user(dbsession, "contstcitync")
    tag = Tag(name="CityNCTag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "CityNCCo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "CityNCCont", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "CityNCTag",
            "sort": "city",
            "order": "asc",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["sort"] == "city"


def test_contact_search_tags_results_sort_category_name(dbsession):
    user = _make_user(dbsession, "contstcatnm")
    tag = Tag(name="CatNmTag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "CatNmCo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "CatNmCont", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "CatNmTag",
            "sort": "category_name",
            "order": "asc",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["sort"] == "category_name"


def test_contact_search_tags_results_cat_companies_country(dbsession):
    user = _make_user(dbsession, "contstrccountry")
    tag = Tag(name="CoCntryTag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "CoCntryCo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "CoCntryCont", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "CoCntryTag",
            "category": "companies",
            "country": "PL",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["category"] == "companies"
    assert result["q"]["country"] == "PL"


def test_contact_search_tags_results_cat_companies_subdivision(dbsession):
    user = _make_user(dbsession, "contstrccsub")
    tag = Tag(name="CoSubTag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "CoSubCo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "CoSubCont", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "CoSubTag",
            "category": "companies",
            "subdivision": "PL-14",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["category"] == "companies"


def test_contact_search_tags_results_cat_projects_country(dbsession):
    user = _make_user(dbsession, "contstrpjcntry")
    tag = Tag(name="PjCntryTag")
    tag.created_by = user
    dbsession.add(tag)
    proj = _make_project(dbsession, user, "PjCntryProj")
    tag.projects.append(proj)
    _make_contact(dbsession, user, "PjCntryCont", project=proj)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "PjCntryTag",
            "category": "projects",
            "country": "PL",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["category"] == "projects"
    assert result["q"]["country"] == "PL"


def test_contact_search_tags_results_cat_projects_subdivision(dbsession):
    user = _make_user(dbsession, "contstrpjsub")
    tag = Tag(name="PjSubTag")
    tag.created_by = user
    dbsession.add(tag)
    proj = _make_project(dbsession, user, "PjSubProj")
    tag.projects.append(proj)
    _make_contact(dbsession, user, "PjSubCont", project=proj)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "PjSubTag",
            "category": "projects",
            "subdivision": "PL-14",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["category"] == "projects"


def test_contact_search_tags_results_no_cat_country(dbsession):
    user = _make_user(dbsession, "contstrnccntry")
    tag = Tag(name="NcCntryTag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "NcCntryCo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "NcCntryCont", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "NcCntryTag",
            "country": "PL",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["country"] == "PL"


def test_contact_search_tags_results_no_cat_subdivision(dbsession):
    user = _make_user(dbsession, "contstrncsub")
    tag = Tag(name="NcSubTag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "NcSubCo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "NcSubCont", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "NcSubTag",
            "subdivision": "PL-14",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert "subdivision" in result["q"]


def test_contact_search_tags_results_color_filter(dbsession):
    user = _make_user(dbsession, "contstrcolor")
    tag = Tag(name="ColorFTag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "ColorFCo")
    tag.companies.append(co)
    c = _make_contact(dbsession, user, "ColorFCont", company=co)
    c.color = "red"
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "ColorFTag",
            "color": "red",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["color"] == "red"


# ===========================================================================
# unassigned() – full branch coverage
# ===========================================================================


def test_contact_unassigned_with_filters_and_asc_sort(dbsession):
    import datetime

    user = _make_user(dbsession, "contunassfilt")
    unassigned = _make_contact(dbsession, user, "UnassignedMatch")
    unassigned.role = "manager"
    unassigned.phone = "555"
    unassigned.email = "u@x.com"
    unassigned.color = "red"

    co = _make_company(dbsession, user, "AssignedCo")
    _make_contact(dbsession, user, "AssignedContact", company=co)
    transaction.commit()

    now = datetime.datetime.now()
    date_from = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
    date_to = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")

    request = _make_request(
        dbsession,
        user,
        params={
            "name": "Unassigned",
            "role": "manager",
            "phone": "555",
            "email": "u@x.com",
            "color": "red",
            "date_from": date_from,
            "date_to": date_to,
            "sort": "name",
            "order": "asc",
        },
    )
    view = ContactView(request)
    result = view.unassigned()

    assert result["q"]["sort"] == "name"
    assert result["q"]["order"] == "asc"
    assert result["counter"] >= 1
    assert all(c.company_id is None and c.project_id is None for c in result["paginator"])


def test_contact_unassigned_invalid_sort_and_order_fallback(dbsession):
    user = _make_user(dbsession, "contunassinv")
    _make_contact(dbsession, user, "FallbackContact")
    transaction.commit()

    request = _make_request(
        dbsession,
        user,
        params={"sort": "bad_sort", "order": "bad_order"},
    )
    view = ContactView(request)
    result = view.unassigned()

    assert result["q"]["sort"] == "created_at"
    assert result["q"]["order"] == "desc"


def test_contact_unassigned_bulk_selection_request(dbsession):
    user = _make_user(dbsession, "contunassbulk")
    _make_contact(dbsession, user, "BulkUnassigned")
    transaction.commit()

    request = _make_request(
        dbsession,
        user,
        method="POST",
        params={"_select_all": "1", "checked": "1"},
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = ContactView(request)
    result = view.unassigned()

    assert result is request.response
    assert result.headers.get("HX-Refresh") == "true"


def test_contact_search_tags_results_name_role_phone_email(dbsession):
    user = _make_user(dbsession, "contstrnrpe")
    tag = Tag(name="NRPETag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "NRPECo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "NRPECont", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "NRPETag",
            "name": "NR",
            "role": "PE",
            "phone": "123",
            "email": "x",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["name"] == "NR"


def test_contact_search_tags_results_city_desc_companies(dbsession):
    user = _make_user(dbsession, "contstrcdesc")
    tag = Tag(name="CDescTag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "CDescCo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "CDescCont", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "CDescTag",
            "sort": "city",
            "order": "desc",
            "category": "companies",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["sort"] == "city"
    assert result["q"]["order"] == "desc"


def test_contact_search_tags_results_city_no_category_desc(dbsession):
    user = _make_user(dbsession, "contstrcncd")
    tag = Tag(name="CNcdTag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "CNcdCo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "CNcdCont", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "CNcdTag",
            "sort": "city",
            "order": "desc",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["sort"] == "city"


def test_contact_search_tags_results_category_name_desc(dbsession):
    user = _make_user(dbsession, "contstrcnmd")
    tag = Tag(name="CNmdTag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "CNmdCo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "CNmdCont", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "CNmdTag",
            "sort": "category_name",
            "order": "desc",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["sort"] == "category_name"
    assert result["q"]["order"] == "desc"


def test_contact_search_tags_results_default_sort(dbsession):
    user = _make_user(dbsession, "contstrdefsrt")
    tag = Tag(name="DefSrtTag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "DefSrtCo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "DefSrtCont", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "DefSrtTag",
            "sort": "created_at",
            "order": "asc",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["sort"] == "created_at"
    assert result["q"]["order"] == "asc"


# --- Cover lines 544-545, 549: search_tags_results city sort companies ---


def test_contact_search_tags_results_city_companies_desc(dbsession):
    user = _make_user(dbsession, "contcityco")
    co = _make_company(dbsession, user, "ContCityCoCo")
    tag = Tag(name="ContCityCoTag")
    tag.created_by = user
    co.tags.append(tag)
    dbsession.add(tag)
    _make_contact(dbsession, user, "ContCityCoCont", company=co)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "ContCityCoTag",
            "sort": "city",
            "order": "desc",
            "category": "companies",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["sort"] == "city"


# --- Cover lines 701-717: contact_import_csv success path ---


@patch("marker.views.contact.location")
@patch("marker.views.contact.parse_google_contacts_csv")
def test_contact_import_csv_success_with_location(mock_parse, mock_loc, dbsession):
    mock_loc.return_value = {"lat": 50, "lon": 20}
    user = _make_user(dbsession, "contcsvimp")
    transaction.commit()
    mock_reader = [
        {
            "First Name": "John",
            "Last Name": "Doe",
            "Phone 1 - Value": "123",
            "E-mail 1 - Value": "j@d.com",
            "Organization 1 - Name": "TestCo",
        },
    ]
    mock_parse.return_value = (mock_reader, ["First Name", "Last Name"])
    request = _make_request(dbsession, user, method="POST")
    csv_file_mock = MagicMock()
    csv_file_mock.file = io.BytesIO(b"dummy")
    request.POST = MultiDict({"csv_file": csv_file_mock})
    request.referrer = "/contacts"
    # Mock the importer
    mock_importer = MagicMock()
    mock_importer.add_row.return_value = True
    with patch.object(ContactView, "_get_csv_importer", return_value=mock_importer):
        view = ContactView(request)
        result = view.contact_import_csv()
    assert isinstance(result, HTTPFound)


# --- Cover line 735: contact_import_csv GET ---


def test_contact_import_csv_get_heading_and_form(dbsession):
    user = _make_user(dbsession, "contcsvget")
    transaction.commit()
    request = _make_request(dbsession, user)
    view = ContactView(request)
    result = view.contact_import_csv()
    assert "heading" in result
    assert "form" in result


def test_contact_search_tags_results_bulk_select(dbsession):
    user = _make_user(dbsession, "contstrbulk")
    tag = Tag(name="BulkSelTag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "BulkSelCo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "BulkSelCont", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        method="POST",
        params={
            "target": "contacts",
            "tag": "BulkSelTag",
            "_select_all": "1",
            "checked": "1",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result is request.response


def test_contact_all_bulk_select(dbsession):
    user = _make_user(dbsession, "contallbulk")
    _make_contact(dbsession, user, "AllBulkCont")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        method="POST",
        params={
            "_select_all": "1",
            "checked": "1",
        },
    )
    view = ContactView(request)
    result = view.all()
    assert result is request.response


def test_contact_all_invalid_order(dbsession):
    user = _make_user(dbsession, "contallorder")
    _make_contact(dbsession, user, "AllOrderCont")
    transaction.commit()
    request = _make_request(dbsession, user, params={"order": "INVALID"})
    view = ContactView(request)
    result = view.all()
    assert result["q"]["order"] == "desc"


def test_contact_search_target_invalid(dbsession):
    user = _make_user(dbsession, "conttarginv")
    tag = Tag(name="TargInvTag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "TargInvCo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "TargInvCont", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "INVALID",
            "tag": "TargInvTag",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    # invalid target defaults to "companies", which returns HTTPSeeOther
    from pyramid.httpexceptions import HTTPSeeOther

    assert isinstance(result, HTTPSeeOther)


# --- vcard() ---


@patch("marker.views.contact.response_vcard")
def test_contact_vcard(mock_resp_vcard, dbsession):
    mock_resp_vcard.return_value = MagicMock(status_code=200)
    user = _make_user(dbsession, "contvcard")
    contact = _make_contact(dbsession, user, "VcardCont")
    transaction.commit()
    request = _make_request(dbsession, user, contact=contact)
    view = ContactView(request)
    result = view.vcard()
    assert result.status_code == 200


# --- check() ---


def test_contact_check(dbsession):
    user = _make_user(dbsession, "contcheck")
    contact = _make_contact(dbsession, user, "CheckCont")
    transaction.commit()
    request = _make_request(dbsession, user, contact=contact, method="POST")
    view = ContactView(request)
    result = view.check()
    assert "checked" in result


# --- contact_import_csv() ---


def test_contact_import_csv_get_form(dbsession):
    user = _make_user(dbsession, "contimportget")
    transaction.commit()
    request = _make_request(dbsession, user, method="GET", post={})
    view = ContactView(request)
    result = view.contact_import_csv()
    assert "form" in result


def test_contact_import_csv_empty_file(dbsession):
    user = _make_user(dbsession, "contimportempty")
    transaction.commit()
    request = _make_request(dbsession, user, method="POST", post={})
    csv_field = MagicMock()
    csv_field.file = None
    request.POST["csv_file"] = csv_field
    view = ContactView(request)
    result = view.contact_import_csv()
    assert isinstance(result, HTTPFound)


@patch("marker.views.contact.parse_google_contacts_csv", return_value=(None, []))
def test_contact_import_csv_bad_file(mock_parse, dbsession):
    user = _make_user(dbsession, "contimportbad")
    transaction.commit()
    request = _make_request(dbsession, user, method="POST", post={})
    csv_field = MagicMock()
    csv_field.file = io.BytesIO(b"bad data")
    request.POST["csv_file"] = csv_field
    view = ContactView(request)
    result = view.contact_import_csv()
    assert isinstance(result, HTTPFound)


@patch(
    "marker.views.contact.missing_google_contacts_columns", return_value=["First Name"]
)
@patch("marker.views.contact.parse_google_contacts_csv", return_value=([], ["Name"]))
def test_contact_import_csv_missing_columns_minimal(
    mock_parse, mock_missing, dbsession
):
    user = _make_user(dbsession, "contimportmisscol")
    transaction.commit()
    request = _make_request(dbsession, user, method="POST", post={})
    csv_field = MagicMock()
    csv_field.file = io.BytesIO(b"Name\nJohn")
    request.POST["csv_file"] = csv_field
    view = ContactView(request)
    result = view.contact_import_csv()
    assert isinstance(result, HTTPFound)


@patch("marker.views.contact.missing_google_contacts_columns", return_value=[])
@patch("marker.views.contact.parse_google_contacts_csv")
def test_contact_import_csv_success_redirect(mock_parse, mock_missing, dbsession):
    rows = [{"First Name": "John", "Last Name": "Doe"}]
    mock_parse.return_value = (iter(rows), ["First Name", "Last Name"])
    user = _make_user(dbsession, "contimportsuccess")
    transaction.commit()
    request = _make_request(dbsession, user, method="POST", post={})
    csv_field = MagicMock()
    csv_field.file = io.BytesIO(b"data")
    request.POST["csv_file"] = csv_field
    mock_importer = MagicMock()
    mock_importer.add_row.return_value = True
    with patch.object(ContactView, "_get_csv_importer", return_value=mock_importer):
        view = ContactView(request)
        result = view.contact_import_csv()
    assert isinstance(result, HTTPFound)


def test_contact_all_sort_city_projects_asc(dbsession):
    """Cover lines 544-545: all() city sort projects asc."""
    user = _make_user(dbsession, "contcitypasc")
    proj = _make_project(dbsession, user, "ContCityPAscProj")
    _make_contact(dbsession, user, "ContCityPAscCont", project=proj)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "sort": "city",
            "order": "asc",
            "category": "projects",
        },
    )
    view = ContactView(request)
    result = view.all()
    assert "paginator" in result


def test_contact_search_tags_sort_city_projects_desc(dbsession):
    """Cover lines 544-545: search_tags_results city sort projects desc."""
    user = _make_user(dbsession, "contstcitypd")
    tag = Tag(name="CityPDTag")
    tag.created_by = user
    dbsession.add(tag)
    proj = _make_project(dbsession, user, "CityPDProj")
    tag.projects.append(proj)
    _make_contact(dbsession, user, "CityPDCont", project=proj)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "CityPDTag",
            "sort": "city",
            "order": "desc",
            "category": "projects",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["sort"] == "city"


def test_contact_search_tags_sort_city_companies_asc(dbsession):
    """Cover line 549: search_tags_results city sort companies asc."""
    user = _make_user(dbsession, "contstcityca")
    tag = Tag(name="CityCATag")
    tag.created_by = user
    dbsession.add(tag)
    co = _make_company(dbsession, user, "CityCACo")
    tag.companies.append(co)
    _make_contact(dbsession, user, "CityCACont", company=co)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "CityCATag",
            "sort": "city",
            "order": "asc",
            "category": "companies",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["sort"] == "city"


@patch("marker.views.contact.missing_google_contacts_columns")
@patch("marker.views.contact.parse_google_contacts_csv")
def test_contact_import_csv_missing_columns_mocked(mock_parse, mock_missing, dbsession):
    """Cover lines 701-708: CSV import with missing Google Contacts columns."""
    mock_parse.return_value = (iter([{"col": "val"}]), ["col"])
    mock_missing.return_value = ["First Name", "Organization 1 - Name"]
    user = _make_user(dbsession, "contimpmissing")
    transaction.commit()
    request = _make_request(dbsession, user, method="POST", post={})
    csv_field = MagicMock()
    csv_field.file = io.BytesIO(b"col\nval")
    request.POST["csv_file"] = csv_field
    view = ContactView(request)
    result = view.contact_import_csv()
    assert isinstance(result, HTTPFound)


@patch("marker.views.contact.missing_google_contacts_columns", return_value=[])
@patch("marker.views.contact.parse_google_contacts_csv")
def test_contact_import_csv_skipped_row(mock_parse, mock_missing, dbsession):
    """Cover line 717: CSV import with skipped (duplicate) rows."""
    rows = [{"First Name": "John"}]
    mock_parse.return_value = (iter(rows), ["First Name"])
    user = _make_user(dbsession, "contimpskip")
    transaction.commit()
    request = _make_request(dbsession, user, method="POST", post={})
    csv_field = MagicMock()
    csv_field.file = io.BytesIO(b"data")
    request.POST["csv_file"] = csv_field
    mock_importer = MagicMock()
    mock_importer.add_row.return_value = False
    with patch.object(ContactView, "_get_csv_importer", return_value=mock_importer):
        view = ContactView(request)
        result = view.contact_import_csv()
    assert isinstance(result, HTTPFound)


def test_contact_get_csv_importer(dbsession):
    """Cover line 735: _get_csv_importer creates a GoogleContactsCsvImporter."""
    from marker.utils.contact_csv_import import GoogleContactsCsvImporter

    user = _make_user(dbsession, "contimporter")
    transaction.commit()
    request = _make_request(dbsession, user)
    view = ContactView(request)
    importer = view._get_csv_importer()
    assert isinstance(importer, GoogleContactsCsvImporter)


# ===========================================================================
# Date range filtering tests
# ===========================================================================


def test_contact_all_date_from(dbsession):
    user = _make_user(dbsession, "contdtf1")
    _make_contact(dbsession, user, "DtFromCont")
    transaction.commit()
    request = _make_request(dbsession, user, params={"date_from": "2020-01-01T00:00"})
    view = ContactView(request)
    result = view.all()
    assert result["q"]["date_from"] == "2020-01-01T00:00"
    assert result["counter"] >= 1


def test_contact_all_date_to(dbsession):
    user = _make_user(dbsession, "contdtt1")
    _make_contact(dbsession, user, "DtToCont")
    transaction.commit()
    request = _make_request(dbsession, user, params={"date_to": "2030-01-01T00:00"})
    view = ContactView(request)
    result = view.all()
    assert result["q"]["date_to"] == "2030-01-01T00:00"
    assert result["counter"] >= 1


def test_contact_all_date_range(dbsession):
    user = _make_user(dbsession, "contdtr1")
    _make_contact(dbsession, user, "DtRangeCont")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={"date_from": "2020-01-01T00:00", "date_to": "2030-01-01T00:00"},
    )
    view = ContactView(request)
    result = view.all()
    assert result["q"]["date_from"] == "2020-01-01T00:00"
    assert result["q"]["date_to"] == "2030-01-01T00:00"
    assert result["counter"] >= 1


def test_contact_search_tags_date_from(dbsession):
    user = _make_user(dbsession, "contstrdf")
    company = _make_company(dbsession, user)
    tag = Tag(name="ContSTRDfTag")
    tag.created_by = user
    dbsession.add(tag)
    company.tags.append(tag)
    _make_contact(dbsession, user, "STRDfCont", company=company)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "ContSTRDfTag",
            "date_from": "2020-01-01T00:00",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["date_from"] == "2020-01-01T00:00"


def test_contact_search_tags_date_to(dbsession):
    user = _make_user(dbsession, "contstrdt")
    company = _make_company(dbsession, user)
    tag = Tag(name="ContSTRDtTag")
    tag.created_by = user
    dbsession.add(tag)
    company.tags.append(tag)
    _make_contact(dbsession, user, "STRDtCont", company=company)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "target": "contacts",
            "tag": "ContSTRDtTag",
            "date_to": "2030-01-01T00:00",
        },
    )
    view = ContactView(request)
    result = view.search_tags_results()
    assert result["q"]["date_to"] == "2030-01-01T00:00"
