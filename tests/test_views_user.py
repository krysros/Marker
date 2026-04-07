from unittest.mock import MagicMock

import pytest
import transaction
from pyramid.httpexceptions import HTTPSeeOther
from webob.multidict import MultiDict

import marker.forms.ts
from marker.models.comment import Comment
from marker.models.company import Company
from marker.models.contact import Contact
from marker.models.project import Project
from marker.models.tag import Tag
from marker.models.user import User
from marker.views.user import UserView
from tests.conftest import DummyRequestWithIdentity


@pytest.fixture(autouse=True)
def patch_translationstring_str(monkeypatch):
    monkeypatch.setattr(
        marker.forms.ts.TranslationString, "__str__", lambda self: self.msg
    )
    yield


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _req(dbsession, user, method="GET", params=None, post=None, context_user=None):
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = method
    request.GET = MultiDict(params or {})
    request.POST = MultiDict(post or {})
    request.params = MultiDict(params or {})
    request.locale_name = "en"
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/user"
    request.session = MagicMock()
    request.response = MagicMock()
    request.response.headers = {}
    request.context = MagicMock()
    if context_user is not None:
        request.context.user = context_user
    else:
        request.context.user = user
    request.matchdict = {}
    request.matched_route = MagicMock()
    request.matched_route.name = "user_all"
    request.environ = {}
    request.environ["webob._parsed_get_vars"] = (MultiDict(params or {}), MultiDict())
    request.environ["webob._parsed_post_vars"] = (MultiDict(post or {}), MultiDict())
    request.environ["webob._parsed_params_vars"] = (
        MultiDict(params or {}),
        MultiDict(),
    )
    request.path_qs = "/user"
    request.query_string = ""
    request.referrer = "/home"
    request.headers = {}
    return request


def _user(dbsession, name="testuser"):
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


def _company(dbsession, user, name="TestCo", color="", country="PL"):
    company = Company(
        name=name,
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country=country,
        website="http://x.com",
        color=color,
        NIP="n",
        REGON="r",
        KRS="k",
    )
    company.latitude = 50.0
    company.longitude = 20.0
    company.created_by = user
    dbsession.add(company)
    dbsession.flush()
    return company


def _project(
    dbsession,
    user,
    name="TestProj",
    color="",
    deadline=None,
    stage="",
    delivery_method="",
):
    project = Project(
        name=name,
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="http://x.com",
        color=color,
        deadline=deadline,
        stage=stage,
        delivery_method=delivery_method,
    )
    project.latitude = 50.0
    project.longitude = 20.0
    project.created_by = user
    dbsession.add(project)
    dbsession.flush()
    return project


def _tag(dbsession, user, name="TestTag"):
    tag = Tag(name=name)
    tag.created_by = user
    dbsession.add(tag)
    dbsession.flush()
    return tag


def _contact(dbsession, user, name="TestContact", company=None, project=None, color=""):
    contact = Contact(name=name, role="r", phone="123", email="c@e.com", color=color)
    contact.created_by = user
    if company:
        contact.company = company
    if project:
        contact.project = project
    dbsession.add(contact)
    dbsession.flush()
    return contact


def _comment(dbsession, user, company=None, project=None, text="comment"):
    comment = Comment(comment=text)
    comment.created_by = user
    if company:
        comment.company_id = company.id
    if project:
        comment.project_id = project.id
    dbsession.add(comment)
    dbsession.flush()
    return comment


# ===========================================================================
# _is_truthy
# ===========================================================================


def test_is_truthy(dbsession):
    user = _user(dbsession)
    request = _req(dbsession, user)
    view = UserView(request)
    assert view._is_truthy(True) is True
    assert view._is_truthy(False) is False
    assert view._is_truthy(None) is False
    assert view._is_truthy("1") is True
    assert view._is_truthy("true") is True
    assert view._is_truthy("on") is True
    assert view._is_truthy("yes") is True
    assert view._is_truthy("0") is False
    assert view._is_truthy("no") is False


# ===========================================================================
# pills()
# ===========================================================================


def test_pills(dbsession):
    user = _user(dbsession)
    request = _req(dbsession, user)
    view = UserView(request)
    pills = view.pills(user)
    assert len(pills) == 6
    assert pills[0]["title"] == "User"


# ===========================================================================
# export helpers
# ===========================================================================


def test_contact_export_header(dbsession):
    user = _user(dbsession)
    request = _req(dbsession, user)
    view = UserView(request)
    header = view._contact_export_header()
    assert len(header) == 4


def test_company_export_header(dbsession):
    user = _user(dbsession)
    request = _req(dbsession, user)
    view = UserView(request)
    header = view._company_export_header()
    assert len(header) > 4  # contact header + company fields + Tags


def test_project_export_header(dbsession):
    user = _user(dbsession)
    request = _req(dbsession, user)
    view = UserView(request)
    header = view._project_export_header()
    assert len(header) > 4


def test_tag_export_header_companies(dbsession):
    user = _user(dbsession)
    request = _req(dbsession, user)
    view = UserView(request)
    header = view._tag_export_header(category="companies")
    assert "Company name" in header or len(header) > 5


def test_tag_export_header_projects(dbsession):
    user = _user(dbsession)
    request = _req(dbsession, user)
    view = UserView(request)
    header = view._tag_export_header(category="projects")
    assert len(header) > 5


def test_tags_as_string(dbsession):
    user = _user(dbsession)
    t1 = _tag(dbsession, user, "A")
    t2 = _tag(dbsession, user, "B")
    request = _req(dbsession, user)
    view = UserView(request)
    result = view._tags_as_string([t1, t2])
    assert "A" in result and "B" in result and " ::: " in result


def test_contact_row_values(dbsession):
    user = _user(dbsession)
    contact = _contact(dbsession, user)
    request = _req(dbsession, user)
    view = UserView(request)
    vals = view._contact_row_values(contact)
    assert len(vals) == 4
    assert vals[0] == "TestContact"


def test_resolve_row_color(dbsession):
    user = _user(dbsession)
    request = _req(dbsession, user)
    view = UserView(request)
    assert view._resolve_row_color("red", "blue") == "blue"
    assert view._resolve_row_color("red", None) == "red"
    assert view._resolve_row_color("", None) == ""
    assert view._resolve_row_color(None, None) == ""


def test_filter_tags_by_category_companies(dbsession):
    user = _user(dbsession)
    from sqlalchemy import select as sa_select

    from marker.models.tag import Tag as TagModel

    request = _req(dbsession, user)
    view = UserView(request)
    stmt = sa_select(TagModel)
    q = {}
    stmt2, cat = view._filter_tags_by_category(stmt, "companies", q)
    assert cat == "companies"
    assert q.get("category") == "companies"


def test_filter_tags_by_category_projects(dbsession):
    user = _user(dbsession)
    from sqlalchemy import select as sa_select

    from marker.models.tag import Tag as TagModel

    request = _req(dbsession, user)
    view = UserView(request)
    stmt = sa_select(TagModel)
    q = {}
    stmt2, cat = view._filter_tags_by_category(stmt, "projects", q)
    assert cat == "projects"


def test_filter_tags_by_category_other(dbsession):
    user = _user(dbsession)
    from sqlalchemy import select as sa_select

    from marker.models.tag import Tag as TagModel

    request = _req(dbsession, user)
    view = UserView(request)
    stmt = sa_select(TagModel)
    q = {}
    stmt2, cat = view._filter_tags_by_category(stmt, "invalid", q)
    assert cat == ""
    assert "category" not in q


def test_company_row_values(dbsession):
    user = _user(dbsession)
    company = _company(dbsession, user)
    request = _req(dbsession, user)
    view = UserView(request)
    vals = view._company_row_values(company)
    assert vals[0] == "TestCo"
    assert len(vals) == 10


def test_project_row_values(dbsession):
    user = _user(dbsession)
    project = _project(dbsession, user)
    request = _req(dbsession, user)
    view = UserView(request)
    vals = view._project_row_values(project)
    assert vals[0] == "TestProj"
    assert len(vals) == 10


def test_selected_contacts_export_header(dbsession):
    user = _user(dbsession)
    request = _req(dbsession, user)
    view = UserView(request)
    h1 = view._selected_contacts_export_header("projects")
    h2 = view._selected_contacts_export_header("companies")
    assert len(h1) > 0
    assert len(h2) > 0


def test_selected_contacts_export_rows_with_project(dbsession):
    user = _user(dbsession)
    project = _project(dbsession, user)
    contact = _contact(dbsession, user, project=project)
    request = _req(dbsession, user)
    view = UserView(request)
    rows, colors = view._selected_contacts_export_rows([contact], "projects")
    assert len(rows) == 1


def test_selected_contacts_export_rows_no_linked(dbsession):
    user = _user(dbsession)
    contact = _contact(dbsession, user)
    request = _req(dbsession, user)
    view = UserView(request)
    rows, colors = view._selected_contacts_export_rows([contact], "companies")
    assert len(rows) == 1


def test_rows_for_objects_with_contacts(dbsession):
    user = _user(dbsession, "rowhelper")
    company = _company(dbsession, user, "RowHelperCo")
    _contact(dbsession, user, "RowContact", company=company)
    request = _req(dbsession, user)
    view = UserView(request)
    rows, colors = view._rows_for_objects_with_contacts(
        [company], view._company_row_values
    )
    assert len(rows) == 1
    assert rows[0][0] == "RowContact"


def test_rows_for_objects_no_contacts(dbsession):
    user = _user(dbsession, "rownocont")
    company = _company(dbsession, user, "RowNoContCo")
    request = _req(dbsession, user)
    view = UserView(request)
    rows, colors = view._rows_for_objects_with_contacts(
        [company], view._company_row_values
    )
    assert len(rows) == 1
    assert rows[0][0] == ""  # empty contact name


def test_company_export_rows(dbsession):
    user = _user(dbsession, "coexprows")
    company = _company(dbsession, user, "ExpCo")
    request = _req(dbsession, user)
    view = UserView(request)
    rows, colors = view._company_export_rows([company])
    assert len(rows) == 1


def test_project_export_rows(dbsession):
    user = _user(dbsession, "projexprows")
    project = _project(dbsession, user, "ExpProj")
    request = _req(dbsession, user)
    view = UserView(request)
    rows, colors = view._project_export_rows([project])
    assert len(rows) == 1


def test_tag_export_rows_companies(dbsession):
    user = _user(dbsession, "tagexprows")
    tag = _tag(dbsession, user, "ExpTag")
    company = _company(dbsession, user, "TagExpCo")
    tag.companies.append(company)
    _contact(dbsession, user, "TagExpContact", company=company)
    request = _req(dbsession, user)
    view = UserView(request)
    rows, colors = view._tag_export_rows([tag], category="companies")
    assert len(rows) >= 1


def test_tag_export_rows_companies_no_contacts(dbsession):
    user = _user(dbsession, "tagexpnoc")
    tag = _tag(dbsession, user, "ExpTagNoc")
    company = _company(dbsession, user, "TagExpNocCo")
    tag.companies.append(company)
    request = _req(dbsession, user)
    view = UserView(request)
    rows, colors = view._tag_export_rows([tag], category="companies")
    assert len(rows) == 1


def test_tag_export_rows_no_companies(dbsession):
    user = _user(dbsession, "tagexpnocos")
    tag = _tag(dbsession, user, "ExpTagNocos")
    request = _req(dbsession, user)
    view = UserView(request)
    rows, colors = view._tag_export_rows([tag], category="companies")
    assert len(rows) == 1


def test_tag_export_rows_projects(dbsession):
    user = _user(dbsession, "tagexpprows")
    tag = _tag(dbsession, user, "ExpTagP")
    project = _project(dbsession, user, "TagExpProj")
    tag.projects.append(project)
    _contact(dbsession, user, "TagExpPContact", project=project)
    request = _req(dbsession, user)
    view = UserView(request)
    rows, colors = view._tag_export_rows([tag], category="projects")
    assert len(rows) >= 1


def test_tag_export_rows_projects_no_contacts(dbsession):
    user = _user(dbsession, "tagexppnoc")
    tag = _tag(dbsession, user, "ExpTagPNoc")
    project = _project(dbsession, user, "TagExpPNocProj")
    tag.projects.append(project)
    request = _req(dbsession, user)
    view = UserView(request)
    rows, colors = view._tag_export_rows([tag], category="projects")
    assert len(rows) == 1


# ===========================================================================
# all()
# ===========================================================================


def test_user_all_default(dbsession):
    user = _user(dbsession)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.all()
    assert "paginator" in result
    assert "form" in result
    assert result["q"]["sort"] == "created_at"
    assert result["q"]["order"] == "desc"


def test_user_all_with_filters(dbsession):
    user = _user(dbsession, "filteruser")
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "name": "filter",
            "fullname": "Test",
            "email": "filter",
            "role": "admin",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.all()
    assert result["q"]["name"] == "filter"
    assert result["q"]["sort"] == "name"
    assert result["q"]["order"] == "asc"


def test_user_all_invalid_sort_order(dbsession):
    user = _user(dbsession, "invalidsort")
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "invalid", "order": "invalid"})
    view = UserView(request)
    result = view.all()
    assert result["q"]["sort"] == "created_at"
    assert result["q"]["order"] == "desc"


# ===========================================================================
# view()
# ===========================================================================


def test_user_view(dbsession):
    user = _user(dbsession)
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.view()
    assert "user" in result
    assert result["title"] == user.fullname
    assert "user_pills" in result


# ===========================================================================
# comments()
# ===========================================================================


def test_user_comments_default(dbsession):
    user = _user(dbsession, "cmtuser")
    _comment(dbsession, user)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.comments()
    assert "paginator" in result
    assert "form" in result


def test_user_comments_category_companies(dbsession):
    user = _user(dbsession, "cmtcouser")
    co = _company(dbsession, user, "CmtCo")
    _comment(dbsession, user, company=co)
    transaction.commit()
    request = _req(dbsession, user, params={"category": "companies"})
    view = UserView(request)
    result = view.comments()
    assert result["q"].get("category") == "companies"


def test_user_comments_category_projects(dbsession):
    user = _user(dbsession, "cmtpuser")
    proj = _project(dbsession, user, "CmtProj")
    _comment(dbsession, user, project=proj)
    transaction.commit()
    request = _req(dbsession, user, params={"category": "projects"})
    view = UserView(request)
    result = view.comments()
    assert result["q"].get("category") == "projects"


def test_user_comments_order_asc(dbsession):
    user = _user(dbsession, "cmtasc")
    _comment(dbsession, user)
    transaction.commit()
    request = _req(dbsession, user, params={"order": "asc"})
    view = UserView(request)
    result = view.comments()
    assert "paginator" in result


def test_user_comments_invalid_order(dbsession):
    user = _user(dbsession, "cmtinvord")
    transaction.commit()
    request = _req(dbsession, user, params={"order": "invalid"})
    view = UserView(request)
    result = view.comments()
    assert "paginator" in result


# ===========================================================================
# tags()
# ===========================================================================


def test_user_tags_default(dbsession):
    user = _user(dbsession, "taguser")
    _tag(dbsession, user)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.tags()
    assert "paginator" in result
    assert result["q"]["sort"] == "created_at"


def test_user_tags_sort_name_asc(dbsession):
    user = _user(dbsession, "tagnameasc")
    _tag(dbsession, user, "ATag")
    _tag(dbsession, user, "BTag")
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "name", "order": "asc"})
    view = UserView(request)
    result = view.tags()
    assert result["q"]["sort"] == "name"
    assert result["q"]["order"] == "asc"


def test_user_tags_category_companies(dbsession):
    user = _user(dbsession, "tagcatco")
    tag = _tag(dbsession, user, "CatCoTag")
    co = _company(dbsession, user, "TagCatCo")
    tag.companies.append(co)
    transaction.commit()
    request = _req(dbsession, user, params={"category": "companies"})
    view = UserView(request)
    result = view.tags()
    assert "paginator" in result


def test_user_tags_invalid_sort(dbsession):
    user = _user(dbsession, "taginvsort")
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "bad", "order": "bad"})
    view = UserView(request)
    result = view.tags()
    assert result["q"]["sort"] == "created_at"
    assert result["q"]["order"] == "desc"


# ===========================================================================
# export_tags()
# ===========================================================================


def test_user_export_tags_companies(dbsession):
    user = _user(dbsession, "exptag")
    tag = _tag(dbsession, user, "ExpTag")
    co = _company(dbsession, user, "ExpTagCo")
    tag.companies.append(co)
    transaction.commit()
    request = _req(dbsession, user, params={"category": "companies"})
    view = UserView(request)
    result = view.export_tags()
    assert result is not None


def test_user_export_tags_projects(dbsession):
    user = _user(dbsession, "exptagp")
    tag = _tag(dbsession, user, "ExpTagP")
    proj = _project(dbsession, user, "ExpTagProj")
    tag.projects.append(proj)
    transaction.commit()
    request = _req(
        dbsession, user, params={"category": "projects", "sort": "name", "order": "asc"}
    )
    view = UserView(request)
    result = view.export_tags()
    assert result is not None


# ===========================================================================
# companies()
# ===========================================================================


def test_user_companies_default(dbsession):
    user = _user(dbsession, "compuser")
    _company(dbsession, user, "UserCo")
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.companies()
    assert "paginator" in result
    assert "form" in result


def test_user_companies_all_filters(dbsession):
    user = _user(dbsession, "compfilt")
    _company(dbsession, user, "FiltCo", color="red")
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "name": "Filt",
            "street": "S",
            "postcode": "00",
            "city": "C",
            "website": "x",
            "subdivision": "PL-14",
            "country": "PL",
            "color": "red",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.companies()
    assert result["q"]["name"] == "Filt"
    assert result["q"]["color"] == "red"


def test_user_companies_sort_stars_desc(dbsession):
    user = _user(dbsession, "compstars")
    co = _company(dbsession, user, "StarCo")
    user.companies_stars.append(co)
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "stars", "order": "desc"})
    view = UserView(request)
    result = view.companies()
    assert result["q"]["sort"] == "stars"


def test_user_companies_sort_stars_asc(dbsession):
    user = _user(dbsession, "compstarsasc")
    co = _company(dbsession, user, "StarAscCo")
    user.companies_stars.append(co)
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "stars", "order": "asc"})
    view = UserView(request)
    result = view.companies()
    assert result["q"]["sort"] == "stars"


def test_user_companies_sort_comments_asc(dbsession):
    user = _user(dbsession, "compcmtasc")
    co = _company(dbsession, user, "CmtAscCo")
    _comment(dbsession, user, company=co)
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "comments", "order": "asc"})
    view = UserView(request)
    result = view.companies()
    assert result["q"]["sort"] == "comments"


def test_user_companies_sort_comments_desc(dbsession):
    user = _user(dbsession, "compcmtdesc")
    co = _company(dbsession, user, "CmtDescCo")
    _comment(dbsession, user, company=co)
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "comments", "order": "desc"})
    view = UserView(request)
    result = view.companies()
    assert result["q"]["sort"] == "comments"


def test_user_companies_sort_generic_asc(dbsession):
    user = _user(dbsession, "compgenasc")
    _company(dbsession, user, "GenAscCo")
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "city", "order": "asc"})
    view = UserView(request)
    result = view.companies()
    assert result["q"]["sort"] == "city"


def test_user_companies_invalid_sort(dbsession):
    user = _user(dbsession, "compinvsort")
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "bad", "order": "bad"})
    view = UserView(request)
    result = view.companies()
    assert result["q"]["sort"] == "created_at"


# ===========================================================================
# export_companies()
# ===========================================================================


def test_user_export_companies(dbsession):
    user = _user(dbsession, "expcomp")
    co = _company(dbsession, user, "ExpCo")
    _contact(dbsession, user, "ExpCoContact", company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "name": "Exp",
            "street": "S",
            "postcode": "00",
            "city": "C",
            "website": "x",
            "subdivision": "PL-14",
            "country": "PL",
            "color": "",
        },
    )
    view = UserView(request)
    result = view.export_companies()
    assert result is not None


def test_user_export_companies_sort_stars(dbsession):
    user = _user(dbsession, "expcompstars")
    co = _company(dbsession, user, "ExpStarCo")
    user.companies_stars.append(co)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _req(dbsession, user, params={"sort": "stars", "order": order})
        view = UserView(request)
        result = view.export_companies()
        assert result is not None


def test_user_export_companies_sort_comments(dbsession):
    user = _user(dbsession, "expcompcmt")
    co = _company(dbsession, user, "ExpCmtCo")
    _comment(dbsession, user, company=co)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _req(dbsession, user, params={"sort": "comments", "order": order})
        view = UserView(request)
        result = view.export_companies()
        assert result is not None


# ===========================================================================
# projects()
# ===========================================================================


def test_user_projects_default(dbsession):
    user = _user(dbsession, "projuser")
    _project(dbsession, user, "UserProj")
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.projects()
    assert "paginator" in result


def test_user_projects_all_filters(dbsession):
    user = _user(dbsession, "projfilt")
    _project(
        dbsession,
        user,
        "FiltProj",
        color="red",
        stage="planning",
        delivery_method="tender",
    )
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "name": "Filt",
            "street": "S",
            "postcode": "00",
            "city": "C",
            "website": "x",
            "subdivision": "PL-14",
            "country": "PL",
            "color": "red",
            "stage": "planning",
            "delivery_method": "tender",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.projects()
    assert result["q"]["stage"] == "planning"


def test_user_projects_deadline_filter(dbsession):
    import datetime

    user = _user(dbsession, "projdeadline")
    _project(dbsession, user, "DeadlineProj", deadline=datetime.datetime(2025, 6, 1))
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "deadline": "2025-12-31 00:00:00",
        },
    )
    view = UserView(request)
    result = view.projects()
    assert "paginator" in result


def test_user_projects_status_in_progress(dbsession):
    import datetime

    user = _user(dbsession, "projinprog")
    _project(
        dbsession,
        user,
        "InProgProj",
        deadline=datetime.datetime.now() + datetime.timedelta(days=30),
    )
    transaction.commit()
    request = _req(dbsession, user, params={"status": "in_progress"})
    view = UserView(request)
    result = view.projects()
    assert result["q"]["status"] == "in_progress"


def test_user_projects_status_completed(dbsession):
    import datetime

    user = _user(dbsession, "projcompl")
    _project(
        dbsession,
        user,
        "ComplProj",
        deadline=datetime.datetime.now() - datetime.timedelta(days=30),
    )
    transaction.commit()
    request = _req(dbsession, user, params={"status": "completed"})
    view = UserView(request)
    result = view.projects()
    assert result["q"]["status"] == "completed"


def test_user_projects_sort_stars(dbsession):
    user = _user(dbsession, "projstars")
    proj = _project(dbsession, user, "StarProj")
    user.projects_stars.append(proj)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _req(dbsession, user, params={"sort": "stars", "order": order})
        view = UserView(request)
        result = view.projects()
        assert result["q"]["sort"] == "stars"


def test_user_projects_sort_comments(dbsession):
    user = _user(dbsession, "projcmts")
    proj = _project(dbsession, user, "CmtProj")
    _comment(dbsession, user, project=proj)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _req(dbsession, user, params={"sort": "comments", "order": order})
        view = UserView(request)
        result = view.projects()
        assert result["q"]["sort"] == "comments"


def test_user_projects_sort_generic_asc(dbsession):
    user = _user(dbsession, "projgenasc")
    _project(dbsession, user, "GenAscProj")
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "city", "order": "asc"})
    view = UserView(request)
    result = view.projects()
    assert result["q"]["sort"] == "city"


def test_user_projects_invalid_sort(dbsession):
    user = _user(dbsession, "projinvsort")
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "bad", "order": "bad"})
    view = UserView(request)
    result = view.projects()
    assert result["q"]["sort"] == "created_at"


# ===========================================================================
# export_projects()
# ===========================================================================


def test_user_export_projects(dbsession):
    user = _user(dbsession, "expproj")
    proj = _project(dbsession, user, "ExpProj")
    _contact(dbsession, user, "ExpProjContact", project=proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "name": "Exp",
            "street": "S",
            "postcode": "00",
            "city": "C",
            "website": "x",
            "subdivision": "PL-14",
            "country": "PL",
            "color": "",
            "stage": "",
            "delivery_method": "",
        },
    )
    view = UserView(request)
    result = view.export_projects()
    assert result is not None


def test_user_export_projects_sort_stars(dbsession):
    user = _user(dbsession, "expprojstars")
    proj = _project(dbsession, user, "ExpStarProj")
    user.projects_stars.append(proj)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _req(dbsession, user, params={"sort": "stars", "order": order})
        view = UserView(request)
        result = view.export_projects()
        assert result is not None


def test_user_export_projects_sort_comments(dbsession):
    user = _user(dbsession, "expprojcmt")
    proj = _project(dbsession, user, "ExpCmtProj")
    _comment(dbsession, user, project=proj)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _req(dbsession, user, params={"sort": "comments", "order": order})
        view = UserView(request)
        result = view.export_projects()
        assert result is not None


def test_user_export_projects_status_deadline(dbsession):
    import datetime

    user = _user(dbsession, "expprojstat")
    _project(dbsession, user, "ExpStatProj", deadline=datetime.datetime(2025, 6, 1))
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "status": "in_progress",
            "deadline": "2025-12-31 00:00:00",
        },
    )
    view = UserView(request)
    result = view.export_projects()
    assert result is not None


# ===========================================================================
# contacts()
# ===========================================================================


def test_user_contacts_default(dbsession):
    user = _user(dbsession, "contuser")
    _contact(dbsession, user)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.contacts()
    assert "paginator" in result


def test_user_contacts_all_filters(dbsession):
    user = _user(dbsession, "contfilt")
    co = _company(dbsession, user, "ContFiltCo")
    _contact(dbsession, user, "FiltContact", company=co, color="red")
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "name": "Filt",
            "role": "r",
            "phone": "123",
            "email": "c",
            "color": "red",
            "category": "companies",
            "country": "PL",
            "subdivision": "PL-14",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.contacts()
    assert result["q"]["category"] == "companies"


def test_user_contacts_category_projects(dbsession):
    user = _user(dbsession, "contproj")
    proj = _project(dbsession, user, "ContProj")
    _contact(dbsession, user, "ProjContact", project=proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "projects",
            "country": "PL",
            "subdivision": "PL-14",
        },
    )
    view = UserView(request)
    result = view.contacts()
    assert result["q"]["category"] == "projects"


def test_user_contacts_no_category_with_country(dbsession):
    user = _user(dbsession, "contnocatco")
    co = _company(dbsession, user, "NoCatCo", country="PL")
    _contact(dbsession, user, "NoCatContact", company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "country": "PL",
            "subdivision": "PL-14",
        },
    )
    view = UserView(request)
    result = view.contacts()
    assert result["q"]["country"] == "PL"


def test_user_contacts_sort_city_companies(dbsession):
    user = _user(dbsession, "contcityco")
    co = _company(dbsession, user, "CityComp")
    _contact(dbsession, user, "CityContact", company=co)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _req(
            dbsession,
            user,
            params={
                "sort": "city",
                "order": order,
                "category": "companies",
            },
        )
        view = UserView(request)
        result = view.contacts()
        assert result["q"]["sort"] == "city"


def test_user_contacts_sort_city_projects(dbsession):
    user = _user(dbsession, "contcityproj")
    proj = _project(dbsession, user, "CityProj")
    _contact(dbsession, user, "CityProjContact", project=proj)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _req(
            dbsession,
            user,
            params={
                "sort": "city",
                "order": order,
                "category": "projects",
            },
        )
        view = UserView(request)
        result = view.contacts()
        assert result["q"]["sort"] == "city"


def test_user_contacts_sort_city_no_category(dbsession):
    user = _user(dbsession, "contcitynocat")
    co = _company(dbsession, user, "CityNoCatCo")
    _contact(dbsession, user, "CityNoCatContact", company=co)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _req(dbsession, user, params={"sort": "city", "order": order})
        view = UserView(request)
        result = view.contacts()
        assert result["q"]["sort"] == "city"


def test_user_contacts_sort_category_name(dbsession):
    user = _user(dbsession, "contcatname")
    co = _company(dbsession, user, "CatNameCo")
    _contact(dbsession, user, "CatNameContact", company=co)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _req(
            dbsession, user, params={"sort": "category_name", "order": order}
        )
        view = UserView(request)
        result = view.contacts()
        assert result["q"]["sort"] == "category_name"


def test_user_contacts_sort_generic(dbsession):
    user = _user(dbsession, "contgeneric")
    _contact(dbsession, user, "GenContact")
    transaction.commit()
    for order in ("asc", "desc"):
        request = _req(dbsession, user, params={"sort": "name", "order": order})
        view = UserView(request)
        result = view.contacts()
        assert result["q"]["sort"] == "name"


def test_user_contacts_invalid_sort(dbsession):
    user = _user(dbsession, "continvsort")
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "bad", "order": "bad"})
    view = UserView(request)
    result = view.contacts()
    assert result["q"]["sort"] == "created_at"


# ===========================================================================
# export_contacts()
# ===========================================================================


def test_user_export_contacts_companies(dbsession):
    user = _user(dbsession, "expcont")
    co = _company(dbsession, user, "ExpContCo")
    _contact(dbsession, user, "ExpContact", company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "name": "Exp",
            "role": "r",
            "phone": "1",
            "email": "c",
            "category": "companies",
            "country": "PL",
            "subdivision": "PL-14",
            "color": "",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_contacts()
    assert result is not None


def test_user_export_contacts_projects(dbsession):
    user = _user(dbsession, "expcontproj")
    proj = _project(dbsession, user, "ExpContProj")
    _contact(dbsession, user, "ExpProjContact2", project=proj)
    transaction.commit()
    request = _req(dbsession, user, params={"category": "projects"})
    view = UserView(request)
    result = view.export_contacts()
    assert result is not None


def test_user_export_contacts_sort_city(dbsession):
    user = _user(dbsession, "expccontcity")
    co = _company(dbsession, user, "ExpCityCo")
    _contact(dbsession, user, "ExpCityContact", company=co)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _req(
            dbsession,
            user,
            params={
                "sort": "city",
                "order": order,
                "category": "companies",
            },
        )
        view = UserView(request)
        result = view.export_contacts()
        assert result is not None


def test_user_export_contacts_sort_category_name_companies(dbsession):
    user = _user(dbsession, "expcontcatnam")
    co = _company(dbsession, user, "ExpCatNameCo")
    _contact(dbsession, user, "ExpCatNameCont", company=co)
    transaction.commit()
    request = _req(
        dbsession, user, params={"sort": "category_name", "category": "companies"}
    )
    view = UserView(request)
    result = view.export_contacts()
    assert result is not None


# ===========================================================================
# add() / edit()
# ===========================================================================


def test_user_add_get(dbsession):
    user = _user(dbsession)
    transaction.commit()
    request = _req(dbsession, user, method="GET")
    view = UserView(request)
    result = view.add()
    assert "form" in result


def test_user_add_post(dbsession):
    user = _user(dbsession)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        method="POST",
        post={
            "name": "newuser",
            "fullname": "New User",
            "email": "new@e.com",
            "role": "admin",
            "password": "Str0ng!P@ssw0rd",
        },
    )
    view = UserView(request)
    result = view.add()
    assert isinstance(result, HTTPSeeOther)


def test_user_edit_get(dbsession):
    user = _user(dbsession)
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.edit()
    assert "form" in result


def test_user_edit_post(dbsession):
    user = _user(dbsession)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        method="POST",
        post={
            "name": user.name,
            "fullname": "Updated",
            "email": "u@e.com",
            "role": "admin",
            "password": "Str0ng!P@ssw0rd",
        },
    )
    view = UserView(request)
    result = view.edit()
    assert isinstance(result, HTTPSeeOther)


# ===========================================================================
# delete()
# ===========================================================================


def test_user_delete_without_data(dbsession):
    user = _user(dbsession, "deladmin")
    target = _user(dbsession, "deltarget")
    transaction.commit()
    request = _req(dbsession, user, method="POST", context_user=target)
    view = UserView(request)
    result = view.delete()
    assert result.status_code == 303


def test_user_delete_with_data(dbsession):
    user = _user(dbsession, "delwadmin")
    target = _user(dbsession, "delwtarget")
    co = _company(dbsession, target, "DelCo")
    proj = _project(dbsession, target, "DelProj")
    _contact(dbsession, target, "DelContact1", company=co)
    _contact(dbsession, target, "DelContact2", project=proj)
    _tag(dbsession, target, "DelTag")
    _comment(dbsession, target, company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        method="POST",
        context_user=target,
        params={"delete_with_data": "1"},
    )
    view = UserView(request)
    result = view.delete()
    assert result.status_code == 303


# ===========================================================================
# search()
# ===========================================================================


def test_user_search_get(dbsession):
    user = _user(dbsession)
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.search()
    assert "form" in result


def test_user_search_post(dbsession):
    user = _user(dbsession, "searchuser")
    transaction.commit()
    request = _req(
        dbsession, user, method="POST", post={"name": "test", "role": "default"}
    )
    view = UserView(request)
    result = view.search()
    assert isinstance(result, HTTPSeeOther)


# ===========================================================================
# selected_companies()
# ===========================================================================


def test_user_selected_companies_default(dbsession):
    user = _user(dbsession, "selco")
    co = _company(dbsession, user, "SelCo")
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.selected_companies()
    assert "paginator" in result


def test_user_selected_companies_filters(dbsession):
    user = _user(dbsession, "selcofilt")
    co = _company(dbsession, user, "SelCoFilt", color="red", country="PL")
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "color": "red",
            "country": "PL",
            "subdivision": "PL-14",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.selected_companies()
    assert result["q"]["color"] == "red"


def test_user_selected_companies_invalid_sort(dbsession):
    user = _user(dbsession, "selcoinv")
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "bad", "order": "bad"})
    view = UserView(request)
    result = view.selected_companies()
    assert result["q"]["sort"] == "created_at"


# ===========================================================================
# json_selected_companies() / map_selected_companies()
# ===========================================================================


def test_user_json_selected_companies(dbsession):
    user = _user(dbsession, "jsonselco")
    co = _company(dbsession, user, "JsonSelCo")
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "color": "",
            "country": "PL",
            "subdivision": "PL-14",
        },
    )
    view = UserView(request)
    result = view.json_selected_companies()
    assert isinstance(result, list)


def test_user_map_selected_companies(dbsession):
    user = _user(dbsession, "mapselco")
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.map_selected_companies()
    assert "user" in result
    assert "url" in result


# ===========================================================================
# export_selected_companies()
# ===========================================================================


def test_user_export_selected_companies(dbsession):
    user = _user(dbsession, "expselco")
    co = _company(dbsession, user, "ExpSelCo")
    user.selected_companies.append(co)
    _contact(dbsession, user, "ExpSelCoContact", company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "color": "",
            "country": "PL",
            "subdivision": "PL-14",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_selected_companies()
    assert result is not None


# ===========================================================================
# selected_projects()
# ===========================================================================


def test_user_selected_projects_default(dbsession):
    user = _user(dbsession, "selproj")
    proj = _project(dbsession, user, "SelProj")
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.selected_projects()
    assert "paginator" in result


def test_user_selected_projects_filters(dbsession):
    import datetime

    user = _user(dbsession, "selprojfilt")
    proj = _project(
        dbsession,
        user,
        "SelProjFilt",
        color="red",
        deadline=datetime.datetime.now() + datetime.timedelta(days=30),
    )
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "color": "red",
            "country": "PL",
            "subdivision": "PL-14",
            "status": "in_progress",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.selected_projects()
    assert result["q"]["status"] == "in_progress"


def test_user_selected_projects_status_completed(dbsession):
    import datetime

    user = _user(dbsession, "selprojcompl")
    proj = _project(
        dbsession,
        user,
        "SelProjCompl",
        deadline=datetime.datetime.now() - datetime.timedelta(days=30),
    )
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(dbsession, user, params={"status": "completed"})
    view = UserView(request)
    result = view.selected_projects()
    assert result["q"]["status"] == "completed"


# ===========================================================================
# json_selected_projects() / map_selected_projects()
# ===========================================================================


def test_user_json_selected_projects(dbsession):
    user = _user(dbsession, "jsonselproj")
    proj = _project(dbsession, user, "JsonSelProj")
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "country": "PL",
            "subdivision": "PL-14",
            "status": "in_progress",
        },
    )
    view = UserView(request)
    result = view.json_selected_projects()
    assert isinstance(result, list)


def test_user_map_selected_projects(dbsession):
    user = _user(dbsession, "mapselproj")
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.map_selected_projects()
    assert "user" in result


# ===========================================================================
# export_selected_projects()
# ===========================================================================


def test_user_export_selected_projects(dbsession):
    user = _user(dbsession, "expselproj")
    proj = _project(dbsession, user, "ExpSelProj")
    user.selected_projects.append(proj)
    _contact(dbsession, user, "ExpSelProjCont", project=proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "country": "PL",
            "subdivision": "PL-14",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_selected_projects()
    assert result is not None


# ===========================================================================
# selected_tags()
# ===========================================================================


def test_user_selected_tags_default(dbsession):
    user = _user(dbsession, "seltag")
    tag = _tag(dbsession, user, "SelTag")
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.selected_tags()
    assert "paginator" in result


def test_user_selected_tags_filters(dbsession):
    user = _user(dbsession, "seltagfilt")
    tag = _tag(dbsession, user, "SelTagFilt")
    co = _company(dbsession, user, "SelTagCo")
    tag.companies.append(co)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "companies",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.selected_tags()
    assert "paginator" in result


# ===========================================================================
# selected_tags_companies() / selected_tags_projects()
# ===========================================================================


def test_user_selected_tags_companies(dbsession):
    user = _user(dbsession, "seltagco")
    tag = _tag(dbsession, user, "SelTagCo2")
    co = _company(dbsession, user, "SelTagCo2Co")
    tag.companies.append(co)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "color": "",
            "country": "PL",
            "subdivision": "PL-14",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.selected_tags_companies()
    assert "paginator" in result


def test_user_selected_tags_projects(dbsession):
    user = _user(dbsession, "seltagproj")
    tag = _tag(dbsession, user, "SelTagProj2")
    proj = _project(dbsession, user, "SelTagProj2Proj")
    tag.projects.append(proj)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.selected_tags_projects()
    assert "paginator" in result


# ===========================================================================
# export_selected_tags()
# ===========================================================================


def test_user_export_selected_tags(dbsession):
    user = _user(dbsession, "expseltag")
    tag = _tag(dbsession, user, "ExpSelTag")
    co = _company(dbsession, user, "ExpSelTagCo")
    tag.companies.append(co)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(dbsession, user, params={"category": "companies"})
    view = UserView(request)
    result = view.export_selected_tags()
    assert result is not None


def test_user_export_selected_tags_projects(dbsession):
    user = _user(dbsession, "expseltagp")
    tag = _tag(dbsession, user, "ExpSelTagP")
    proj = _project(dbsession, user, "ExpSelTagProj")
    tag.projects.append(proj)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(dbsession, user, params={"category": "projects"})
    view = UserView(request)
    result = view.export_selected_tags()
    assert result is not None


# ===========================================================================
# selected_companies_contacts / selected_projects_contacts / selected_tags_contacts
# ===========================================================================


def test_user_selected_companies_contacts(dbsession):
    user = _user(dbsession, "selcocontact")
    co = _company(dbsession, user, "SelCoContact")
    _contact(dbsession, user, "SelCoContactC", company=co)
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.selected_companies_contacts()
    assert "paginator" in result
    assert "heading" in result


def test_user_selected_projects_contacts(dbsession):
    user = _user(dbsession, "selprojcontact")
    proj = _project(dbsession, user, "SelProjContact")
    _contact(dbsession, user, "SelProjContactC", project=proj)
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.selected_projects_contacts()
    assert "paginator" in result
    assert "heading" in result


def test_user_selected_tags_contacts(dbsession):
    user = _user(dbsession, "seltagcontact")
    tag = _tag(dbsession, user, "SelTagContact")
    co = _company(dbsession, user, "SelTagContactCo")
    _contact(dbsession, user, "SelTagContactC", company=co)
    tag.companies.append(co)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.selected_tags_contacts()
    assert "paginator" in result


# ===========================================================================
# selected_contacts()
# ===========================================================================


def test_user_selected_contacts_default(dbsession):
    user = _user(dbsession, "selcont")
    contact = _contact(dbsession, user, "SelCont")
    user.selected_contacts.append(contact)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.selected_contacts()
    assert "paginator" in result


def test_user_selected_contacts_filters(dbsession):
    user = _user(dbsession, "selcontfilt")
    co = _company(dbsession, user, "SelContFiltCo")
    contact = _contact(dbsession, user, "SelContFilt", company=co, color="red")
    user.selected_contacts.append(contact)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "color": "red",
            "country": "PL",
            "subdivision": "PL-14",
            "category": "companies",
            "sort": "city",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.selected_contacts()
    assert "paginator" in result


def test_user_selected_contacts_category_projects(dbsession):
    user = _user(dbsession, "selcontproj")
    proj = _project(dbsession, user, "SelContProj")
    contact = _contact(dbsession, user, "SelContProj2", project=proj)
    user.selected_contacts.append(contact)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "projects",
            "sort": "city",
            "order": "desc",
        },
    )
    view = UserView(request)
    result = view.selected_contacts()
    assert "paginator" in result


def test_user_selected_contacts_no_category_sort_city(dbsession):
    user = _user(dbsession, "selcontnocat")
    co = _company(dbsession, user, "SelContNoCatCo")
    contact = _contact(dbsession, user, "SelContNoCat", company=co)
    user.selected_contacts.append(contact)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _req(dbsession, user, params={"sort": "city", "order": order})
        view = UserView(request)
        result = view.selected_contacts()
        assert "paginator" in result


def test_user_selected_contacts_sort_category_name(dbsession):
    user = _user(dbsession, "selcontcatnam")
    co = _company(dbsession, user, "SelContCatNameCo")
    contact = _contact(dbsession, user, "SelContCatName", company=co)
    user.selected_contacts.append(contact)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _req(
            dbsession, user, params={"sort": "category_name", "order": order}
        )
        view = UserView(request)
        result = view.selected_contacts()
        assert "paginator" in result


def test_user_selected_contacts_sort_generic(dbsession):
    user = _user(dbsession, "selcontgen")
    contact = _contact(dbsession, user, "SelContGen")
    user.selected_contacts.append(contact)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _req(dbsession, user, params={"sort": "name", "order": order})
        view = UserView(request)
        result = view.selected_contacts()
        assert "paginator" in result


# ===========================================================================
# export_selected_contacts()
# ===========================================================================


def test_user_export_selected_contacts_companies(dbsession):
    user = _user(dbsession, "expselcont")
    co = _company(dbsession, user, "ExpSelContCo")
    contact = _contact(dbsession, user, "ExpSelCont", company=co)
    user.selected_contacts.append(contact)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "companies",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


def test_user_export_selected_contacts_projects(dbsession):
    user = _user(dbsession, "expselcontp")
    proj = _project(dbsession, user, "ExpSelContProj")
    contact = _contact(dbsession, user, "ExpSelContP", project=proj)
    user.selected_contacts.append(contact)
    transaction.commit()
    request = _req(dbsession, user, params={"category": "projects"})
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


# ===========================================================================
# delete_selected_*
# ===========================================================================


def test_user_delete_selected_companies(dbsession):
    user = _user(dbsession, "delselco")
    co = _company(dbsession, user, "DelSelCo")
    _contact(dbsession, user, "DelSelCoCont", company=co)
    user.selected_companies.append(co)
    user.companies_stars.append(co)
    transaction.commit()
    request = _req(dbsession, user, method="POST")
    view = UserView(request)
    result = view.delete_selected_companies()
    assert result.status_code == 303


def test_user_delete_selected_projects(dbsession):
    user = _user(dbsession, "delselproj")
    proj = _project(dbsession, user, "DelSelProj")
    _contact(dbsession, user, "DelSelProjCont", project=proj)
    user.selected_projects.append(proj)
    user.projects_stars.append(proj)
    transaction.commit()
    request = _req(dbsession, user, method="POST")
    view = UserView(request)
    result = view.delete_selected_projects()
    assert result.status_code == 303


def test_user_delete_selected_contacts(dbsession):
    user = _user(dbsession, "delselcont")
    contact = _contact(dbsession, user, "DelSelCont")
    user.selected_contacts.append(contact)
    transaction.commit()
    request = _req(dbsession, user, method="POST")
    view = UserView(request)
    result = view.delete_selected_contacts()
    assert result.status_code == 303


def test_user_delete_selected_tags(dbsession):
    user = _user(dbsession, "delseltag")
    tag = _tag(dbsession, user, "DelSelTag")
    co = _company(dbsession, user, "DelSelTagCo")
    proj = _project(dbsession, user, "DelSelTagProj")
    tag.companies.append(co)
    tag.projects.append(proj)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(dbsession, user, method="POST")
    view = UserView(request)
    result = view.delete_selected_tags()
    assert result.status_code == 303


# ===========================================================================
# merge_selected_tags()
# ===========================================================================


def test_user_merge_selected_tags_no_name(dbsession):
    user = _user(dbsession, "mergenoname")
    tag = _tag(dbsession, user, "MergeNoName")
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(dbsession, user, method="POST", params={})
    view = UserView(request)
    result = view.merge_selected_tags()
    assert result.status_code == 303


def test_user_merge_selected_tags_new(dbsession):
    user = _user(dbsession, "mergenew")
    t1 = _tag(dbsession, user, "MergeNew1")
    t2 = _tag(dbsession, user, "MergeNew2")
    co = _company(dbsession, user, "MergeNewCo")
    proj = _project(dbsession, user, "MergeNewProj")
    t1.companies.append(co)
    t2.projects.append(proj)
    user.selected_tags.append(t1)
    user.selected_tags.append(t2)
    transaction.commit()
    request = _req(
        dbsession, user, method="POST", params={"merge_tag_name": "MergedTag"}
    )
    view = UserView(request)
    result = view.merge_selected_tags()
    assert result.status_code == 303


def test_user_merge_selected_tags_existing(dbsession):
    user = _user(dbsession, "mergeexist")
    t1 = _tag(dbsession, user, "MergeExist1")
    t2 = _tag(dbsession, user, "MergeExist2")
    co = _company(dbsession, user, "MergeExistCo")
    t1.companies.append(co)
    user.selected_tags.append(t1)
    user.selected_tags.append(t2)
    transaction.commit()
    request = _req(
        dbsession, user, method="POST", params={"merge_tag_name": "MergeExist1"}
    )
    view = UserView(request)
    result = view.merge_selected_tags()
    assert result.status_code == 303


# ===========================================================================
# companies_stars()
# ===========================================================================


def test_user_companies_stars_default(dbsession):
    user = _user(dbsession, "costaruser")
    co = _company(dbsession, user, "StarCo")
    user.companies_stars.append(co)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.companies_stars()
    assert "paginator" in result


def test_user_companies_stars_filters(dbsession):
    user = _user(dbsession, "costarfilt")
    co = _company(dbsession, user, "StarFiltCo", color="red")
    user.companies_stars.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "color": "red",
            "country": "PL",
            "subdivision": "PL-14",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.companies_stars()
    assert result["q"]["color"] == "red"


def test_user_companies_stars_invalid_sort(dbsession):
    user = _user(dbsession, "costarinvsort")
    transaction.commit()
    request = _req(dbsession, user, params={"sort": "bad", "order": "bad"})
    view = UserView(request)
    result = view.companies_stars()
    assert result["q"]["sort"] == "created_at"


# ===========================================================================
# export_companies_stars()
# ===========================================================================


def test_user_export_companies_stars(dbsession):
    user = _user(dbsession, "expcostar")
    co = _company(dbsession, user, "ExpStarCo")
    user.companies_stars.append(co)
    _contact(dbsession, user, "ExpStarCoContact", company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "color": "",
            "country": "PL",
            "subdivision": "PL-14",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_companies_stars()
    assert result is not None


# ===========================================================================
# clear_companies_stars()
# ===========================================================================


def test_user_clear_companies_stars(dbsession):
    user = _user(dbsession, "clearcostar")
    co = _company(dbsession, user, "ClearStarCo")
    user.companies_stars.append(co)
    transaction.commit()
    request = _req(dbsession, user, method="POST")
    view = UserView(request)
    result = view.clear_companies_stars()
    assert result.status_code == 303


# ===========================================================================
# json_companies_stars() / map_companies_stars()
# ===========================================================================


def test_user_json_companies_stars(dbsession):
    user = _user(dbsession, "jsoncostar")
    co = _company(dbsession, user, "JsonStarCo")
    user.companies_stars.append(co)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.json_companies_stars()
    assert isinstance(result, list)
    assert len(result) == 1


def test_user_map_companies_stars(dbsession):
    user = _user(dbsession, "mapcostar")
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.map_companies_stars()
    assert "user" in result
    assert "counter" in result


# ===========================================================================
# projects_stars()
# ===========================================================================


def test_user_projects_stars_default(dbsession):
    user = _user(dbsession, "pstaruser")
    proj = _project(dbsession, user, "StarProj")
    user.projects_stars.append(proj)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.projects_stars()
    assert "paginator" in result


def test_user_projects_stars_filters(dbsession):
    import datetime

    user = _user(dbsession, "pstarfilt")
    proj = _project(
        dbsession,
        user,
        "StarFiltProj",
        color="red",
        deadline=datetime.datetime.now() + datetime.timedelta(days=30),
    )
    user.projects_stars.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "status": "in_progress",
            "color": "red",
            "country": "PL",
            "subdivision": "PL-14",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.projects_stars()
    assert result["q"]["status"] == "in_progress"


def test_user_projects_stars_completed(dbsession):
    import datetime

    user = _user(dbsession, "pstarcompl")
    proj = _project(
        dbsession,
        user,
        "StarComplProj",
        deadline=datetime.datetime.now() - datetime.timedelta(days=30),
    )
    user.projects_stars.append(proj)
    transaction.commit()
    request = _req(dbsession, user, params={"status": "completed"})
    view = UserView(request)
    result = view.projects_stars()
    assert result["q"]["status"] == "completed"


# ===========================================================================
# export_projects_stars()
# ===========================================================================


def test_user_export_projects_stars(dbsession):
    user = _user(dbsession, "exppstar")
    proj = _project(dbsession, user, "ExpStarProj")
    user.projects_stars.append(proj)
    _contact(dbsession, user, "ExpStarProjCont", project=proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "color": "",
            "country": "PL",
            "subdivision": "PL-14",
            "status": "in_progress",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_projects_stars()
    assert result is not None


# ===========================================================================
# clear_projects_stars()
# ===========================================================================


def test_user_clear_projects_stars(dbsession):
    user = _user(dbsession, "clearpstar")
    proj = _project(dbsession, user, "ClearStarProj")
    user.projects_stars.append(proj)
    transaction.commit()
    request = _req(dbsession, user, method="POST")
    view = UserView(request)
    result = view.clear_projects_stars()
    assert result.status_code == 303


# ===========================================================================
# json_projects_stars() / map_projects_stars()
# ===========================================================================


def test_user_json_projects_stars(dbsession):
    user = _user(dbsession, "jsonpstar")
    proj = _project(dbsession, user, "JsonStarProj")
    user.projects_stars.append(proj)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.json_projects_stars()
    assert isinstance(result, list)


def test_user_map_projects_stars(dbsession):
    user = _user(dbsession, "mappstar")
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.map_projects_stars()
    assert "user" in result


# ===========================================================================
# count_* methods
# ===========================================================================


def test_user_count_companies(dbsession):
    user = _user(dbsession, "cntco")
    _company(dbsession, user, "CntCo")
    request = _req(dbsession, user)
    view = UserView(request)
    result = UserView.count_companies(view)
    assert result == 1


def test_user_count_projects(dbsession):
    user = _user(dbsession, "cntproj")
    _project(dbsession, user, "CntProj")
    request = _req(dbsession, user)
    view = UserView(request)
    result = UserView.count_projects(view)
    assert result == 1


def test_user_count_tags(dbsession):
    user = _user(dbsession, "cnttag")
    _tag(dbsession, user, "CntTag")
    request = _req(dbsession, user)
    view = UserView(request)
    result = UserView.count_tags(view)
    assert result == 1


def test_user_count_contacts(dbsession):
    user = _user(dbsession, "cntcont")
    _contact(dbsession, user, "CntCont")
    request = _req(dbsession, user)
    view = UserView(request)
    result = UserView.count_contacts(view)
    assert result == 1


def test_user_count_comments(dbsession):
    user = _user(dbsession, "cntcmt")
    _comment(dbsession, user)
    request = _req(dbsession, user)
    view = UserView(request)
    result = UserView.count_comments(view)
    assert result == 1


# ===========================================================================
# map_companies() / map_projects()
# ===========================================================================


def test_user_map_companies(dbsession):
    user = _user(dbsession, "mapco")
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.map_companies()
    assert "user" in result
    assert "url" in result
    assert "user_pills" in result


def test_user_map_projects(dbsession):
    user = _user(dbsession, "mapproj")
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.map_projects()
    assert "user" in result
    assert "url" in result


# ===========================================================================
# json_companies() / json_projects()
# ===========================================================================


def test_user_json_companies(dbsession):
    user = _user(dbsession, "jsonco")
    _company(dbsession, user, "JsonCo")
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.json_companies()
    assert isinstance(result, list)
    assert len(result) == 1


def test_user_json_companies_bbox(dbsession):
    user = _user(dbsession, "jsoncobbox")
    _company(dbsession, user, "JsonCoBbox")
    request = _req(
        dbsession,
        user,
        params={
            "north": "51",
            "south": "49",
            "east": "21",
            "west": "19",
        },
    )
    view = UserView(request)
    result = view.json_companies()
    assert isinstance(result, list)


def test_user_json_companies_invalid_bbox(dbsession):
    user = _user(dbsession, "jsoncoinvbbox")
    _company(dbsession, user, "JsonCoInvBbox")
    request = _req(
        dbsession,
        user,
        params={
            "north": "abc",
            "south": "def",
            "east": "ghi",
            "west": "jkl",
        },
    )
    view = UserView(request)
    result = view.json_companies()
    assert isinstance(result, list)


def test_user_json_projects(dbsession):
    user = _user(dbsession, "jsonproj")
    _project(dbsession, user, "JsonProj")
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.json_projects()
    assert isinstance(result, list)
    assert len(result) == 1


def test_user_json_projects_bbox(dbsession):
    user = _user(dbsession, "jsonprojbbox")
    _project(dbsession, user, "JsonProjBbox")
    request = _req(
        dbsession,
        user,
        params={
            "north": "51",
            "south": "49",
            "east": "21",
            "west": "19",
        },
    )
    view = UserView(request)
    result = view.json_projects()
    assert isinstance(result, list)


def test_user_json_projects_invalid_bbox(dbsession):
    user = _user(dbsession, "jsonprojinvbb")
    _project(dbsession, user, "JsonProjInvBb")
    request = _req(
        dbsession,
        user,
        params={
            "north": "abc",
            "south": "def",
            "east": "ghi",
            "west": "jkl",
        },
    )
    view = UserView(request)
    result = view.json_projects()
    assert isinstance(result, list)


# ===========================================================================
# Phase 2 – remaining user.py coverage gaps
# ===========================================================================


# --- _tag_export_rows companies branch (lines 520-528) ---


def test_user_export_tags_companies_branch(dbsession):
    """export_tags with category=companies exercises _tag_export_rows companies branch."""
    user = _user(dbsession, "texpc")
    tag = _tag(dbsession, user, "TExpCTag")
    co = _company(dbsession, user, "TExpCCo")
    tag.companies.append(co)
    _contact(dbsession, user, "TExpCCont", company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "companies",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_tags()
    assert result is not None


def test_user_export_tags_companies_no_contacts(dbsession):
    """Tag with company but no contacts on that company."""
    user = _user(dbsession, "texpcnc")
    tag = _tag(dbsession, user, "TExpCNCTag")
    co = _company(dbsession, user, "TExpCNCCo")
    tag.companies.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "companies",
            "sort": "name",
            "order": "desc",
        },
    )
    view = UserView(request)
    result = view.export_tags()
    assert result is not None


# --- export_tags invalid sort/order (lines 839, 842) ---


def test_user_export_tags_invalid_sort_order(dbsession):
    user = _user(dbsession, "texinv")
    _tag(dbsession, user, "TExpInvTag")
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = UserView(request)
    result = view.export_tags()
    assert result is not None


def test_user_export_tags_projects_no_projects(dbsession):
    """Cover lines 520-528: tag with category=projects but tag has no projects."""
    user = _user(dbsession, "texpnp")
    tag = _tag(dbsession, user, "TExpNoProjTag")
    # tag has no projects
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "projects",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_tags()
    assert result is not None


def test_user_export_contacts_sort_country_projects(dbsession):
    """Cover lines 1725-1730: export_contacts country sort with projects category."""
    user = _user(dbsession, "texccp")
    proj = _project(dbsession, user, "TExCCProj")
    from marker.models.contact import Contact

    c = Contact(name="TExCCCont", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.project = proj
    dbsession.add(c)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "country",
            "order": "asc",
            "category": "projects",
        },
    )
    view = UserView(request)
    result = view.export_contacts()
    assert result is not None


def test_user_export_contacts_sort_country_companies(dbsession):
    """Cover lines 1731-1736: export_contacts country sort with companies."""
    user = _user(dbsession, "texccco")
    co = _company(dbsession, user, "TExCCComp")
    from marker.models.contact import Contact

    c = Contact(name="TExCCCoCont", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.company = co
    dbsession.add(c)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "country",
            "order": "desc",
            "category": "companies",
        },
    )
    view = UserView(request)
    result = view.export_contacts()
    assert result is not None


def test_user_export_contacts_color_filter(dbsession):
    """Cover line 1722: export_contacts color filter."""
    user = _user(dbsession, "texccolor")
    co = _company(dbsession, user, "TExColorComp")
    from marker.models.contact import Contact

    c = Contact(name="TExColorCont", role="r", phone="1", email="a@b.com", color="red")
    c.created_by = user
    c.company = co
    dbsession.add(c)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "color": "red",
        },
    )
    view = UserView(request)
    result = view.export_contacts()
    assert result is not None


def test_user_export_contacts_sort_country_projects_desc(dbsession):
    """Cover lines 1729-1730: export_contacts country sort projects desc."""
    user = _user(dbsession, "texccpd")
    proj = _project(dbsession, user, "TExCCPdProj")
    from marker.models.contact import Contact

    c = Contact(name="TExCCPdCont", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.project = proj
    dbsession.add(c)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "country",
            "order": "desc",
            "category": "projects",
        },
    )
    view = UserView(request)
    result = view.export_contacts()
    assert result is not None


def test_user_export_contacts_sort_country_companies_asc(dbsession):
    """Cover line 1734: export_contacts country sort companies asc."""
    user = _user(dbsession, "texcccoa")
    co = _company(dbsession, user, "TExCCCoAComp")
    from marker.models.contact import Contact

    c = Contact(name="TExCCCoACont", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.company = co
    dbsession.add(c)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "country",
            "order": "asc",
            "category": "companies",
        },
    )
    view = UserView(request)
    result = view.export_contacts()
    assert result is not None


def test_user_selected_projects_stage_filter(dbsession):
    """Cover lines 2187-2188: selected projects stage filter."""
    user = _user(dbsession, "tselstage")
    proj = _project(dbsession, user, "TSelStageProj")
    proj.stage = "design"
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "stage": "design",
        },
    )
    view = UserView(request)
    result = view.selected_projects()
    assert "q" in result


def test_user_selected_projects_delivery_method_filter(dbsession):
    """Cover lines 2191-2192: selected projects delivery_method filter."""
    user = _user(dbsession, "tseldm")
    proj = _project(dbsession, user, "TSelDmProj")
    proj.delivery_method = "general_contractor"
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "delivery_method": "general_contractor",
        },
    )
    view = UserView(request)
    result = view.selected_projects()
    assert "q" in result


def test_user_selected_projects_bulk_select(dbsession):
    """Cover line 2200: selected_projects bulk selection."""
    user = _user(dbsession, "tspbulk")
    proj = _project(dbsession, user, "TSpBulkProj")
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        method="POST",
        params={
            "_select_all": "1",
            "checked": "1",
        },
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = UserView(request)
    result = view.selected_projects()
    assert result is request.response


def test_user_json_selected_projects_color(dbsession):
    """Cover line 2271: json_selected_projects color filter."""
    user = _user(dbsession, "tjspcolor")
    proj = _project(dbsession, user, "TJspColorProj")
    proj.color = "red"
    proj.latitude = 50.0
    proj.longitude = 20.0
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(dbsession, user, params={"color": "red"})
    view = UserView(request)
    result = view.json_selected_projects()
    assert isinstance(result, list)


def test_user_json_selected_projects_delivery_method(dbsession):
    """Cover line 2283: json_selected_projects delivery_method filter."""
    user = _user(dbsession, "tjspdm")
    proj = _project(dbsession, user, "TJspDmProj")
    proj.delivery_method = "general_contractor"
    proj.latitude = 50.0
    proj.longitude = 20.0
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(dbsession, user, params={"delivery_method": "general_contractor"})
    view = UserView(request)
    result = view.json_selected_projects()
    assert isinstance(result, list)


def test_user_selected_projects_contacts_country_subdivision(dbsession):
    """Cover lines 2931-2937: _selected_related_contacts projects country/subdivision."""
    user = _user(dbsession, "tscpcat")
    proj = _project(dbsession, user, "TScpCatProj")
    from marker.models.contact import Contact

    c = Contact(name="TScpCatCont", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.project = proj
    dbsession.add(c)
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "country": "PL",
            "subdivision": "PL-14",
        },
    )
    view = UserView(request)
    result = view.selected_projects_contacts()
    assert isinstance(result, dict)


def test_user_selected_projects_contacts_sort_city_related(dbsession):
    """Cover lines 2974: _selected_related_contacts city sort projects."""
    user = _user(dbsession, "tsccityp")
    proj = _project(dbsession, user, "TScCityProj")
    from marker.models.contact import Contact

    c = Contact(name="TScCityCont", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.project = proj
    dbsession.add(c)
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "city",
            "order": "desc",
        },
    )
    view = UserView(request)
    result = view.selected_projects_contacts()
    assert isinstance(result, dict)


def test_user_selected_companies_contacts_sort_city_asc(dbsession):
    """Cover lines 2981-2982: _selected_related_contacts city sort companies asc."""
    user = _user(dbsession, "tsccityco")
    co = _company(dbsession, user, "TScCityComp")
    from marker.models.contact import Contact

    c = Contact(name="TScCityCoCont", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.company = co
    dbsession.add(c)
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "city",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.selected_companies_contacts()
    assert isinstance(result, dict)


def test_user_selected_companies_contacts_sort_city_desc(dbsession):
    """Cover lines 2989-2990: _selected_related_contacts city sort companies desc."""
    user = _user(dbsession, "tsccityd")
    co = _company(dbsession, user, "TScCityDComp")
    from marker.models.contact import Contact

    c = Contact(name="TScCityDCont", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.company = co
    dbsession.add(c)
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "city",
            "order": "desc",
        },
    )
    view = UserView(request)
    result = view.selected_companies_contacts()
    assert isinstance(result, dict)


def test_user_export_selected_contacts_projects_country_subdivision(dbsession):
    """Cover line 3370: export_selected_contacts projects country/subdivision."""
    user = _user(dbsession, "tescpc")
    proj = _project(dbsession, user, "TEscpcProj")
    from marker.models.contact import Contact

    c = Contact(name="TEscpcCont", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.project = proj
    dbsession.add(c)
    user.selected_contacts.append(c)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "projects",
            "country": "PL",
            "subdivision": "PL-14",
        },
    )
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


def test_user_export_selected_contacts_companies_subdivision(dbsession):
    """Cover line 3362: export_selected_contacts companies subdivision."""
    user = _user(dbsession, "tesccsub")
    co = _company(dbsession, user, "TEscSubComp")
    from marker.models.contact import Contact

    c = Contact(name="TEscSubCont", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.company = co
    dbsession.add(c)
    user.selected_contacts.append(c)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "companies",
            "subdivision": "PL-14",
        },
    )
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


def test_user_export_selected_contacts_sort_country_projects(dbsession):
    """Cover lines 3380-3385: export_selected_contacts country sort projects."""
    user = _user(dbsession, "tesccntp")
    proj = _project(dbsession, user, "TEsccntpProj")
    from marker.models.contact import Contact

    c = Contact(name="TEsccntpCont", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.project = proj
    dbsession.add(c)
    user.selected_contacts.append(c)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "country",
            "order": "asc",
            "category": "projects",
        },
    )
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


def test_user_export_selected_contacts_sort_country_companies(dbsession):
    """Cover lines 3386-3391: export_selected_contacts country sort companies."""
    user = _user(dbsession, "tesccntco")
    co = _company(dbsession, user, "TEsccntcoComp")
    from marker.models.contact import Contact

    c = Contact(name="TEsccntcoCont", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.company = co
    dbsession.add(c)
    user.selected_contacts.append(c)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "country",
            "order": "desc",
            "category": "companies",
        },
    )
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


def test_user_export_selected_contacts_sort_country_projects_desc(dbsession):
    """Cover lines 3384-3385: export_selected_contacts projects country desc."""
    user = _user(dbsession, "tesccntpd")
    proj = _project(dbsession, user, "TEsccntpdProj")
    from marker.models.contact import Contact

    c = Contact(name="TEsccntpdCont", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.project = proj
    dbsession.add(c)
    user.selected_contacts.append(c)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "country",
            "order": "desc",
            "category": "projects",
        },
    )
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


def test_user_export_selected_contacts_sort_country_companies_asc(dbsession):
    """Cover line 3389: export_selected_contacts companies country asc."""
    user = _user(dbsession, "tesccntcoa")
    co = _company(dbsession, user, "TEsccntcoaComp")
    from marker.models.contact import Contact

    c = Contact(name="TEsccntcoaCont", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.company = co
    dbsession.add(c)
    user.selected_contacts.append(c)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "country",
            "order": "asc",
            "category": "companies",
        },
    )
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


def test_user_export_selected_contacts_color_filter(dbsession):
    """Cover color filter in export_selected_contacts."""
    user = _user(dbsession, "tescolor")
    co = _company(dbsession, user, "TEsColorComp")
    from marker.models.contact import Contact

    c = Contact(name="TEsColorCont", role="r", phone="1", email="a@b.com", color="blue")
    c.created_by = user
    c.company = co
    dbsession.add(c)
    user.selected_contacts.append(c)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "color": "blue",
        },
    )
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


# --- tags bulk selection (line 785) ---


def test_user_tags_bulk_select(dbsession):
    user = _user(dbsession, "tbulk")
    _tag(dbsession, user, "TBulkTag")
    transaction.commit()
    request = _req(
        dbsession, user, method="POST", params={"_select_all": "1", "checked": "1"}
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = UserView(request)
    result = view.tags()
    assert result is request.response


# --- companies bulk selection (line 983) ---


def test_user_companies_bulk_select(dbsession):
    user = _user(dbsession, "cbulk")
    _company(dbsession, user, "CBulkCo")
    transaction.commit()
    request = _req(
        dbsession, user, method="POST", params={"_select_all": "1", "checked": "1"}
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = UserView(request)
    result = view.companies()
    assert result is request.response


# --- export_companies invalid sort/order + color + generic asc sort (lines 1062,1065,1094,1128) ---


def test_user_export_companies_invalid_sort_order(dbsession):
    user = _user(dbsession, "ecoinvsort")
    _company(dbsession, user, "ECoInvSortCo")
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = UserView(request)
    result = view.export_companies()
    assert result is not None


def test_user_export_companies_color_filter(dbsession):
    user = _user(dbsession, "ecocolor")
    _company(dbsession, user, "ECoColorCo", color="red")
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "color": "red",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_companies()
    assert result is not None


# --- projects bulk selection (line 1289) ---


def test_user_projects_bulk_select(dbsession):
    user = _user(dbsession, "pbulk")
    _project(dbsession, user, "PBulkProj")
    transaction.commit()
    request = _req(
        dbsession, user, method="POST", params={"_select_all": "1", "checked": "1"}
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = UserView(request)
    result = view.projects()
    assert result is request.response


# --- export_projects invalid sort/order + filters (lines 1376,1379,1408,1411,1414,1423,1455) ---


def test_user_export_projects_invalid_sort_order(dbsession):
    user = _user(dbsession, "eprojinvsort")
    _project(dbsession, user, "EProjInvSortP")
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = UserView(request)
    result = view.export_projects()
    assert result is not None


def test_user_export_projects_filters(dbsession):
    import datetime

    user = _user(dbsession, "eprojfilt")
    _project(
        dbsession,
        user,
        "EProjFiltP",
        color="blue",
        stage="design",
        delivery_method="general_contractor",
        deadline=datetime.datetime.now() - datetime.timedelta(days=10),
    )
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "color": "blue",
            "stage": "design",
            "delivery_method": "general_contractor",
            "status": "completed",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_projects()
    assert result is not None


# --- contacts bulk selection (line 1570) ---


def test_user_contacts_bulk_select(dbsession):
    user = _user(dbsession, "contbulk")
    co = _company(dbsession, user, "ContBulkCo")
    _contact(dbsession, user, "ContBulk", company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        method="POST",
        params={"_select_all": "1", "checked": "1", "category": "companies"},
    )
    request.params = MultiDict(
        {"_select_all": "1", "checked": "1", "category": "companies"}
    )
    view = UserView(request)
    result = view.contacts()
    assert result is request.response


# --- export_contacts invalid order + projects-category filters + geo sort + category_name sort ---
# (lines 1687,1706,1708,1722-1745)


def test_user_export_contacts_invalid_order(dbsession):
    user = _user(dbsession, "econtinvord")
    co = _company(dbsession, user, "ECIoCo")
    _contact(dbsession, user, "ECIoCont", company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "order": "INVALID",
            "category": "companies",
        },
    )
    view = UserView(request)
    result = view.export_contacts()
    assert result is not None


def test_user_export_contacts_projects_country_subdivision(dbsession):
    user = _user(dbsession, "econtprojgeo")
    proj = _project(dbsession, user, "EContProjGeoP")
    _contact(dbsession, user, "EContProjGeoCont", project=proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "projects",
            "country": "PL",
            "subdivision": "PL-14",
        },
    )
    view = UserView(request)
    result = view.export_contacts()
    assert result is not None


def test_user_export_contacts_sort_city_projects(dbsession):
    user = _user(dbsession, "econtcityp")
    proj = _project(dbsession, user, "ECCityProjP")
    _contact(dbsession, user, "ECCityProjCont", project=proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "projects",
            "sort": "city",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_contacts()
    assert result is not None


def test_user_export_contacts_sort_city_companies_desc(dbsession):
    user = _user(dbsession, "econtcitycd")
    co = _company(dbsession, user, "ECCityCoCd")
    _contact(dbsession, user, "ECCityCoCdCont", company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "companies",
            "sort": "city",
            "order": "desc",
        },
    )
    view = UserView(request)
    result = view.export_contacts()
    assert result is not None


def test_user_export_contacts_sort_city_no_category(dbsession):
    user = _user(dbsession, "econtcitync")
    co = _company(dbsession, user, "ECCityNcCo")
    _contact(dbsession, user, "ECCityNcCont", company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "city",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_contacts()
    assert result is not None


def test_user_export_contacts_sort_category_name_asc(dbsession):
    user = _user(dbsession, "econtcatname")
    co = _company(dbsession, user, "ECCatNmCo")
    _contact(dbsession, user, "ECCatNmCont", company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "category_name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_contacts()
    assert result is not None


def test_user_export_contacts_sort_category_name_desc(dbsession):
    user = _user(dbsession, "econtcatnmd")
    co = _company(dbsession, user, "ECCatNmDCo")
    _contact(dbsession, user, "ECCatNmDCont", company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "category_name",
            "order": "desc",
        },
    )
    view = UserView(request)
    result = view.export_contacts()
    assert result is not None


# --- selected_companies bulk selection (line 1919) ---


def test_user_selected_companies_bulk_select(dbsession):
    user = _user(dbsession, "selcobulk")
    co = _company(dbsession, user, "SelCoBulkCo")
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(
        dbsession, user, method="POST", params={"_select_all": "1", "checked": "1"}
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = UserView(request)
    result = view.selected_companies()
    assert result is request.response


# --- json_selected_companies color filter (line 1979) ---


def test_user_json_selected_companies_color(dbsession):
    user = _user(dbsession, "jsonselcoclr")
    co = _company(dbsession, user, "JsonSelCoClrCo", color="red")
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(dbsession, user, params={"color": "red"})
    view = UserView(request)
    result = view.json_selected_companies()
    assert isinstance(result, list)


# --- map_selected_companies (lines 2031-2055) ---


def test_user_map_selected_companies_filters(dbsession):
    user = _user(dbsession, "mapselcofl")
    co = _company(dbsession, user, "MapSelCoFlCo", color="red")
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
            "color": "red",
            "country": "PL",
            "subdivision": "PL-14",
        },
    )
    view = UserView(request)
    result = view.map_selected_companies()
    assert "user" in result


def test_user_map_selected_companies_asc(dbsession):
    user = _user(dbsession, "mapselcoasc")
    co = _company(dbsession, user, "MapSelCoAscCo")
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.map_selected_companies()
    assert "user" in result


# --- export_selected_companies sort (lines 2090-2104) ---


def test_user_export_selected_companies_sort(dbsession):
    user = _user(dbsession, "expselcosrt")
    co = _company(dbsession, user, "ExpSelCoSrtCo")
    user.selected_companies.append(co)
    _contact(dbsession, user, "ExpSelCoSrtCont", company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = UserView(request)
    result = view.export_selected_companies()
    assert result is not None


def test_user_export_selected_companies_asc_desc(dbsession):
    user = _user(dbsession, "expselcoad")
    co = _company(dbsession, user, "ExpSelCoADCo")
    user.selected_companies.append(co)
    _contact(dbsession, user, "ExpSelCoADCont", company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_selected_companies()
    assert result is not None


# --- selected_projects sort/filter (lines 2156-2200) ---


def test_user_selected_projects_sort_order_fallback(dbsession):
    user = _user(dbsession, "selpinvsrt")
    _project(dbsession, user, "SelPInvSrtP")
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = UserView(request)
    result = view.selected_projects()
    assert "paginator" in result


def test_user_selected_projects_color_country(dbsession):
    user = _user(dbsession, "selpclrcntry")
    proj = _project(dbsession, user, "SelPClrCntryP", color="red")
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "color": "red",
            "country": "PL",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.selected_projects()
    assert "paginator" in result


# --- json_selected_projects filters (lines 2267-2283) ---


def test_user_json_selected_projects_filters(dbsession):
    import datetime

    user = _user(dbsession, "jselselpfl")
    proj = _project(
        dbsession,
        user,
        "JSelPFlP",
        deadline=datetime.datetime.now() + datetime.timedelta(days=10),
        stage="design",
        delivery_method="general_contractor",
    )
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "status": "in_progress",
            "subdivision": "PL-14",
            "stage": "design",
        },
    )
    view = UserView(request)
    result = view.json_selected_projects()
    assert isinstance(result, list)


def test_user_json_selected_projects_completed(dbsession):
    import datetime

    user = _user(dbsession, "jselselpcompl")
    proj = _project(
        dbsession,
        user,
        "JSelPComplP",
        deadline=datetime.datetime.now() - datetime.timedelta(days=10),
    )
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(dbsession, user, params={"status": "completed"})
    view = UserView(request)
    result = view.json_selected_projects()
    assert isinstance(result, list)


# --- map_selected_projects filters (lines 2334-2373) ---


def test_user_map_selected_projects_sort_fallback(dbsession):
    user = _user(dbsession, "mapselpsrt")
    _project(dbsession, user, "MapSelPSrtP")
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = UserView(request)
    result = view.map_selected_projects()
    assert "user" in result


def test_user_map_selected_projects_all_filters(dbsession):
    import datetime

    user = _user(dbsession, "mapselpall")
    proj = _project(
        dbsession,
        user,
        "MapSelPAllP",
        color="red",
        stage="design",
        delivery_method="general_contractor",
        deadline=datetime.datetime.now() + datetime.timedelta(days=10),
    )
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "status": "in_progress",
            "color": "red",
            "country": "PL",
            "subdivision": "PL-14",
            "stage": "design",
            "delivery_method": "general_contractor",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.map_selected_projects()
    assert "user" in result


def test_user_map_selected_projects_completed(dbsession):
    import datetime

    user = _user(dbsession, "mapselpcomp")
    proj = _project(
        dbsession,
        user,
        "MapSelPCompP",
        deadline=datetime.datetime.now() - datetime.timedelta(days=10),
    )
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(dbsession, user, params={"status": "completed"})
    view = UserView(request)
    result = view.map_selected_projects()
    assert "user" in result


# --- export_selected_projects sort (lines 2408-2422) ---


def test_user_export_selected_projects_sort_fallback(dbsession):
    user = _user(dbsession, "expselpinvsrt")
    proj = _project(dbsession, user, "ExpSelPInvSrtP")
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = UserView(request)
    result = view.export_selected_projects()
    assert result is not None


def test_user_export_selected_projects_asc(dbsession):
    user = _user(dbsession, "expselpasc")
    proj = _project(dbsession, user, "ExpSelPAscP")
    user.selected_projects.append(proj)
    _contact(dbsession, user, "ExpSelPAscCont", project=proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_selected_projects()
    assert result is not None


# --- selected_tags sort/order + bulk selection (lines 2459,2462,2480) ---


def test_user_selected_tags_sort_fallback(dbsession):
    user = _user(dbsession, "seltinvsrt")
    _tag(dbsession, user, "SelTInvSrtTag")
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = UserView(request)
    result = view.selected_tags()
    assert "paginator" in result


def test_user_selected_tags_bulk_select(dbsession):
    user = _user(dbsession, "seltbulk")
    tag = _tag(dbsession, user, "SelTBulkTag")
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(
        dbsession, user, method="POST", params={"_select_all": "1", "checked": "1"}
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = UserView(request)
    result = view.selected_tags()
    assert result is request.response


# --- selected_tags_companies sort + color + bulk selection (lines 2549,2552,2567-2568,2584) ---


def test_user_selected_tags_companies_sort_color(dbsession):
    user = _user(dbsession, "seltcosrtclr")
    tag = _tag(dbsession, user, "STCoSrtClrTag")
    co = _company(dbsession, user, "STCoSrtClrCo", color="red")
    tag.companies.append(co)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
            "color": "red",
        },
    )
    view = UserView(request)
    result = view.selected_tags_companies()
    assert "paginator" in result


def test_user_selected_tags_companies_bulk_select(dbsession):
    user = _user(dbsession, "seltcobulk")
    tag = _tag(dbsession, user, "STCoBulkTag")
    co = _company(dbsession, user, "STCoBulkCo")
    tag.companies.append(co)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(
        dbsession, user, method="POST", params={"_select_all": "1", "checked": "1"}
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = UserView(request)
    result = view.selected_tags_companies()
    assert result is request.response


# --- selected_tags_projects sort/filters/bulk (lines 2667-2717) ---


def test_user_selected_tags_projects_sort_fallback(dbsession):
    user = _user(dbsession, "seltpjinvsrt")
    tag = _tag(dbsession, user, "STPjInvSrtTag")
    proj = _project(dbsession, user, "STPjInvSrtP")
    tag.projects.append(proj)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = UserView(request)
    result = view.selected_tags_projects()
    assert "paginator" in result


def test_user_selected_tags_projects_all_filters(dbsession):
    import datetime

    user = _user(dbsession, "seltpjallfl")
    tag = _tag(dbsession, user, "STPjAllFlTag")
    proj = _project(
        dbsession,
        user,
        "STPjAllFlP",
        color="red",
        stage="design",
        delivery_method="general_contractor",
        deadline=datetime.datetime.now() + datetime.timedelta(days=10),
    )
    tag.projects.append(proj)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "status": "in_progress",
            "color": "red",
            "country": "PL",
            "subdivision": "PL-14",
            "stage": "design",
            "delivery_method": "general_contractor",
        },
    )
    view = UserView(request)
    result = view.selected_tags_projects()
    assert "paginator" in result


def test_user_selected_tags_projects_completed(dbsession):
    import datetime

    user = _user(dbsession, "seltpjcompl")
    tag = _tag(dbsession, user, "STPjComplTag")
    proj = _project(
        dbsession,
        user,
        "STPjComplP",
        deadline=datetime.datetime.now() - datetime.timedelta(days=10),
    )
    tag.projects.append(proj)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(dbsession, user, params={"status": "completed"})
    view = UserView(request)
    result = view.selected_tags_projects()
    assert "paginator" in result


def test_user_selected_tags_projects_bulk_select(dbsession):
    user = _user(dbsession, "seltpjbulk")
    tag = _tag(dbsession, user, "STPjBulkTag")
    proj = _project(dbsession, user, "STPjBulkP")
    tag.projects.append(proj)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(
        dbsession, user, method="POST", params={"_select_all": "1", "checked": "1"}
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = UserView(request)
    result = view.selected_tags_projects()
    assert result is request.response


# --- export_selected_tags sort (lines 2774,2777,2786) ---


def test_user_export_selected_tags_sort_fallback(dbsession):
    user = _user(dbsession, "expseltinvsrt")
    tag = _tag(dbsession, user, "ExpSelTInvSrtTag")
    user.selected_tags.append(tag)
    co = _company(dbsession, user, "ExpSelTInvSrtCo")
    tag.companies.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
            "category": "companies",
        },
    )
    view = UserView(request)
    result = view.export_selected_tags()
    assert result is not None


def test_user_export_selected_tags_asc(dbsession):
    user = _user(dbsession, "expseltasc")
    tag = _tag(dbsession, user, "ExpSelTAscTag")
    user.selected_tags.append(tag)
    co = _company(dbsession, user, "ExpSelTAscCo")
    tag.companies.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "name",
            "order": "asc",
            "category": "companies",
        },
    )
    view = UserView(request)
    result = view.export_selected_tags()
    assert result is not None


# --- _selected_related_contacts full filter/sort/bulk ---
# (lines 2823-3030 via selected_companies_contacts, selected_projects_contacts, selected_tags_contacts)


def test_user_selected_companies_contacts_sort_fallback(dbsession):
    user = _user(dbsession, "selcocontsrt")
    co = _company(dbsession, user, "SelCoContSrtCo")
    _contact(dbsession, user, "SelCoContSrtCont", company=co)
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = UserView(request)
    result = view.selected_companies_contacts()
    assert "paginator" in result


def test_user_selected_companies_contacts_filters(dbsession):
    user = _user(dbsession, "selcocontfl")
    co = _company(dbsession, user, "SelCoContFlCo", color="red")
    _contact(dbsession, user, "SelCoContFlCont", company=co, color="red")
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "name": "SelCoContFl",
            "role": "r",
            "phone": "123",
            "email": "c@e",
            "country": "PL",
            "subdivision": "PL-14",
            "color": "red",
        },
    )
    view = UserView(request)
    result = view.selected_companies_contacts()
    assert "paginator" in result


def test_user_selected_companies_contacts_projects_category(dbsession):
    """companies scope with category=projects should filter(false()) → empty."""
    user = _user(dbsession, "selcocontpcats")
    co = _company(dbsession, user, "SelCoContPCatCo")
    _contact(dbsession, user, "SelCoContPCatCont", company=co)
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(dbsession, user, params={"category": "projects"})
    view = UserView(request)
    result = view.selected_companies_contacts()
    assert "paginator" in result


def test_user_selected_projects_contacts_companies_category(dbsession):
    """projects scope with category=companies should filter(false()) → empty."""
    user = _user(dbsession, "selprojcontccat")
    proj = _project(dbsession, user, "SelProjContCCatP")
    _contact(dbsession, user, "SelProjContCCatCont", project=proj)
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(dbsession, user, params={"category": "companies"})
    view = UserView(request)
    result = view.selected_projects_contacts()
    assert "paginator" in result


def test_user_selected_tags_contacts_no_category(dbsession):
    """tags scope with no category (else branch) + country + subdivision."""
    user = _user(dbsession, "seltagcontncats")
    tag = _tag(dbsession, user, "SelTagContNCatTag")
    co = _company(dbsession, user, "SelTagContNCatCo")
    tag.companies.append(co)
    _contact(dbsession, user, "SelTagContNCatCont", company=co)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "country": "PL",
            "subdivision": "PL-14",
        },
    )
    view = UserView(request)
    result = view.selected_tags_contacts()
    assert "paginator" in result


def test_user_selected_companies_contacts_sort_city(dbsession):
    """Sort by city for companies scope."""
    user = _user(dbsession, "selcocontcity")
    co = _company(dbsession, user, "SelCoContCityCo")
    _contact(dbsession, user, "SelCoContCityCont", company=co)
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "city",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.selected_companies_contacts()
    assert "paginator" in result


def test_user_selected_projects_contacts_sort_city_paginator(dbsession):
    """Sort by city for projects scope."""
    user = _user(dbsession, "selpjcontcity")
    proj = _project(dbsession, user, "SelPjContCityP")
    _contact(dbsession, user, "SelPjContCityCont", project=proj)
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "city",
            "order": "desc",
        },
    )
    view = UserView(request)
    result = view.selected_projects_contacts()
    assert "paginator" in result


def test_user_selected_tags_contacts_sort_city_no_category(dbsession):
    """Sort by city for tags scope with no category (coalesce branch)."""
    user = _user(dbsession, "seltagcontcitync")
    tag = _tag(dbsession, user, "STContCityNCTag")
    co = _company(dbsession, user, "STContCityNCCo")
    tag.companies.append(co)
    _contact(dbsession, user, "STContCityNCCont", company=co)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "city",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.selected_tags_contacts()
    assert "paginator" in result


def test_user_selected_tags_contacts_sort_city_desc_no_category(dbsession):
    """Cover lines 2989-2990: tags scope city sort desc (coalesce else desc)."""
    user = _user(dbsession, "seltagcitydnc")
    tag = _tag(dbsession, user, "STCityDNCTag")
    co = _company(dbsession, user, "STCityDNCCo")
    tag.companies.append(co)
    _contact(dbsession, user, "STCityDNCCont", company=co)
    user.selected_tags.append(tag)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "city",
            "order": "desc",
        },
    )
    view = UserView(request)
    result = view.selected_tags_contacts()
    assert "paginator" in result


def test_user_selected_projects_contacts_sort_city_asc(dbsession):
    """Cover line 2974: _selected_related_contacts projects city asc."""
    user = _user(dbsession, "selpcityasc")
    proj = _project(dbsession, user, "SelPCityAscProj")
    from marker.models.contact import Contact

    c = Contact(name="SelPCityAscCont", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.project = proj
    dbsession.add(c)
    user.selected_projects.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "city",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.selected_projects_contacts()
    assert isinstance(result, dict)


def test_user_selected_companies_contacts_pagination(dbsession):
    """Cover line 3030: next_page when paginator length == per_page (20)."""
    user = _user(dbsession, "selpagination")
    co = _company(dbsession, user, "SelPaginCo")
    from marker.models.contact import Contact

    for i in range(21):
        c = Contact(
            name=f"PagCont{i}", role="r", phone=str(i), email=f"p{i}@e.com", color=""
        )
        c.created_by = user
        c.company = co
        dbsession.add(c)
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(dbsession, user)
    view = UserView(request)
    result = view.selected_companies_contacts()
    assert result["next_page"] is not None


def test_user_selected_companies_contacts_sort_category_name(dbsession):
    """Sort by category_name."""
    user = _user(dbsession, "selcocontcatnm")
    co = _company(dbsession, user, "SelCoContCatNmCo")
    _contact(dbsession, user, "SelCoContCatNmCont", company=co)
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "category_name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.selected_companies_contacts()
    assert "paginator" in result


def test_user_selected_companies_contacts_sort_category_name_desc(dbsession):
    user = _user(dbsession, "selcocontcatnmd")
    co = _company(dbsession, user, "SelCoContCatNmDCo")
    _contact(dbsession, user, "SelCoContCatNmDCont", company=co)
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "category_name",
            "order": "desc",
        },
    )
    view = UserView(request)
    result = view.selected_companies_contacts()
    assert "paginator" in result


def test_user_selected_companies_contacts_sort_generic_asc(dbsession):
    user = _user(dbsession, "selcocontgen")
    co = _company(dbsession, user, "SelCoContGenCo")
    _contact(dbsession, user, "SelCoContGenCont", company=co)
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.selected_companies_contacts()
    assert "paginator" in result


def test_user_selected_companies_contacts_bulk_select(dbsession):
    user = _user(dbsession, "selcocontbulk")
    co = _company(dbsession, user, "SelCoContBulkCo")
    _contact(dbsession, user, "SelCoContBulkCont", company=co)
    user.selected_companies.append(co)
    transaction.commit()
    request = _req(
        dbsession, user, method="POST", params={"_select_all": "1", "checked": "1"}
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = UserView(request)
    result = view.selected_companies_contacts()
    assert result is request.response


# --- selected_contacts filters/sort/bulk (lines 3150-3264) ---


def test_user_selected_contacts_sort_fallback(dbsession):
    user = _user(dbsession, "selcontsinvsrt")
    co = _company(dbsession, user, "SelContSInvSrtCo")
    c1 = _contact(dbsession, user, "SelContSInvSrt", company=co)
    user.selected_contacts.append(c1)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = UserView(request)
    result = view.selected_contacts()
    assert "paginator" in result


def test_user_selected_contacts_text_filters(dbsession):
    user = _user(dbsession, "selcontstxtfl")
    co = _company(dbsession, user, "SelContsTxtFlCo")
    c1 = _contact(dbsession, user, "SelContsTxtFl", company=co)
    user.selected_contacts.append(c1)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "name": "SelConts",
            "role": "r",
            "phone": "123",
            "email": "c@e",
        },
    )
    view = UserView(request)
    result = view.selected_contacts()
    assert "paginator" in result


def test_user_selected_contacts_projects_country_subdivision(dbsession):
    user = _user(dbsession, "selcontsprjgeo")
    proj = _project(dbsession, user, "SelContsPjGeoP")
    c1 = _contact(dbsession, user, "SelContsPjGeoCont", project=proj)
    user.selected_contacts.append(c1)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "projects",
            "country": "PL",
            "subdivision": "PL-14",
        },
    )
    view = UserView(request)
    result = view.selected_contacts()
    assert "paginator" in result


def test_user_selected_contacts_no_category_country_subdivision(dbsession):
    user = _user(dbsession, "selcontsncgeo")
    co = _company(dbsession, user, "SelContsNCGeoCo")
    c1 = _contact(dbsession, user, "SelContsNCGeoCont", company=co)
    user.selected_contacts.append(c1)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "country": "PL",
            "subdivision": "PL-14",
        },
    )
    view = UserView(request)
    result = view.selected_contacts()
    assert "paginator" in result


def test_user_selected_contacts_sort_city_projects(dbsession):
    user = _user(dbsession, "selcontscitypj")
    proj = _project(dbsession, user, "SelContsCityPjP")
    c1 = _contact(dbsession, user, "SelContsCityPjCont", project=proj)
    user.selected_contacts.append(c1)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "projects",
            "sort": "city",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.selected_contacts()
    assert "paginator" in result


def test_user_selected_contacts_sort_city_companies(dbsession):
    user = _user(dbsession, "selcontscityco")
    co = _company(dbsession, user, "SelContsCityCoCo")
    c1 = _contact(dbsession, user, "SelContsCityCoCont", company=co)
    user.selected_contacts.append(c1)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "companies",
            "sort": "city",
            "order": "desc",
        },
    )
    view = UserView(request)
    result = view.selected_contacts()
    assert "paginator" in result


def test_user_selected_contacts_bulk_select(dbsession):
    user = _user(dbsession, "selcontsbulk")
    co = _company(dbsession, user, "SelContsBulkCo")
    c1 = _contact(dbsession, user, "SelContsBulkCont", company=co)
    user.selected_contacts.append(c1)
    transaction.commit()
    request = _req(
        dbsession, user, method="POST", params={"_select_all": "1", "checked": "1"}
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = UserView(request)
    result = view.selected_contacts()
    assert result is request.response


# --- export_selected_contacts full filter/sort (lines 3334-3400) ---


def test_user_export_selected_contacts_sort_fallback(dbsession):
    user = _user(dbsession, "expselcontinvsrt")
    co = _company(dbsession, user, "ExpSelContInvCo")
    c1 = _contact(dbsession, user, "ExpSelContInvCont", company=co)
    user.selected_contacts.append(c1)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


def test_user_export_selected_contacts_text_filters(dbsession):
    user = _user(dbsession, "expselconttxtfl")
    co = _company(dbsession, user, "ExpSelContTxtCo")
    c1 = _contact(dbsession, user, "ExpSelContTxtCont", company=co)
    user.selected_contacts.append(c1)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "name": "ExpSelCont",
            "role": "r",
            "phone": "123",
            "email": "c@e",
            "category": "companies",
            "country": "PL",
            "color": "red",
        },
    )
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


def test_user_export_selected_contacts_projects_country(dbsession):
    user = _user(dbsession, "expselcontpjcntry")
    proj = _project(dbsession, user, "ExpSelContPjCntryP")
    c1 = _contact(dbsession, user, "ExpSelContPjCntryCont", project=proj)
    user.selected_contacts.append(c1)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "projects",
            "country": "PL",
        },
    )
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


def test_user_export_selected_contacts_sort_city(dbsession):
    user = _user(dbsession, "expselcontcity")
    proj = _project(dbsession, user, "ExpSelContCityP")
    c1 = _contact(dbsession, user, "ExpSelContCityCont", project=proj)
    user.selected_contacts.append(c1)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "projects",
            "sort": "city",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


def test_user_export_selected_contacts_sort_city_desc(dbsession):
    user = _user(dbsession, "expselcontcityd")
    co = _company(dbsession, user, "ExpSelContCityDCo")
    c1 = _contact(dbsession, user, "ExpSelContCityDCont", company=co)
    user.selected_contacts.append(c1)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "category": "companies",
            "sort": "city",
            "order": "desc",
        },
    )
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


def test_user_export_selected_contacts_sort_category_name(dbsession):
    user = _user(dbsession, "expselcontcatnm")
    co = _company(dbsession, user, "ExpSelContCatNmCo")
    c1 = _contact(dbsession, user, "ExpSelContCatNmCont", company=co)
    user.selected_contacts.append(c1)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "category_name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


def test_user_export_selected_contacts_sort_category_name_desc(dbsession):
    user = _user(dbsession, "expselcontcatnmd")
    co = _company(dbsession, user, "ExpSelContCatNmDCo")
    c1 = _contact(dbsession, user, "ExpSelContCatNmDCont", company=co)
    user.selected_contacts.append(c1)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "category_name",
            "order": "desc",
        },
    )
    view = UserView(request)
    result = view.export_selected_contacts()
    assert result is not None


# --- companies_stars bulk selection (line 3731) ---


def test_user_companies_stars_bulk_select(dbsession):
    user = _user(dbsession, "costarbulk")
    co = _company(dbsession, user, "CoStarBulkCo")
    user.companies_stars.append(co)
    transaction.commit()
    request = _req(
        dbsession, user, method="POST", params={"_select_all": "1", "checked": "1"}
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = UserView(request)
    result = view.companies_stars()
    assert result is request.response


# --- export_companies_stars sort/color (lines 3793-3816) ---


def test_user_export_companies_stars_sort_fallback(dbsession):
    user = _user(dbsession, "expcostarinvs")
    co = _company(dbsession, user, "ExpCoStarInvsCo")
    user.companies_stars.append(co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = UserView(request)
    result = view.export_companies_stars()
    assert result is not None


def test_user_export_companies_stars_color_sort(dbsession):
    user = _user(dbsession, "expcostarclrs")
    co = _company(dbsession, user, "ExpCoStarClrsCo", color="red")
    user.companies_stars.append(co)
    _contact(dbsession, user, "ExpCoStarClrsCont", company=co)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "color": "red",
            "sort": "name",
            "order": "desc",
        },
    )
    view = UserView(request)
    result = view.export_companies_stars()
    assert result is not None


# --- projects_stars sort/order fallback + bulk selection (lines 3926,3929,3965) ---


def test_user_projects_stars_sort_fallback(dbsession):
    user = _user(dbsession, "pstarinvsrt")
    _project(dbsession, user, "PStarInvSrtP")
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = UserView(request)
    result = view.projects_stars()
    assert "paginator" in result


def test_user_projects_stars_bulk_select(dbsession):
    user = _user(dbsession, "pstarbulk")
    proj = _project(dbsession, user, "PStarBulkP")
    user.projects_stars.append(proj)
    transaction.commit()
    request = _req(
        dbsession, user, method="POST", params={"_select_all": "1", "checked": "1"}
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = UserView(request)
    result = view.projects_stars()
    assert result is request.response


# --- export_projects_stars sort/filters (lines 4029-4057) ---


def test_user_export_projects_stars_sort_fallback(dbsession):
    user = _user(dbsession, "exppstarinvs")
    proj = _project(dbsession, user, "ExpPStarInvsP")
    user.projects_stars.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = UserView(request)
    result = view.export_projects_stars()
    assert result is not None


def test_user_export_projects_stars_filters(dbsession):
    import datetime

    user = _user(dbsession, "exppstarfl")
    proj = _project(
        dbsession,
        user,
        "ExpPStarFlP",
        color="red",
        deadline=datetime.datetime.now() + datetime.timedelta(days=10),
    )
    user.projects_stars.append(proj)
    _contact(dbsession, user, "ExpPStarFlCont", project=proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "status": "in_progress",
            "color": "red",
            "sort": "name",
            "order": "desc",
        },
    )
    view = UserView(request)
    result = view.export_projects_stars()
    assert result is not None


def test_user_export_projects_stars_completed(dbsession):
    import datetime

    user = _user(dbsession, "exppstarcompl")
    proj = _project(
        dbsession,
        user,
        "ExpPStarComplP",
        deadline=datetime.datetime.now() - datetime.timedelta(days=10),
    )
    user.projects_stars.append(proj)
    transaction.commit()
    request = _req(
        dbsession,
        user,
        params={
            "status": "completed",
            "sort": "name",
            "order": "asc",
        },
    )
    view = UserView(request)
    result = view.export_projects_stars()
    assert result is not None
