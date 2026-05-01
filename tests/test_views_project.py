"""Tests for marker/views/project.py"""

import datetime
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
from marker.views.project import ProjectView
from tests.conftest import DummyRequestWithIdentity


@pytest.fixture(autouse=True)
def patch_translationstring_str(monkeypatch):
    monkeypatch.setattr(
        marker.forms.ts.TranslationString, "__str__", lambda self: self.msg
    )
    yield


def _make_user(dbsession, name="projuser"):
    user = User(
        name=name, fullname="P U", email=f"{name}@e.com", role="admin", password="pw"
    )
    dbsession.add(user)
    dbsession.flush()
    return user


def _make_project(dbsession, user, name="TestProj"):
    project = Project(
        name=name,
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="http://example.com",
        color="green",
        deadline=None,
        stage="",
        delivery_method="",
    )
    project.created_by = user
    dbsession.add(project)
    dbsession.flush()
    return project


def _make_company(dbsession, user, name="ProjTestCo"):
    company = Company(
        name=name,
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="",
        color="red",
        NIP="",
        REGON="",
        KRS="",
    )
    company.created_by = user
    dbsession.add(company)
    dbsession.flush()
    return company


def _make_request(dbsession, user, project=None, method="GET", params=None, post=None):
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = method
    request.GET = MultiDict(params or {})
    request.POST = MultiDict(post or {})
    request.params = MultiDict(params or {})
    request.locale_name = "en"
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/project"
    request.session = MagicMock()
    request.response = MagicMock()
    request.response.headers = {}
    request.context = MagicMock()
    if project:
        request.context.project = project
    request.matchdict = {}
    request.matched_route = MagicMock()
    request.matched_route.name = "project_view"
    request.environ = {}
    request.environ["webob._parsed_get_vars"] = (MultiDict(params or {}), MultiDict())
    request.environ["webob._parsed_post_vars"] = (MultiDict(post or {}), MultiDict())
    request.environ["webob._parsed_params_vars"] = (
        MultiDict(params or {}),
        MultiDict(),
    )
    request.path_qs = "/project"
    request.query_string = ""
    return request


# --- all() ---


def test_project_all_default(dbsession):
    user = _make_user(dbsession)
    _make_project(dbsession, user)
    transaction.commit()
    request = _make_request(dbsession, user)
    view = ProjectView(request)
    result = view.all()
    assert "paginator" in result
    assert "counter" in result
    assert result["view_mode"] == "projects"


def test_project_all_with_filters(dbsession):
    user = _make_user(dbsession, "projfluser")
    _make_project(dbsession, user, "FilterProj")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "name": "Filter",
            "city": "C",
            "street": "S",
            "postcode": "00-000",
            "country": "PL",
            "subdivision": "PL-14",
            "website": "example",
            "color": "green",
            "sort": "name",
            "order": "asc",
        },
    )
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["name"] == "Filter"


def test_project_all_filter_stage(dbsession):
    user = _make_user(dbsession, "projstageuser")
    transaction.commit()
    request = _make_request(dbsession, user, params={"stage": "started"})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["stage"] == "started"


def test_project_all_filter_delivery_method_design_build(dbsession):
    user = _make_user(dbsession, "projdmuser")
    transaction.commit()
    request = _make_request(dbsession, user, params={"delivery_method": "design_build"})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["delivery_method"] == "design_build"


def test_project_all_filter_status_in_progress(dbsession):
    user = _make_user(dbsession, "projstatuser")
    transaction.commit()
    request = _make_request(dbsession, user, params={"status": "in_progress"})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["status"] == "in_progress"


def test_project_all_filter_status_completed(dbsession):
    user = _make_user(dbsession, "projcompuser2")
    transaction.commit()
    request = _make_request(dbsession, user, params={"status": "completed"})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["status"] == "completed"


def test_project_all_sort_stars_desc(dbsession):
    user = _make_user(dbsession, "projstaruser")
    project = _make_project(dbsession, user, "StarProj")
    user.projects_stars.append(project)
    transaction.commit()
    request = _make_request(dbsession, user, params={"sort": "stars", "order": "desc"})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["sort"] == "stars"


def test_project_all_sort_comments_basic(dbsession):
    user = _make_user(dbsession, "projcmtalluser")
    project = _make_project(dbsession, user, "CmtAllProj")
    comment = Comment(comment="test")
    comment.created_by = user
    project.comments.append(comment)
    transaction.commit()
    request = _make_request(
        dbsession, user, params={"sort": "comments", "order": "asc"}
    )
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["sort"] == "comments"


def test_project_all_with_tags(dbsession):
    user = _make_user(dbsession, "projtaguser")
    project = _make_project(dbsession, user, "TaggedProj")
    tag = Tag(name="ProjTag1")
    tag.created_by = user
    project.tags.append(tag)
    transaction.commit()
    request = _make_request(dbsession, user, params={"tag": "ProjTag1"})
    view = ProjectView(request)
    result = view.all()
    assert "tag" in result["q"]


def test_project_all_contacts_view_mode_minimal(dbsession):
    user = _make_user(dbsession, "projcontactviewuser")
    project = _make_project(dbsession, user, "ContactViewProj")
    tag = Tag(name="ProjContactTag")
    tag.created_by = user
    project.tags.append(tag)
    contact = Contact(name="ProjContact", role="", phone="", email="", color="")
    contact.created_by = user
    project.contacts.append(contact)
    transaction.commit()
    request = _make_request(
        dbsession, user, params={"tag": "ProjContactTag", "view": "contacts"}
    )
    view = ProjectView(request)
    result = view.all()
    assert result["view_mode"] == "contacts"


# --- comments() ---


def test_project_comments(dbsession):
    user = _make_user(dbsession, "projcmtuser")
    project = _make_project(dbsession, user, "CmtProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project)
    view = ProjectView(request)
    result = view.comments()
    assert "paginator" in result
    assert "project" in result


# --- map() ---


def test_project_map(dbsession):
    user = _make_user(dbsession, "projmapuser")
    project = _make_project(dbsession, user, "MapProj")
    tag = Tag(name="MapProjTag")
    tag.created_by = user
    project.tags.append(tag)
    transaction.commit()
    request = _make_request(dbsession, user, project=project)
    view = ProjectView(request)
    result = view.map()
    assert "url" in result


# --- project_json() ---


def test_project_json(dbsession):
    user = _make_user(dbsession, "projjsonuser")
    project = _make_project(dbsession, user, "JsonProj")
    tag = Tag(name="JsonProjTag")
    tag.created_by = user
    project.tags.append(tag)
    transaction.commit()
    request = _make_request(dbsession, user, project=project)
    view = ProjectView(request)
    result = view.project_json()
    assert isinstance(result, list)


# --- count_* ---


def test_project_count_companies_basic(dbsession):
    user = _make_user(dbsession, "projcntcouser")
    project = _make_project(dbsession, user, "CntCoProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project)
    view = ProjectView(request)
    result = view.count_companies()
    assert isinstance(result, int)


def test_project_count_tags(dbsession):
    user = _make_user(dbsession, "projcnttaguser")
    project = _make_project(dbsession, user, "CntTagProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project)
    result = ProjectView(request).count_tags()
    assert isinstance(result, int)


def test_project_count_contacts(dbsession):
    user = _make_user(dbsession, "projcntcontuser")
    project = _make_project(dbsession, user, "CntContProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project)
    result = ProjectView(request).count_contacts()
    assert isinstance(result, int)


def test_project_count_comments(dbsession):
    user = _make_user(dbsession, "projcntcmtuser")
    project = _make_project(dbsession, user, "CntCmtProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project)
    result = ProjectView(request).count_comments()
    assert isinstance(result, int)


def test_project_count_stars(dbsession):
    user = _make_user(dbsession, "projcntstaruser")
    project = _make_project(dbsession, user, "CntStarProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project)
    result = ProjectView(request).count_stars()
    assert isinstance(result, int)


def test_project_count_similar(dbsession):
    user = _make_user(dbsession, "projcntsimuser")
    project = _make_project(dbsession, user, "CntSimProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project)
    result = ProjectView(request).count_similar()
    assert isinstance(result, int)


# --- view() ---


def test_project_view(dbsession):
    user = _make_user(dbsession, "projviewuser")
    project = _make_project(dbsession, user, "ViewProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project)
    view = ProjectView(request)
    result = view.view()
    assert "project" in result
    assert "project_pills" in result


# --- similar() ---


def test_project_similar(dbsession):
    user = _make_user(dbsession, "projsimuser")
    project = _make_project(dbsession, user, "SimProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project)
    view = ProjectView(request)
    result = view.similar()
    assert "paginator" in result


# --- add() ---


@patch("marker.views.project.location", return_value=None)
def test_project_add_get(mock_loc, dbsession):
    user = _make_user(dbsession, "projaddgetuser")
    transaction.commit()
    request = _make_request(dbsession, user, method="GET", post={})
    view = ProjectView(request)
    result = view.add()
    assert "form" in result


@patch("marker.views.project.location", return_value={"lat": 52.0, "lon": 21.0})
def test_project_add_post(mock_loc, dbsession):
    user = _make_user(dbsession, "projaddpostuser")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        method="POST",
        post={
            "name": "NewProjectABC",
            "street": "Street",
            "postcode": "",
            "city": "City",
            "subdivision": "",
            "country": "",
            "website": "",
            "color": "",
            "deadline": "",
            "stage": "",
            "delivery_method": "",
        },
    )
    view = ProjectView(request)
    result = view.add()
    assert isinstance(result, HTTPSeeOther)


# --- edit() ---


@patch("marker.views.project.location", return_value=None)
def test_project_edit_get(mock_loc, dbsession):
    user = _make_user(dbsession, "projeditgetuser")
    project = _make_project(dbsession, user, "EditGetProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project, method="GET", post={})
    view = ProjectView(request)
    result = view.edit()
    assert "form" in result


@patch("marker.views.project.location", return_value=None)
def test_project_edit_post(mock_loc, dbsession):
    user = _make_user(dbsession, "projeditpostuser")
    project = _make_project(dbsession, user, "EditPostProj")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        method="POST",
        post={
            "name": "EditPostProj",
            "street": "New Street",
            "postcode": "",
            "city": "NewCity",
            "subdivision": "",
            "country": "",
            "website": "",
            "color": "",
            "deadline": "",
            "stage": "",
            "delivery_method": "",
        },
    )
    view = ProjectView(request)
    result = view.edit()
    assert isinstance(result, HTTPSeeOther)


# --- delete() ---


def test_project_delete(dbsession):
    user = _make_user(dbsession, "projdeluser")
    project = _make_project(dbsession, user, "DelProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project, method="POST")
    view = ProjectView(request)
    result = view.delete()
    assert result.status_code == 303


# --- del_row() ---


def test_project_del_row(dbsession):
    user = _make_user(dbsession, "projdelrowuser")
    project = _make_project(dbsession, user, "DelRowProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project, method="POST")
    view = ProjectView(request)
    result = view.del_row()
    assert result == ""


# --- search() ---


def test_project_search_get(dbsession):
    user = _make_user(dbsession, "projsearchgetuser")
    transaction.commit()
    request = _make_request(dbsession, user, method="GET", post={})
    view = ProjectView(request)
    result = view.search()
    assert "form" in result


def test_project_search_post_basic(dbsession):
    user = _make_user(dbsession, "projsearchpostuser")
    transaction.commit()
    post_data = {
        "name": "SearchProj",
        "subdivision": "",
        "country": "",
        "stage": "",
        "delivery_method": "",
        "color": "",
    }
    request = _make_request(dbsession, user, method="POST", post=post_data)
    # Search form reads from request.POST
    view = ProjectView(request)
    result = view.search()
    assert isinstance(result, HTTPSeeOther)


# --- star() ---


def test_project_star(dbsession):
    user = _make_user(dbsession, "projstaruser2")
    project = _make_project(dbsession, user, "StarProj2")
    transaction.commit()
    request = _make_request(dbsession, user, project=project, method="POST")
    view = ProjectView(request)
    result = view.star()
    assert "bi-star" in result


# --- projects_stars() ---


def test_projects_stars(dbsession):
    user = _make_user(dbsession, "projstarsuser")
    project = _make_project(dbsession, user, "StarsProj")
    user.projects_stars.append(project)
    transaction.commit()
    request = _make_request(dbsession, user, project=project)
    view = ProjectView(request)
    result = view.projects_stars()
    assert "paginator" in result


# --- check() ---


def test_project_check(dbsession):
    user = _make_user(dbsession, "projcheckuser")
    project = _make_project(dbsession, user, "CheckProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project, method="POST")
    view = ProjectView(request)
    result = view.check()
    assert "checked" in result


# --- select() ---


def test_project_select(dbsession):
    user = _make_user(dbsession, "projselectuser")
    _make_project(dbsession, user, "SelectProj")
    transaction.commit()
    request = _make_request(dbsession, user, params={"name": "Select"})
    view = ProjectView(request)
    result = view.select()
    assert "projects" in result


# --- add_company() ---


def test_project_add_company_get(dbsession):
    user = _make_user(dbsession, "projaddcoget")
    project = _make_project(dbsession, user, "AddCoGetProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project, method="GET", post={})
    view = ProjectView(request)
    result = view.add_company()
    assert "form" in result


# --- add_tag() ---


def test_project_add_tag_get(dbsession):
    user = _make_user(dbsession, "projaddtagget")
    project = _make_project(dbsession, user, "AddTagGetProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project, method="GET", post={})
    view = ProjectView(request)
    result = view.add_tag()
    assert "form" in result


# --- add_contact() ---


def test_project_add_contact_get(dbsession):
    user = _make_user(dbsession, "projaddcontget")
    project = _make_project(dbsession, user, "AddContGetProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project, method="GET", post={})
    view = ProjectView(request)
    result = view.add_contact()
    assert "form" in result


# --- project_add_comment() ---


def test_project_add_comment_get(dbsession):
    user = _make_user(dbsession, "projaddcmtget")
    project = _make_project(dbsession, user, "AddCmtGetProj")
    transaction.commit()
    request = _make_request(dbsession, user, project=project, method="GET", post={})
    view = ProjectView(request)
    result = view.project_add_comment()
    assert "form" in result


# --- project_activity_edit() ---


def test_project_activity_edit_get(dbsession):
    user = _make_user(dbsession, "projacteditget")
    project = _make_project(dbsession, user, "ActEditGetProj")
    from marker.models.association import Activity

    company = _make_company(dbsession, user, "ActEditCo")
    activity = Activity(role="investor", stage="started")
    activity.company = company
    activity.project = project
    dbsession.add(activity)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        method="GET",
        post={},
    )
    request.matchdict = {"company_id": str(company.id), "project_id": str(project.id)}
    view = ProjectView(request)
    result = view.project_activity_edit()
    assert "form" in result


# --- unlink_tag() ---


def test_project_unlink_tag(dbsession):
    user = _make_user(dbsession, "projunlinktaguser")
    project = _make_project(dbsession, user, "UnlinkTagProj")
    tag = Tag(name="UnlinkTag")
    tag.created_by = user
    project.tags.append(tag)
    dbsession.flush()
    proj_id = project.id
    tag_id = tag.id
    transaction.commit()
    request = _make_request(dbsession, user, project=project, method="POST")
    request.matchdict = {"project_id": str(proj_id), "tag_id": str(tag_id)}
    view = ProjectView(request)
    result = view.unlink_tag()
    assert result == ""


# ===========================================================================
# Extended coverage tests
# ===========================================================================

# --- all() edge cases ---


def test_project_all_invalid_view_param(dbsession):
    """Line 189: invalid view param falls back to 'projects'."""
    user = _make_user(dbsession, "projinvview")
    transaction.commit()
    request = _make_request(dbsession, user, params={"view": "invalid"})
    view = ProjectView(request)
    result = view.all()
    assert result["view_mode"] == "projects"


def test_project_all_invalid_order(dbsession):
    """Line 290: invalid order falls back to default."""
    user = _make_user(dbsession, "projinvorder")
    transaction.commit()
    request = _make_request(dbsession, user, params={"order": "xyz"})
    view = ProjectView(request)
    result = view.all()
    assert "paginator" in result


def test_project_all_sort_updated_at_asc(dbsession):
    """Else branch with valid sort 'updated_at' and order 'asc'."""
    user = _make_user(dbsession, "projinvsort")
    _make_project(dbsession, user, "UpdAtProj")
    transaction.commit()
    request = _make_request(
        dbsession, user, params={"sort": "updated_at", "order": "asc"}
    )
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["sort"] == "updated_at"


def test_project_all_default_sort_desc(dbsession):
    """Line 333: else branch for desc with default sort."""
    user = _make_user(dbsession, "projdescsort")
    _make_project(dbsession, user, "DescSortProj")
    transaction.commit()
    request = _make_request(dbsession, user, params={"sort": "name", "order": "desc"})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["order"] == "desc"


def test_project_all_stars_asc(dbsession):
    """Stars sort ascending branch."""
    user = _make_user(dbsession, "projstarsasc")
    project = _make_project(dbsession, user, "StarsAscProj")
    user.projects_stars.append(project)
    transaction.commit()
    request = _make_request(dbsession, user, params={"sort": "stars", "order": "asc"})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["sort"] == "stars"
    assert result["q"]["order"] == "asc"


def test_project_all_comments_desc(dbsession):
    """Comments sort descending branch."""
    user = _make_user(dbsession, "projcmtsdesc")
    project = _make_project(dbsession, user, "CmtsDescProj")
    comment = Comment(comment="c")
    comment.created_by = user
    project.comments.append(comment)
    transaction.commit()
    request = _make_request(
        dbsession, user, params={"sort": "comments", "order": "desc"}
    )
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["sort"] == "comments"


def test_project_all_deadline_filter(dbsession):
    """Deadline filter branch."""
    user = _make_user(dbsession, "projdlfilter")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={"deadline": "2030-01-01 00:00:00"},
    )
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["deadline"] == "2030-01-01 00:00:00"


# --- map() edge cases ---


def test_project_map_with_filters(dbsession):
    """Test map() with all filter params."""
    user = _make_user(dbsession, "projmapfilt")
    _make_project(dbsession, user, "MapFiltProj")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "name": "Map",
            "street": "S",
            "postcode": "00",
            "city": "C",
            "subdivision": "PL-14",
            "country": "PL",
            "website": "example",
            "color": "green",
            "stage": "",
            "delivery_method": "",
            "sort": "name",
            "order": "asc",
        },
    )
    view = ProjectView(request)
    result = view.map()
    assert "url" in result


def test_project_map_status_completed(dbsession):
    """Lines 467-471: status=completed filter in map."""
    user = _make_user(dbsession, "projmapstcomp")
    project = _make_project(dbsession, user, "MapCompProj")
    project.deadline = datetime.datetime.now() - datetime.timedelta(days=1)
    transaction.commit()
    request = _make_request(dbsession, user, params={"status": "completed"})
    view = ProjectView(request)
    result = view.map()
    assert result["q"]["status"] == "completed"


def test_project_map_sort_stars(dbsession):
    """Lines 525-532: stars sorting in map."""
    user = _make_user(dbsession, "projmapstar")
    project = _make_project(dbsession, user, "MapStarProj")
    user.projects_stars.append(project)
    transaction.commit()
    request = _make_request(dbsession, user, params={"sort": "stars", "order": "desc"})
    view = ProjectView(request)
    result = view.map()
    assert result["q"]["sort"] == "stars"


def test_project_map_sort_stars_asc(dbsession):
    user = _make_user(dbsession, "projmapstarasc")
    project = _make_project(dbsession, user, "MapStarAscProj")
    user.projects_stars.append(project)
    transaction.commit()
    request = _make_request(dbsession, user, params={"sort": "stars", "order": "asc"})
    view = ProjectView(request)
    result = view.map()
    assert result["q"]["order"] == "asc"


def test_project_map_sort_default_asc(dbsession):
    user = _make_user(dbsession, "projmapdefasc")
    _make_project(dbsession, user, "MapDefAscP")
    transaction.commit()
    request = _make_request(dbsession, user, params={"sort": "name", "order": "asc"})
    view = ProjectView(request)
    result = view.map()
    assert result["q"]["order"] == "asc"


def test_project_map_sort_default_desc(dbsession):
    user = _make_user(dbsession, "projmapdefdesc")
    _make_project(dbsession, user, "MapDefDescP")
    transaction.commit()
    request = _make_request(dbsession, user, params={"sort": "name", "order": "desc"})
    view = ProjectView(request)
    result = view.map()
    assert result["q"]["order"] == "desc"


def test_project_map_deadline(dbsession):
    user = _make_user(dbsession, "projmapdl")
    _make_project(dbsession, user, "MapDlProj")
    transaction.commit()
    request = _make_request(dbsession, user, params={"deadline": "2030-01-01 00:00:00"})
    view = ProjectView(request)
    result = view.map()
    assert "url" in result


# --- project_json() filter branches ---


def test_project_json_filters(dbsession):
    """Lines 573-607: all individual filter branches."""
    user = _make_user(dbsession, "projjsonfilt")
    _make_project(dbsession, user, "JsonFiltProj")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "name": "Json",
            "street": "S",
            "postcode": "00",
            "city": "C",
            "website": "example",
            "subdivision": "PL-14",
            "country": "PL",
            "color": "green",
            "stage": "",
            "delivery_method": "",
        },
    )
    view = ProjectView(request)
    result = view.project_json()
    assert isinstance(result, list)


def test_project_json_deadline_fixed(dbsession):
    user = _make_user(dbsession, "projjsondl")
    project = _make_project(dbsession, user, "JsonDlProj")
    project.deadline = datetime.datetime(2030, 1, 1)
    transaction.commit()
    request = _make_request(dbsession, user, params={"deadline": "2031-01-01 00:00:00"})
    view = ProjectView(request)
    result = view.project_json()
    assert isinstance(result, list)


# --- view() route branches ---


def test_project_view_companies_route(dbsession):
    """Lines 745-750: project_companies route with sorting."""
    user = _make_user(dbsession, "projviewco")
    project = _make_project(dbsession, user, "ViewCoProj")
    company = _make_company(dbsession, user, "ViewTestCo")
    activity = Activity(role="investor", stage="")
    activity.company = company
    activity.project = project
    dbsession.add(activity)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        params={"sort": "name", "order": "asc"},
    )
    request.matched_route.name = "project_companies"
    view = ProjectView(request)
    result = view.view()
    assert "companies_assoc" in result
    assert len(result["companies_assoc"]) == 1


def test_project_view_companies_invalid_sort(dbsession):
    """Lines 745-746: invalid sort defaults to 'name'."""
    user = _make_user(dbsession, "projviewcoinvsort")
    project = _make_project(dbsession, user, "ViewCoInvSortP")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        params={"sort": "invalid", "order": "invalid"},
    )
    request.matched_route.name = "project_companies"
    view = ProjectView(request)
    result = view.view()
    assert result["q"]["sort"] == "name"
    assert result["q"]["order"] == "asc"


def test_project_view_companies_desc_order(dbsession):
    user = _make_user(dbsession, "projviewcodesc")
    project = _make_project(dbsession, user, "ViewCoDescP")
    company = _make_company(dbsession, user, "ViewDescCo")
    activity = Activity(role="investor", stage="")
    activity.company = company
    activity.project = project
    dbsession.add(activity)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        params={"sort": "name", "order": "desc"},
    )
    request.matched_route.name = "project_companies"
    view = ProjectView(request)
    result = view.view()
    assert "companies_assoc" in result


def test_project_view_companies_filter_stage_and_role(dbsession):
    user = _make_user(dbsession, "projfltsr")
    project = _make_project(dbsession, user, "FltSRProj")
    company = _make_company(dbsession, user, "FltSRCo")
    activity = Activity(role="investor", stage="announcement")
    activity.company = company
    activity.project = project
    dbsession.add(activity)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        params={
            "sort": "name",
            "order": "asc",
            "stage": "announcement",
            "role": "investor",
        },
    )
    request.matched_route.name = "project_companies"
    view = ProjectView(request)
    result = view.view()
    assert len(result["companies_assoc"]) == 1
    assert result["q"]["stage"] == "announcement"
    assert result["q"]["role"] == "investor"


def test_project_view_contacts_route(dbsession):
    """Line 763+: project_contacts route."""
    user = _make_user(dbsession, "projviewcont")
    project = _make_project(dbsession, user, "ViewContProj")
    contact = Contact(name="ViewContact", role="", phone="", email="", color="")
    contact.created_by = user
    project.contacts.append(contact)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        params={"sort": "name", "order": "asc"},
    )
    request.matched_route.name = "project_contacts"
    view = ProjectView(request)
    result = view.view()
    assert "contacts" in result
    assert len(result["contacts"]) == 1


def test_project_view_contacts_invalid_sort(dbsession):
    """Lines 771-789: invalid sort/order for contacts."""
    user = _make_user(dbsession, "projviewcontinvsort")
    project = _make_project(dbsession, user, "ViewContInvSortP")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        params={"sort": "invalid", "order": "invalid"},
    )
    request.matched_route.name = "project_contacts"
    view = ProjectView(request)
    result = view.view()
    assert result["q"]["sort"] == "created_at"
    assert result["q"]["order"] == "desc"


def test_project_view_tags_route(dbsession):
    """Lines 791-813: project_tags route."""
    user = _make_user(dbsession, "projviewtag")
    project = _make_project(dbsession, user, "ViewTagProj")
    tag = Tag(name="ViewTestTag")
    tag.created_by = user
    project.tags.append(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        params={"sort": "name", "order": "desc"},
    )
    request.matched_route.name = "project_tags"
    view = ProjectView(request)
    result = view.view()
    assert "tags" in result
    assert len(result["tags"]) == 1


def test_project_view_tags_invalid_sort(dbsession):
    """Lines 791+: invalid sort/order for tags defaults."""
    user = _make_user(dbsession, "projviewtaginvsort")
    project = _make_project(dbsession, user, "ViewTagInvSortP")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        params={"sort": "invalid", "order": "invalid"},
    )
    request.matched_route.name = "project_tags"
    view = ProjectView(request)
    result = view.view()
    assert result["q"]["sort"] == "created_at"
    assert result["q"]["order"] == "asc"


# --- similar() edge cases ---


def test_project_similar_status_completed_basic(dbsession):
    """Lines 879, 882: status=completed filter."""
    user = _make_user(dbsession, "projsimcomp")
    project = _make_project(dbsession, user, "SimCompProj")
    tag = Tag(name="SimCompTag")
    tag.created_by = user
    project.tags.append(tag)
    p2 = _make_project(dbsession, user, "SimCompProj2")
    p2.deadline = datetime.datetime.now() - datetime.timedelta(days=1)
    p2.tags.append(tag)
    transaction.commit()
    request = _make_request(
        dbsession, user, project=project, params={"status": "completed"}
    )
    view = ProjectView(request)
    result = view.similar()
    assert result["q"]["status"] == "completed"


def test_project_similar_sort_shared_tags_asc(dbsession):
    """Lines 907-908: shared_tags sort ascending."""
    user = _make_user(dbsession, "projsimstasc")
    project = _make_project(dbsession, user, "SimSTAscProj")
    tag = Tag(name="SimSTAscTag")
    tag.created_by = user
    project.tags.append(tag)
    p2 = _make_project(dbsession, user, "SimSTAscProj2")
    p2.tags.append(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        params={"sort": "shared_tags", "order": "asc"},
    )
    view = ProjectView(request)
    result = view.similar()
    assert result["q"]["sort"] == "shared_tags"
    assert result["q"]["order"] == "asc"


def test_project_similar_sort_stars(dbsession):
    """Lines 914-931: stars sort branches."""
    user = _make_user(dbsession, "projsimstars")
    project = _make_project(dbsession, user, "SimStarsProj")
    tag = Tag(name="SimStarsTag")
    tag.created_by = user
    project.tags.append(tag)
    p2 = _make_project(dbsession, user, "SimStarsProj2")
    p2.tags.append(tag)
    user.projects_stars.append(p2)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _make_request(
            dbsession,
            user,
            project=project,
            params={"sort": "stars", "order": order},
        )
        view = ProjectView(request)
        result = view.similar()
        assert result["q"]["sort"] == "stars"


def test_project_similar_sort_comments(dbsession):
    """Lines 938-964: comments sort branches."""
    user = _make_user(dbsession, "projsimcmts")
    project = _make_project(dbsession, user, "SimCmtsProj")
    tag = Tag(name="SimCmtsTag")
    tag.created_by = user
    project.tags.append(tag)
    p2 = _make_project(dbsession, user, "SimCmtsProj2")
    p2.tags.append(tag)
    comment = Comment(comment="c")
    comment.created_by = user
    p2.comments.append(comment)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _make_request(
            dbsession,
            user,
            project=project,
            params={"sort": "comments", "order": order},
        )
        view = ProjectView(request)
        result = view.similar()
        assert result["q"]["sort"] == "comments"


def test_project_similar_sort_generic(dbsession):
    """Lines 972, 975: generic sort asc/desc."""
    user = _make_user(dbsession, "projsimgen")
    project = _make_project(dbsession, user, "SimGenProj")
    tag = Tag(name="SimGenTag")
    tag.created_by = user
    project.tags.append(tag)
    p2 = _make_project(dbsession, user, "SimGenProj2")
    p2.tags.append(tag)
    transaction.commit()
    for order in ("asc", "desc"):
        request = _make_request(
            dbsession,
            user,
            project=project,
            params={"sort": "created_at", "order": order},
        )
        view = ProjectView(request)
        result = view.similar()
        assert result["q"]["sort"] == "created_at"


def test_project_similar_filters(dbsession):
    """Filter params: color, country, subdivision, stage, delivery_method."""
    user = _make_user(dbsession, "projsimfilt")
    project = _make_project(dbsession, user, "SimFiltProj")
    tag = Tag(name="SimFiltTag")
    tag.created_by = user
    project.tags.append(tag)
    p2 = _make_project(dbsession, user, "SimFiltProj2")
    p2.tags.append(tag)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        params={
            "color": "green",
            "country": "PL",
            "subdivision": "PL-14",
            "stage": "",
            "delivery_method": "",
        },
    )
    view = ProjectView(request)
    result = view.similar()
    assert "paginator" in result


# --- add() with tags and query string ---


@patch("marker.views.project.location", return_value={"lat": 52.0, "lon": 21.0})
def test_project_add_post_with_tags(mock_loc, dbsession):
    """Lines 1112-1120: tag processing on add."""
    user = _make_user(dbsession, "projaddtagpost")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        method="POST",
        post={
            "name": "ProjWithTags",
            "street": "",
            "postcode": "",
            "city": "",
            "subdivision": "",
            "country": "",
            "website": "",
            "color": "",
            "deadline": "",
            "stage": "",
            "delivery_method": "",
        },
    )
    request.params = MultiDict(
        [
            ("tag", "NewTag1"),
            ("tag", "NewTag2"),
        ]
    )
    view = ProjectView(request)
    result = view.add()
    assert isinstance(result, HTTPSeeOther)


@patch("marker.views.project.location", return_value=None)
def test_project_add_get_with_query_string(mock_loc, dbsession):
    """Lines 1131-1141: query string pre-population."""
    user = _make_user(dbsession, "projaddqs")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        method="GET",
        post={},
        params={
            "name": "PrePop",
            "street": "QS St",
            "postcode": "11-111",
            "city": "QSCity",
            "country": "PL",
            "subdivision": "PL-14",
            "website": "http://qs.com",
            "color": "primary",
            "deadline": "",
            "stage": "",
            "delivery_method": "",
        },
    )
    request.query_string = "name=PrePop"
    view = ProjectView(request)
    result = view.add()
    assert "form" in result
    assert result["form"].name.data == "PrePop"


# --- edit() with successful geocoding ---


@patch("marker.views.project.location", return_value={"lat": 50.0, "lon": 20.0})
def test_project_edit_post_location_success(mock_loc, dbsession):
    """Lines 1175-1176: location lookup success."""
    user = _make_user(dbsession, "projeditloc")
    project = _make_project(dbsession, user, "EditLocProj")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        method="POST",
        post={
            "name": "EditLocProj",
            "street": "New St",
            "postcode": "",
            "city": "Krakow",
            "subdivision": "",
            "country": "PL",
            "website": "",
            "color": "",
            "deadline": "",
            "stage": "",
            "delivery_method": "",
        },
    )
    view = ProjectView(request)
    result = view.edit()
    assert isinstance(result, HTTPSeeOther)


# --- star() toggle off ---


def test_project_star_toggle_off(dbsession):
    """Lines 1310-1312: remove star from already starred project."""
    user = _make_user(dbsession, "projstartoggle")
    project = _make_project(dbsession, user, "StarToggleProj")
    user.projects_stars.append(project)
    transaction.commit()
    request = _make_request(dbsession, user, project=project, method="POST")
    view = ProjectView(request)
    result = view.star()
    assert "bi-star" in result


# --- projects_stars() sort edge cases ---


def test_projects_stars_invalid_sort(dbsession):
    """Lines 1347-1348: invalid sort defaults."""
    user = _make_user(dbsession, "projstarsisort")
    project = _make_project(dbsession, user, "StarsISortProj")
    user.projects_stars.append(project)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        params={"sort": "invalid", "order": "invalid"},
    )
    view = ProjectView(request)
    result = view.projects_stars()
    assert "paginator" in result


def test_projects_stars_desc_order(dbsession):
    """Line 1360: descending order branch."""
    user = _make_user(dbsession, "projstarsdesc")
    project = _make_project(dbsession, user, "StarsDescProj")
    user.projects_stars.append(project)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        params={"sort": "created_at", "order": "desc"},
    )
    view = ProjectView(request)
    result = view.projects_stars()
    assert "paginator" in result


# --- add_company() POST ---


def test_project_add_company_post(dbsession):
    """Lines 1401-1425: POST add_company."""
    user = _make_user(dbsession, "projaddcopost")
    project = _make_project(dbsession, user, "AddCoPostProj")
    company = _make_company(dbsession, user, "AddCoPostCompany")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        method="POST",
        post={
            "name": "AddCoPostCompany",
            "stage": "",
            "role": "",
            "currency": "",
        },
    )
    view = ProjectView(request)
    result = view.add_company()
    assert isinstance(result, HTTPSeeOther)


# --- add_tag() POST ---


def test_project_add_tag_post(dbsession):
    """Lines 1525-1550: POST add_tag."""
    user = _make_user(dbsession, "projaddtagpost2")
    project = _make_project(dbsession, user, "AddTagPostProj")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        method="POST",
        post={
            "name": "BrandNewTag",
        },
    )
    view = ProjectView(request)
    result = view.add_tag()
    assert isinstance(result, HTTPSeeOther)


# --- add_contact() POST ---


def test_project_add_contact_post(dbsession):
    """Lines 1600+: POST add_contact."""
    user = _make_user(dbsession, "projaddcontpost")
    project = _make_project(dbsession, user, "AddContPostProj")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        method="POST",
        post={
            "name": "NewContact",
            "role": "",
            "phone": "",
            "email": "",
            "color": "",
        },
    )
    view = ProjectView(request)
    result = view.add_contact()
    assert isinstance(result, HTTPSeeOther)


# --- project_add_comment() POST ---


def test_project_add_comment_post(dbsession):
    """Line 1650: POST add_comment."""
    user = _make_user(dbsession, "projaddcmtpost")
    project = _make_project(dbsession, user, "AddCmtPostProj")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        method="POST",
        post={
            "comment": "This is a test comment",
        },
    )
    view = ProjectView(request)
    result = view.project_add_comment()
    assert isinstance(result, HTTPSeeOther)


# --- project_activity_edit() POST ---


def test_project_activity_edit_post(dbsession):
    user = _make_user(dbsession, "projacteditpost")
    project = _make_project(dbsession, user, "ActEditPostProj")
    company = _make_company(dbsession, user, "ActEditPostCo")
    activity = Activity(role="investor", stage="")
    activity.company = company
    activity.project = project
    dbsession.add(activity)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        project=project,
        method="POST",
        post={"stage": "", "role": "", "currency": ""},
    )
    request.matchdict = {"company_id": str(company.id), "project_id": str(project.id)}
    view = ProjectView(request)
    result = view.project_activity_edit()
    assert isinstance(result, HTTPSeeOther)


# --- select() with name ---


def test_project_select_with_name(dbsession):
    """Lines 1479-1506: select with name filter."""
    user = _make_user(dbsession, "projselectname")
    _make_project(dbsession, user, "SelectNameProj")
    transaction.commit()
    request = _make_request(dbsession, user, params={"name": "SelectName"})
    view = ProjectView(request)
    result = view.select()
    assert "projects" in result


def test_project_select_no_name(dbsession):
    """Lines 1479-1506: select without name returns empty."""
    user = _make_user(dbsession, "projselectnoname")
    transaction.commit()
    request = _make_request(dbsession, user, params={})
    view = ProjectView(request)
    result = view.select()
    assert "projects" in result


# ===========================================================================
# Phase 2 – remaining project.py coverage gaps
# ===========================================================================


def test_project_all_invalid_view_mode(dbsession):
    user = _make_user(dbsession, "projinvvm")
    transaction.commit()
    request = _make_request(dbsession, user, params={"view": "INVALID"})
    view = ProjectView(request)
    result = view.all()
    assert result["view_mode"] == "projects"


def test_project_all_filter_tags(dbsession):
    user = _make_user(dbsession, "projfilttag")
    proj = _make_project(dbsession, user, "ProjFiltTagP")
    tag = Tag(name="ProjFiltTag")
    tag.created_by = user
    proj.tags.append(tag)
    dbsession.add(tag)
    transaction.commit()
    request = _make_request(dbsession, user, params={"tag": "ProjFiltTag"})
    view = ProjectView(request)
    result = view.all()
    assert "ProjFiltTag" in result["q"]["tag"]


def test_project_all_filter_name(dbsession):
    user = _make_user(dbsession, "projfiltname")
    _make_project(dbsession, user, "ProjFiltNameP")
    transaction.commit()
    request = _make_request(dbsession, user, params={"name": "ProjFiltName"})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["name"] == "ProjFiltName"


def test_project_all_filter_delivery_method_general_contractor(dbsession):
    user = _make_user(dbsession, "projfltdm")
    proj = _make_project(dbsession, user, "ProjFltDmP")
    proj.delivery_method = "general_contractor"
    transaction.commit()
    request = _make_request(
        dbsession, user, params={"delivery_method": "general_contractor"}
    )
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["delivery_method"] == "general_contractor"


def test_project_all_filter_deadline(dbsession):
    import datetime

    user = _make_user(dbsession, "projfiltdl")
    deadline = datetime.datetime.now() + datetime.timedelta(days=30)
    proj = _make_project(dbsession, user, "ProjFiltDlP")
    proj.deadline = deadline
    transaction.commit()
    deadline_str = deadline.strftime("%Y-%m-%d %H:%M:%S")
    request = _make_request(dbsession, user, params={"deadline": deadline_str})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["deadline"] == deadline_str


def test_project_all_sort_stars_asc(dbsession):
    user = _make_user(dbsession, "projsrtstars")
    proj = _make_project(dbsession, user, "ProjSrtStarsP")
    user.projects_stars.append(proj)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "sort": "stars",
            "order": "asc",
        },
    )
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["sort"] == "stars"


def test_project_all_sort_comments_with_project_id(dbsession):
    from marker.models.comment import Comment

    user = _make_user(dbsession, "projsrtcmts")
    proj = _make_project(dbsession, user, "ProjSrtCmtsP")
    c = Comment(comment="test_comment")
    c.created_by = user
    c.project_id = proj.id
    dbsession.add(c)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "sort": "comments",
            "order": "asc",
        },
    )
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["sort"] == "comments"


def test_project_all_contacts_view_mode_full_attrs(dbsession):
    from marker.models.contact import Contact

    user = _make_user(dbsession, "projcontvm")
    proj = _make_project(dbsession, user, "ProjContVmP")
    tag = Tag(name="ProjContVmTag")
    tag.created_by = user
    proj.tags.append(tag)
    dbsession.add(tag)
    c = Contact(name="ProjContVmCont", role="r", phone="1", email="x@e.com", color="")
    c.created_by = user
    c.project = proj
    dbsession.add(c)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "tag": "ProjContVmTag",
            "view": "contacts",
        },
    )
    view = ProjectView(request)
    result = view.all()
    assert result["view_mode"] == "contacts"


def test_project_comments_invalid_sort_order(dbsession):
    user = _make_user(dbsession, "projcmtinvsrt")
    proj = _make_project(dbsession, user, "ProjCmtInvSrtP")
    proj_id = proj.id
    transaction.commit()
    proj = dbsession.get(Project, proj_id)
    request = _make_request(
        dbsession,
        user,
        project=proj,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    request.matched_route.name = "project_comments"
    view = ProjectView(request)
    result = view.comments()
    assert result["q"]["sort"] == "created_at"


# --- Cover lines 511-701: map_projects status=in_progress ---


def test_project_map_in_progress(dbsession):
    import datetime

    user = _make_user(dbsession, "projmapip")
    proj = _make_project(dbsession, user, "ProjMapIpP")
    proj.deadline = datetime.datetime.now() + datetime.timedelta(days=30)
    proj.latitude = 50.0
    proj.longitude = 20.0
    transaction.commit()
    request = _make_request(dbsession, user, params={"status": "in_progress"})
    view = ProjectView(request)
    result = view.map()
    assert result["q"]["status"] == "in_progress"


# --- Cover lines 813-975: view() bulk select on default route ---


def test_project_view_bulk_select_default_route(dbsession):
    user = _make_user(dbsession, "projvbsdef")
    proj = _make_project(dbsession, user, "ProjVbsDefP")
    proj_id = proj.id
    transaction.commit()
    proj = dbsession.get(Project, proj_id)
    request = _make_request(
        dbsession,
        user,
        project=proj,
        method="POST",
        params={"_select_all": "1", "checked": "1"},
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    request.matched_route.name = "project_view"
    view = ProjectView(request)
    result = view.view()
    assert result is request.response


# --- Cover lines 975, 975: similar() status=completed ---


def test_project_similar_status_completed_with_paginator(dbsession):
    import datetime

    user = _make_user(dbsession, "projsimcomp")
    proj1 = _make_project(dbsession, user, "ProjSimCompP1")
    proj2 = _make_project(dbsession, user, "ProjSimCompP2")
    proj2.deadline = datetime.datetime.now() - datetime.timedelta(days=10)
    tag = Tag(name="ProjSimCompTag")
    tag.created_by = user
    proj1.tags.append(tag)
    proj2.tags.append(tag)
    dbsession.add(tag)
    proj1_id = proj1.id
    transaction.commit()
    proj1 = dbsession.get(Project, proj1_id)
    request = _make_request(
        dbsession,
        user,
        project=proj1,
        params={
            "status": "completed",
        },
    )
    view = ProjectView(request)
    result = view.similar()
    assert "paginator" in result


# --- Cover lines 975-1017: similar() shared_tags asc ---


def test_project_similar_shared_tags_asc(dbsession):
    user = _make_user(dbsession, "projsimsta")
    proj1 = _make_project(dbsession, user, "ProjSimStaP1")
    proj2 = _make_project(dbsession, user, "ProjSimStaP2")
    tag = Tag(name="ProjSimStaTag")
    tag.created_by = user
    proj1.tags.append(tag)
    proj2.tags.append(tag)
    dbsession.add(tag)
    proj1_id = proj1.id
    transaction.commit()
    proj1 = dbsession.get(Project, proj1_id)
    request = _make_request(
        dbsession,
        user,
        project=proj1,
        params={
            "sort": "shared_tags",
            "order": "asc",
        },
    )
    view = ProjectView(request)
    result = view.similar()
    assert "paginator" in result


# --- Cover lines 975-1017: similar() stars desc ---


def test_project_similar_stars_desc(dbsession):
    user = _make_user(dbsession, "projsimstrd")
    proj1 = _make_project(dbsession, user, "ProjSimStrdP1")
    proj2 = _make_project(dbsession, user, "ProjSimStrdP2")
    tag = Tag(name="ProjSimStrdTag")
    tag.created_by = user
    proj1.tags.append(tag)
    proj2.tags.append(tag)
    dbsession.add(tag)
    proj1_id = proj1.id
    transaction.commit()
    proj1 = dbsession.get(Project, proj1_id)
    request = _make_request(
        dbsession,
        user,
        project=proj1,
        params={
            "sort": "stars",
            "order": "desc",
        },
    )
    view = ProjectView(request)
    result = view.similar()
    assert "paginator" in result


# --- Cover lines 975-1017: similar() comments ---


def test_project_similar_comments(dbsession):
    from marker.models.comment import Comment

    user = _make_user(dbsession, "projsimcmt")
    proj1 = _make_project(dbsession, user, "ProjSimCmtP1")
    proj2 = _make_project(dbsession, user, "ProjSimCmtP2")
    cmt = Comment(comment="c")
    cmt.created_by = user
    proj2.comments.append(cmt)
    tag = Tag(name="ProjSimCmtTag")
    tag.created_by = user
    proj1.tags.append(tag)
    proj2.tags.append(tag)
    dbsession.add(tag)
    proj1_id = proj1.id
    transaction.commit()
    proj1 = dbsession.get(Project, proj1_id)
    request = _make_request(
        dbsession,
        user,
        project=proj1,
        params={
            "sort": "comments",
            "order": "asc",
        },
    )
    view = ProjectView(request)
    result = view.similar()
    assert "paginator" in result


# --- Cover line 975: similar() generic sort asc ---


def test_project_similar_name_asc(dbsession):
    user = _make_user(dbsession, "projsimnmasc")
    proj1 = _make_project(dbsession, user, "ProjSimNmP1")
    proj2 = _make_project(dbsession, user, "ProjSimNmP2")
    tag = Tag(name="ProjSimNmTag")
    tag.created_by = user
    proj1.tags.append(tag)
    proj2.tags.append(tag)
    dbsession.add(tag)
    proj1_id = proj1.id
    transaction.commit()
    proj1 = dbsession.get(Project, proj1_id)
    request = _make_request(
        dbsession,
        user,
        project=proj1,
        params={
            "sort": "name",
            "order": "asc",
        },
    )
    view = ProjectView(request)
    result = view.similar()
    assert "paginator" in result


def test_project_similar_invalid_sort_order(dbsession):
    """Cover lines 975, 975: similar() invalid sort/order defaults."""
    user = _make_user(dbsession, "projsiminv")
    proj1 = _make_project(dbsession, user, "ProjSimInvP1")
    proj2 = _make_project(dbsession, user, "ProjSimInvP2")
    tag = Tag(name="ProjSimInvTag")
    tag.created_by = user
    proj1.tags.append(tag)
    proj2.tags.append(tag)
    dbsession.add(tag)
    proj1_id = proj1.id
    transaction.commit()
    proj1 = dbsession.get(Project, proj1_id)
    request = _make_request(
        dbsession,
        user,
        project=proj1,
        params={
            "sort": "INVALID",
            "order": "INVALID",
        },
    )
    view = ProjectView(request)
    result = view.similar()
    assert "paginator" in result


def test_project_similar_in_progress(dbsession):
    """Cover lines 975-1017: similar() status=in_progress."""
    import datetime

    user = _make_user(dbsession, "projsiminprog")
    proj1 = _make_project(dbsession, user, "ProjSimInProgP1")
    proj2 = _make_project(dbsession, user, "ProjSimInProgP2")
    proj2.deadline = datetime.datetime.now() + datetime.timedelta(days=10)
    tag = Tag(name="ProjSimInProgTag")
    tag.created_by = user
    proj1.tags.append(tag)
    proj2.tags.append(tag)
    dbsession.add(tag)
    proj1_id = proj1.id
    transaction.commit()
    proj1 = dbsession.get(Project, proj1_id)
    request = _make_request(
        dbsession,
        user,
        project=proj1,
        params={
            "status": "in_progress",
        },
    )
    view = ProjectView(request)
    result = view.similar()
    assert "paginator" in result


def test_project_similar_stage(dbsession):
    """Cover lines 975-1017: similar() stage filter."""
    user = _make_user(dbsession, "projsimstage")
    proj1 = _make_project(dbsession, user, "ProjSimStageP1")
    proj2 = _make_project(dbsession, user, "ProjSimStageP2")
    proj2.stage = "tender"
    tag = Tag(name="ProjSimStageTag")
    tag.created_by = user
    proj1.tags.append(tag)
    proj2.tags.append(tag)
    dbsession.add(tag)
    proj1_id = proj1.id
    transaction.commit()
    proj1 = dbsession.get(Project, proj1_id)
    request = _make_request(
        dbsession,
        user,
        project=proj1,
        params={
            "stage": "tender",
        },
    )
    view = ProjectView(request)
    result = view.similar()
    assert "paginator" in result


def test_project_similar_delivery_method(dbsession):
    """Cover lines 975-1017: similar() delivery_method filter."""
    user = _make_user(dbsession, "projsimdm")
    proj1 = _make_project(dbsession, user, "ProjSimDmP1")
    proj2 = _make_project(dbsession, user, "ProjSimDmP2")
    proj2.delivery_method = "design-build"
    tag = Tag(name="ProjSimDmTag")
    tag.created_by = user
    proj1.tags.append(tag)
    proj2.tags.append(tag)
    dbsession.add(tag)
    proj1_id = proj1.id
    transaction.commit()
    proj1 = dbsession.get(Project, proj1_id)
    request = _make_request(
        dbsession,
        user,
        project=proj1,
        params={
            "delivery_method": "design-build",
        },
    )
    view = ProjectView(request)
    result = view.similar()
    assert "paginator" in result


def test_project_similar_bulk_select(dbsession):
    """Cover line 975: similar() bulk selection."""
    user = _make_user(dbsession, "projsimbulk")
    proj1 = _make_project(dbsession, user, "ProjSimBulkP1")
    proj2 = _make_project(dbsession, user, "ProjSimBulkP2")
    tag = Tag(name="ProjSimBulkTag")
    tag.created_by = user
    proj1.tags.append(tag)
    proj2.tags.append(tag)
    dbsession.add(tag)
    proj1_id = proj1.id
    transaction.commit()
    proj1 = dbsession.get(Project, proj1_id)
    request = _make_request(
        dbsession,
        user,
        project=proj1,
        method="POST",
        params={
            "_select_all": "1",
            "checked": "1",
        },
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = ProjectView(request)
    result = view.similar()
    assert result is request.response


def test_project_similar_empty_tag_name(dbsession):
    """Cover line 1017: skip tags with empty name in similar tag display."""
    user = _make_user(dbsession, "projsimemptytag")
    proj1 = _make_project(dbsession, user, "ProjSimEmptyP1")
    proj2 = _make_project(dbsession, user, "ProjSimEmptyP2")
    empty_tag = Tag(name="")
    empty_tag.created_by = user
    proj1.tags.append(empty_tag)
    proj2.tags.append(empty_tag)
    dbsession.add(empty_tag)
    valid_tag = Tag(name="ProjSimValidTag")
    valid_tag.created_by = user
    proj1.tags.append(valid_tag)
    proj2.tags.append(valid_tag)
    dbsession.add(valid_tag)
    proj1_id = proj1.id
    transaction.commit()
    proj1 = dbsession.get(Project, proj1_id)
    request = _make_request(
        dbsession,
        user,
        project=proj1,
        params={
            "sort": "shared_tags",
            "order": "desc",
        },
    )
    view = ProjectView(request)
    result = view.similar()
    assert "paginator" in result


def test_project_search_post_with_tag(dbsession):
    user = _make_user(dbsession, "projsrchpost")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        method="POST",
        post={
            "name": "Test",
            "country": "",
            "color": "",
            "subdivision": "",
            "stage": "",
            "delivery_method": "",
        },
    )
    request.params["tag"] = "SomeTag"
    view = ProjectView(request)
    result = view.search()
    assert isinstance(result, HTTPSeeOther)


def test_project_comments_asc(dbsession):
    from marker.models.comment import Comment

    user = _make_user(dbsession, "projcmtasc")
    proj = _make_project(dbsession, user, "ProjCmtAscP")
    c = Comment(comment="test_comment")
    c.created_by = user
    c.project_id = proj.id
    dbsession.add(c)
    proj_id = proj.id
    transaction.commit()
    proj = dbsession.get(Project, proj_id)
    request = _make_request(
        dbsession,
        user,
        project=proj,
        params={
            "sort": "created_at",
            "order": "asc",
        },
    )
    request.matched_route.name = "project_comments"
    view = ProjectView(request)
    result = view.comments()
    assert result["q"]["order"] == "asc"


def test_project_json_stage_delivery(dbsession):
    user = _make_user(dbsession, "projjsonstdm")
    proj = _make_project(dbsession, user, "ProjJsonStDmP")
    proj.stage = "design"
    proj.delivery_method = "general_contractor"
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "stage": "design",
            "delivery_method": "general_contractor",
        },
    )
    view = ProjectView(request)
    result = view.project_json()
    assert isinstance(result, list)


def test_project_json_deadline_relative(dbsession):
    import datetime

    user = _make_user(dbsession, "projjsondl")
    deadline = datetime.datetime.now() + datetime.timedelta(days=30)
    proj = _make_project(dbsession, user, "ProjJsonDlP")
    proj.deadline = deadline
    transaction.commit()
    deadline_str = deadline.strftime("%Y-%m-%d %H:%M:%S")
    request = _make_request(dbsession, user, params={"deadline": deadline_str})
    view = ProjectView(request)
    result = view.project_json()
    assert isinstance(result, list)


def test_project_count_companies_with_data(dbsession):
    user = _make_user(dbsession, "projcntco")
    proj = _make_project(dbsession, user, "ProjCntCoP")
    co = Company(
        name="ProjCntCoCo",
        street="S",
        postcode="00",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="",
        color="",
        NIP="",
        REGON="",
        KRS="",
    )
    co.created_by = user
    dbsession.add(co)
    dbsession.flush()
    from marker.models.association import Activity

    a = Activity(company_id=co.id, project_id=proj.id, role="investor")
    dbsession.add(a)
    proj_id = proj.id
    transaction.commit()
    proj = dbsession.get(Project, proj_id)
    request = _make_request(dbsession, user, project=proj)
    view = ProjectView(request)
    result = view.count_companies()
    assert result == 1


def test_project_all_stars_desc(dbsession):
    user = _make_user(dbsession, "projstdesc")
    proj = _make_project(dbsession, user, "ProjStDescP")
    user.projects_stars.append(proj)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "sort": "stars",
            "order": "desc",
        },
    )
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["sort"] == "stars"
    assert result["q"]["order"] == "desc"


def test_project_all_contacts_view_mode_alt_tag(dbsession):
    user = _make_user(dbsession, "projcontvm")
    proj = _make_project(dbsession, user, "ProjContVmP")
    tag = Tag(name="ContVmTag")
    tag.created_by = user
    proj.tags.append(tag)
    dbsession.add(tag)
    from marker.models.contact import Contact

    c = Contact(name="ProjContVmC", role="r", phone="1", email="a@b.com", color="")
    c.created_by = user
    c.project = proj
    dbsession.add(c)
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={
            "view": "contacts",
            "tag": "ContVmTag",
        },
    )
    view = ProjectView(request)
    result = view.all()
    assert result["view_mode"] == "contacts"


def test_project_all_bulk_select(dbsession):
    user = _make_user(dbsession, "projallbulk")
    _make_project(dbsession, user, "ProjAllBulkP")
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
    view = ProjectView(request)
    result = view.all()
    assert result is request.response


def test_project_map_filters(dbsession):
    user = _make_user(dbsession, "projmapfl")
    proj = _make_project(dbsession, user, "ProjMapFlP")
    proj.stage = "design"
    proj.delivery_method = "general_contractor"
    proj.deadline = __import__("datetime").datetime.now() + __import__(
        "datetime"
    ).timedelta(days=10)
    proj.latitude = 50.0
    proj.longitude = 20.0
    transaction.commit()
    deadline_str = proj.deadline.strftime("%Y-%m-%d %H:%M:%S")
    request = _make_request(
        dbsession,
        user,
        params={
            "stage": "design",
            "delivery_method": "general_contractor",
            "deadline": deadline_str,
        },
    )
    view = ProjectView(request)
    result = view.map()
    assert result["q"]["stage"] == "design"


def test_project_view_bulk_select(dbsession):
    user = _make_user(dbsession, "projvwbulk")
    proj = _make_project(dbsession, user, "ProjVwBulkP")
    proj_id = proj.id
    transaction.commit()
    proj = dbsession.get(Project, proj_id)
    request = _make_request(
        dbsession,
        user,
        project=proj,
        method="POST",
        params={"_select_all": "1", "checked": "1"},
    )
    request.matched_route = MagicMock()
    request.matched_route.name = "project_tags"
    view = ProjectView(request)
    result = view.view()
    assert result is request.response


@patch("marker.views.project.project_autofill_from_website")
def test_project_website_autofill(mock_autofill, dbsession):
    mock_autofill.return_value = {"city": "Warsaw"}
    user = _make_user(dbsession, "projwsaf")
    proj = _make_project(dbsession, user, "ProjWsAfP")
    proj_id = proj.id
    transaction.commit()
    proj = dbsession.get(Project, proj_id)
    request = _make_request(
        dbsession, user, project=proj, params={"website": "http://x.com"}
    )
    view = ProjectView(request)
    result = view.website_autofill()
    assert result["fields"]["city"] == "Warsaw"


def test_project_stars_asc(dbsession):
    user = _make_user(dbsession, "projstasc")
    proj = _make_project(dbsession, user, "ProjStAscP")
    user.projects_stars.append(proj)
    proj_id = proj.id
    transaction.commit()
    proj = dbsession.get(Project, proj_id)
    request = _make_request(
        dbsession,
        user,
        project=proj,
        params={
            "sort": "created_at",
            "order": "asc",
        },
    )
    view = ProjectView(request)
    result = view.projects_stars()
    assert result["q"]["order"] == "asc"


def test_project_activity_edit_not_found_company(dbsession):
    user = _make_user(dbsession, "projactenfco")
    proj = _make_project(dbsession, user, "ProjActNFCoP")
    proj_id = proj.id
    transaction.commit()
    proj = dbsession.get(Project, proj_id)
    request = _make_request(dbsession, user, project=proj)
    request.matchdict = {"company_id": "99999", "project_id": str(proj_id)}
    view = ProjectView(request)
    import pytest
    from pyramid.httpexceptions import HTTPNotFound

    with pytest.raises(HTTPNotFound):
        view.project_activity_edit()


def test_project_activity_edit_not_found_project(dbsession):
    user = _make_user(dbsession, "projactenfpj")
    co = _make_company(dbsession, user, "ProjActNFPjCo")
    co_id = co.id
    transaction.commit()
    request = _make_request(dbsession, user)
    request.matchdict = {"company_id": str(co_id), "project_id": "99999"}
    view = ProjectView(request)
    import pytest
    from pyramid.httpexceptions import HTTPNotFound

    with pytest.raises(HTTPNotFound):
        view.project_activity_edit()


def test_project_unlink_tag_not_found_project(dbsession):
    user = _make_user(dbsession, "projunltagnfp")
    transaction.commit()
    request = _make_request(dbsession, user)
    request.matchdict = {"project_id": "99999", "tag_id": "1"}
    view = ProjectView(request)
    import pytest
    from pyramid.httpexceptions import HTTPNotFound

    with pytest.raises(HTTPNotFound):
        view.unlink_tag()


def test_project_unlink_tag_not_found_tag(dbsession):
    user = _make_user(dbsession, "projunltagnft")
    proj = _make_project(dbsession, user, "ProjUnlTagNFTP")
    proj_id = proj.id
    transaction.commit()
    request = _make_request(dbsession, user)
    request.matchdict = {"project_id": str(proj_id), "tag_id": "99999"}
    view = ProjectView(request)
    import pytest
    from pyramid.httpexceptions import HTTPNotFound

    with pytest.raises(HTTPNotFound):
        view.unlink_tag()


# --- uptime() and uptime_check() ---


def test_project_uptime(dbsession):
    user = _make_user(dbsession, "projuptime")
    _make_project(dbsession, user, "UptimeProj1")
    # Project without website
    p2 = Project(
        name="UptimeProj2",
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website=None,
        color="",
        deadline=None,
        stage="",
        delivery_method="",
    )
    p2.created_by = user
    dbsession.add(p2)
    transaction.commit()
    request = _make_request(dbsession, user)
    view = ProjectView(request)
    result = view.uptime()
    assert "items" in result
    names = [item["name"] for item in result["items"]]
    assert "UptimeProj1" in names
    assert "UptimeProj2" not in names


def test_project_uptime_check_no_url(dbsession):
    user = _make_user(dbsession, "projupchk1")
    transaction.commit()
    request = _make_request(dbsession, user, params={})
    view = ProjectView(request)
    result = view.uptime_check()
    assert result == {"status_code": None, "error": "No URL"}


def test_project_uptime_check_success(dbsession):
    user = _make_user(dbsession, "projupchk2")
    transaction.commit()
    request = _make_request(dbsession, user, params={"url": "https://example.com"})
    view = ProjectView(request)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = view.uptime_check()
    assert result == {"status_code": 200}


def test_project_uptime_check_prepends_https(dbsession):
    user = _make_user(dbsession, "projupchk3")
    transaction.commit()
    request = _make_request(dbsession, user, params={"url": "example.com"})
    view = ProjectView(request)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        result = view.uptime_check()
    assert result == {"status_code": 200}
    called_req = mock_open.call_args[0][0]
    assert called_req.full_url.startswith("https://")


def test_project_uptime_check_http_error(dbsession):
    import urllib.error

    user = _make_user(dbsession, "projupchk4")
    transaction.commit()
    request = _make_request(dbsession, user, params={"url": "https://example.com/404"})
    view = ProjectView(request)
    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.HTTPError(
            "https://example.com/404", 404, "Not Found", {}, None
        ),
    ):
        result = view.uptime_check()
    assert result == {"status_code": 404}


def test_project_uptime_check_generic_error(dbsession):
    user = _make_user(dbsession, "projupchk5")
    transaction.commit()
    request = _make_request(dbsession, user, params={"url": "https://bad.invalid"})
    view = ProjectView(request)
    with patch(
        "urllib.request.urlopen",
        side_effect=OSError("Connection refused"),
    ):
        result = view.uptime_check()
    assert result["status_code"] is None
    assert "Connection refused" in result["error"]


# ===========================================================================
# Date range filtering tests
# ===========================================================================


def test_project_all_date_from(dbsession):
    user = _make_user(dbsession, "projdtf1")
    _make_project(dbsession, user, "DtFromProj")
    transaction.commit()
    request = _make_request(dbsession, user, params={"date_from": "2020-01-01T00:00"})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["date_from"] == "2020-01-01T00:00"
    assert result["counter"] >= 1


def test_project_all_date_to(dbsession):
    user = _make_user(dbsession, "projdtt1")
    _make_project(dbsession, user, "DtToProj")
    transaction.commit()
    request = _make_request(dbsession, user, params={"date_to": "2030-01-01T00:00"})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["date_to"] == "2030-01-01T00:00"
    assert result["counter"] >= 1


def test_project_all_date_range(dbsession):
    user = _make_user(dbsession, "projdtr1")
    _make_project(dbsession, user, "DtRangeProj")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={"date_from": "2020-01-01T00:00", "date_to": "2030-01-01T00:00"},
    )
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["date_from"] == "2020-01-01T00:00"
    assert result["q"]["date_to"] == "2030-01-01T00:00"
    assert result["counter"] >= 1


def test_project_similar_date_from(dbsession):
    user = _make_user(dbsession, "projsimdf")
    project = _make_project(dbsession, user, "SimDfProj")
    tag = Tag(name="ProjSimDfTag")
    tag.created_by = user
    project.tags.append(tag)
    p2 = _make_project(dbsession, user, "SimDfProj2")
    p2.tags.append(tag)
    transaction.commit()
    request = _make_request(
        dbsession, user, project=project, params={"date_from": "2020-01-01T00:00"}
    )
    view = ProjectView(request)
    result = view.similar()
    assert result["q"]["date_from"] == "2020-01-01T00:00"


def test_project_similar_date_to(dbsession):
    user = _make_user(dbsession, "projsimdt")
    project = _make_project(dbsession, user, "SimDtProj")
    tag = Tag(name="ProjSimDtTag")
    tag.created_by = user
    project.tags.append(tag)
    p2 = _make_project(dbsession, user, "SimDtProj2")
    p2.tags.append(tag)
    transaction.commit()
    request = _make_request(
        dbsession, user, project=project, params={"date_to": "2030-01-01T00:00"}
    )
    view = ProjectView(request)
    result = view.similar()
    assert result["q"]["date_to"] == "2030-01-01T00:00"


# --- all() numeric / date range filters ---


def test_project_all_deadline_from(dbsession):
    user = _make_user(dbsession, "projalldf")
    transaction.commit()
    request = _make_request(
        dbsession, user, params={"deadline_from": "2020-01-01T00:00"}
    )
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["deadline_from"] == "2020-01-01T00:00"


def test_project_all_deadline_to(dbsession):
    user = _make_user(dbsession, "projalldt")
    transaction.commit()
    request = _make_request(dbsession, user, params={"deadline_to": "2030-01-01T00:00"})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["deadline_to"] == "2030-01-01T00:00"


def test_project_all_usable_area_from(dbsession):
    user = _make_user(dbsession, "projallua1")
    transaction.commit()
    request = _make_request(dbsession, user, params={"usable_area_from": "100.00"})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["usable_area_from"] == "100.00"


def test_project_all_usable_area_to(dbsession):
    user = _make_user(dbsession, "projallua2")
    transaction.commit()
    request = _make_request(dbsession, user, params={"usable_area_to": "500.00"})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["usable_area_to"] == "500.00"


def test_project_all_cubic_volume_from(dbsession):
    user = _make_user(dbsession, "projallcv1")
    transaction.commit()
    request = _make_request(dbsession, user, params={"cubic_volume_from": "200.00"})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["cubic_volume_from"] == "200.00"


def test_project_all_cubic_volume_to(dbsession):
    user = _make_user(dbsession, "projallcv2")
    transaction.commit()
    request = _make_request(dbsession, user, params={"cubic_volume_to": "999.00"})
    view = ProjectView(request)
    result = view.all()
    assert result["q"]["cubic_volume_to"] == "999.00"


# --- similar() numeric / date range filters ---


def _make_similar_pair(dbsession, prefix):
    user = _make_user(dbsession, prefix)
    project = _make_project(dbsession, user, f"{prefix}Proj")
    tag = Tag(name=f"{prefix}Tag")
    tag.created_by = user
    project.tags.append(tag)
    p2 = _make_project(dbsession, user, f"{prefix}Proj2")
    p2.tags.append(tag)
    return user, project


def test_project_similar_deadline_from(dbsession):
    user, project = _make_similar_pair(dbsession, "simdf2")
    transaction.commit()
    request = _make_request(
        dbsession, user, project=project, params={"deadline_from": "2020-01-01T00:00"}
    )
    view = ProjectView(request)
    result = view.similar()
    assert result["q"]["deadline_from"] == "2020-01-01T00:00"


def test_project_similar_deadline_to(dbsession):
    user, project = _make_similar_pair(dbsession, "simdt2")
    transaction.commit()
    request = _make_request(
        dbsession, user, project=project, params={"deadline_to": "2030-01-01T00:00"}
    )
    view = ProjectView(request)
    result = view.similar()
    assert result["q"]["deadline_to"] == "2030-01-01T00:00"


def test_project_similar_usable_area_from(dbsession):
    user, project = _make_similar_pair(dbsession, "simua1")
    transaction.commit()
    request = _make_request(
        dbsession, user, project=project, params={"usable_area_from": "100.00"}
    )
    view = ProjectView(request)
    result = view.similar()
    assert result["q"]["usable_area_from"] == "100.00"


def test_project_similar_usable_area_to(dbsession):
    user, project = _make_similar_pair(dbsession, "simua2")
    transaction.commit()
    request = _make_request(
        dbsession, user, project=project, params={"usable_area_to": "500.00"}
    )
    view = ProjectView(request)
    result = view.similar()
    assert result["q"]["usable_area_to"] == "500.00"


def test_project_similar_cubic_volume_from(dbsession):
    user, project = _make_similar_pair(dbsession, "simcv1")
    transaction.commit()
    request = _make_request(
        dbsession, user, project=project, params={"cubic_volume_from": "200.00"}
    )
    view = ProjectView(request)
    result = view.similar()
    assert result["q"]["cubic_volume_from"] == "200.00"


def test_project_similar_cubic_volume_to(dbsession):
    user, project = _make_similar_pair(dbsession, "simcv2")
    transaction.commit()
    request = _make_request(
        dbsession, user, project=project, params={"cubic_volume_to": "999.00"}
    )
    view = ProjectView(request)
    result = view.similar()
    assert result["q"]["cubic_volume_to"] == "999.00"


# --- InvalidOperation branches for all() ---


def test_project_all_usable_area_from_invalid(dbsession):
    user = _make_user(dbsession, "alluainv1")
    transaction.commit()
    request = _make_request(dbsession, user, params={"usable_area_from": "abc"})
    view = ProjectView(request)
    result = view.all()
    assert "usable_area_from" not in result["q"]


def test_project_all_usable_area_to_invalid(dbsession):
    user = _make_user(dbsession, "alluainv2")
    transaction.commit()
    request = _make_request(dbsession, user, params={"usable_area_to": "abc"})
    view = ProjectView(request)
    result = view.all()
    assert "usable_area_to" not in result["q"]


def test_project_all_cubic_volume_from_invalid(dbsession):
    user = _make_user(dbsession, "allcvinv1")
    transaction.commit()
    request = _make_request(dbsession, user, params={"cubic_volume_from": "abc"})
    view = ProjectView(request)
    result = view.all()
    assert "cubic_volume_from" not in result["q"]


def test_project_all_cubic_volume_to_invalid(dbsession):
    user = _make_user(dbsession, "allcvinv2")
    transaction.commit()
    request = _make_request(dbsession, user, params={"cubic_volume_to": "abc"})
    view = ProjectView(request)
    result = view.all()
    assert "cubic_volume_to" not in result["q"]


# --- InvalidOperation branches for similar() ---


def test_project_similar_usable_area_from_invalid(dbsession):
    user, project = _make_similar_pair(dbsession, "simuainv1")
    transaction.commit()
    request = _make_request(
        dbsession, user, project=project, params={"usable_area_from": "abc"}
    )
    view = ProjectView(request)
    result = view.similar()
    assert "usable_area_from" not in result["q"]


def test_project_similar_usable_area_to_invalid(dbsession):
    user, project = _make_similar_pair(dbsession, "simuainv2")
    transaction.commit()
    request = _make_request(
        dbsession, user, project=project, params={"usable_area_to": "abc"}
    )
    view = ProjectView(request)
    result = view.similar()
    assert "usable_area_to" not in result["q"]


def test_project_similar_cubic_volume_from_invalid(dbsession):
    user, project = _make_similar_pair(dbsession, "simcvinv1")
    transaction.commit()
    request = _make_request(
        dbsession, user, project=project, params={"cubic_volume_from": "abc"}
    )
    view = ProjectView(request)
    result = view.similar()
    assert "cubic_volume_from" not in result["q"]


def test_project_similar_cubic_volume_to_invalid(dbsession):
    user, project = _make_similar_pair(dbsession, "simcvinv2")
    transaction.commit()
    request = _make_request(
        dbsession, user, project=project, params={"cubic_volume_to": "abc"}
    )
    view = ProjectView(request)
    result = view.similar()
    assert "cubic_volume_to" not in result["q"]


@patch("marker.views.project.project_autofill_from_website")
def test_project_website_autofill_error(mock_autofill, dbsession):
    mock_autofill.side_effect = RuntimeError("API unavailable")
    user = _make_user(dbsession, "projwsaferr")
    proj = _make_project(dbsession, user, "ProjWsAfErrP")
    proj_id = proj.id
    transaction.commit()
    proj = dbsession.get(Project, proj_id)
    request = _make_request(
        dbsession, user, project=proj, params={"website": "http://x.com"}
    )
    view = ProjectView(request)
    result = view.website_autofill()
    assert result["fields"] == {}
    assert "API unavailable" in result["error"]
    assert request.response.status_code == 502


@patch("marker.views.project.project_autofill_from_website")
def test_project_website_autofill_error_long_response(mock_autofill, dbsession):
    # Simulate a long error message with 'Response:'
    long_msg = "Some error occurred. Response: " + ("x" * 500)
    mock_autofill.side_effect = RuntimeError(long_msg)
    user = _make_user(dbsession, "projwsaferrlong")
    proj = _make_project(dbsession, user, "ProjWsAfErrLongP")
    proj_id = proj.id
    transaction.commit()
    proj = dbsession.get(Project, proj_id)
    request = _make_request(
        dbsession, user, project=proj, params={"website": "http://x.com"}
    )
    # Patch session.flash to append to a real list
    flashes = []

    def flash(msg, category=None):
        flashes.append((category, msg))

    request.session.flash = flash
    view = ProjectView(request)
    result = view.website_autofill()
    # The returned error is the original exception, but the flash message is truncated and should contain (details omitted)
    flash_msg = flashes[-1][1]
    assert "(details omitted)" in flash_msg
    assert request.response.status_code == 502


@patch("marker.views.project.project_autofill_from_website")
def test_project_website_autofill_error_flash_truncation(mock_autofill, dbsession):
    # Simulate an extremely long error message to trigger flash truncation
    long_msg = "A" * 2000
    mock_autofill.side_effect = RuntimeError(long_msg)
    user = _make_user(dbsession, "projwsaferrflash")
    proj = _make_project(dbsession, user, "ProjWsAfErrFlashP")
    proj_id = proj.id
    transaction.commit()
    proj = dbsession.get(Project, proj_id)
    request = _make_request(
        dbsession, user, project=proj, params={"website": "http://x.com"}
    )
    flashes = []

    def flash(msg, category=None):
        flashes.append((category, msg))

    request.session.flash = flash
    view = ProjectView(request)
    result = view.website_autofill()
    # The flash message should be truncated to max_len and end with '...'
    flash_msg = flashes[-1][1]
    assert flash_msg.endswith("...")
    assert request.response.status_code == 502


# ===========================================================================
# add() validate_from_ai and add_ai() coverage
# ===========================================================================


def test_project_add_get_validate_from_ai(dbsession):
    """GET add with validate=1 triggers form.validate() — line 1260."""
    user = _make_user(dbsession, "projaddvai")
    transaction.commit()
    request = _make_request(
        dbsession, user, method="GET", params={"validate": "1", "name": "ValidateProj"}
    )
    view = ProjectView(request)
    result = view.add()
    assert "form" in result
    # form should have been validated (errors may be present but form is returned)


@patch("marker.views.project.location_details", return_value=None)
@patch(
    "marker.views.project.project_autofill_from_website",
    return_value={"name": "NewAIProjInv"},
)
def test_project_add_ai_post_invalid_form_htmx(mock_autofill, mock_geo, dbsession):
    """Autofill returns data that fails ProjectForm validation (missing country).
    With HX-Request, should HX-Redirect to manual add form."""
    user = _make_user(dbsession, "projaddaihtmx")
    transaction.commit()
    request = _make_request(
        dbsession, user, method="POST", post={"website": "http://example.com"}
    )
    request.headers = {"HX-Request": "true"}
    view = ProjectView(request)
    result = view.add_ai()
    assert result.status_code == 303


@patch("marker.views.project.location_details", return_value=None)
@patch(
    "marker.views.project.project_autofill_from_website",
    return_value={"name": "NewAIProjInvNoHX"},
)
def test_project_add_ai_post_invalid_form_no_htmx(mock_autofill, mock_geo, dbsession):
    """Autofill returns invalid data without HX-Request; returns form dict."""
    user = _make_user(dbsession, "projaddaiinvnohx")
    transaction.commit()
    request = _make_request(
        dbsession, user, method="POST", post={"website": "http://example.com"}
    )
    request.headers = {}
    view = ProjectView(request)
    result = view.add_ai()
    assert isinstance(result, dict)
    assert "form" in result


@patch("marker.views.project.location_details", return_value={"lat": 1.0, "lon": 2.0})
@patch(
    "marker.views.project.project_autofill_from_website",
    return_value={
        "name": "NewAIProjSuccess",
        "country": "PL",
        "stage": "",
        "delivery_method": "",
        "object_category": "",
    },
)
def test_project_add_ai_post_success_htmx(mock_autofill, mock_geo, dbsession):
    """Autofill returns valid data; project saved, HX-Redirect issued."""
    user = _make_user(dbsession, "projaddaisuccess")
    transaction.commit()
    request = _make_request(
        dbsession, user, method="POST", post={"website": "http://example.com"}
    )
    request.headers = {"HX-Request": "true"}
    view = ProjectView(request)
    result = view.add_ai()
    assert result.status_code == 303


@patch("marker.views.project.location_details", return_value=None)
@patch(
    "marker.views.project.project_autofill_from_website",
    return_value={
        "name": "NewAIProjSucNoHX",
        "country": "PL",
        "stage": "",
        "delivery_method": "",
        "object_category": "",
    },
)
def test_project_add_ai_post_success_no_htmx(mock_autofill, mock_geo, dbsession):
    """Autofill returns valid data without HX-Request; HTTPSeeOther redirect."""
    user = _make_user(dbsession, "projaddaisucnohx")
    transaction.commit()
    request = _make_request(
        dbsession, user, method="POST", post={"website": "http://example.com"}
    )
    request.headers = {}
    view = ProjectView(request)
    result = view.add_ai()
    assert isinstance(result, HTTPSeeOther)


@patch(
    "marker.views.project.project_autofill_from_website",
    side_effect=Exception("autofill failed"),
)
def test_project_add_ai_post_exception_htmx(mock_autofill, dbsession):
    """Exception during autofill with HX-Request triggers HX-Redirect."""
    user = _make_user(dbsession, "projaddaierr")
    transaction.commit()
    request = _make_request(
        dbsession, user, method="POST", post={"website": "http://fail.com"}
    )
    request.headers = {"HX-Request": "true"}
    view = ProjectView(request)
    result = view.add_ai()
    assert result.status_code == 303


@patch(
    "marker.views.project.project_autofill_from_website",
    side_effect=Exception("autofill failed"),
)
def test_project_add_ai_post_exception_no_htmx(mock_autofill, dbsession):
    """Exception during autofill without HX-Request gives HTTPSeeOther redirect."""
    user = _make_user(dbsession, "projaddaierrnohx")
    transaction.commit()
    request = _make_request(
        dbsession, user, method="POST", post={"website": "http://fail.com"}
    )
    request.headers = {}
    view = ProjectView(request)
    result = view.add_ai()
    assert isinstance(result, HTTPSeeOther)


@patch("marker.views.project.location_details", return_value=None)
@patch(
    "marker.views.project.project_autofill_from_website",
    return_value={"name": "ExistingAIProj", "country": "PL"},
)
def test_project_add_ai_existing_project(mock_autofill, mock_geo, dbsession):
    """If a project with the autofilled name already exists, redirect to it."""
    user = _make_user(dbsession, "projaddaiexist")
    _make_project(dbsession, user, "ExistingAIProj")
    transaction.commit()
    request = _make_request(
        dbsession, user, method="POST", post={"website": "http://existing.com"}
    )
    request.headers = {}
    view = ProjectView(request)
    result = view.add_ai()
    assert isinstance(result, HTTPSeeOther)


@patch("marker.views.project.location_details", return_value=None)
@patch(
    "marker.views.project.project_autofill_from_website",
    return_value={"name": "ExistAIProjHTMX", "country": "PL"},
)
def test_project_add_ai_existing_project_htmx(mock_autofill, mock_geo, dbsession):
    """If a project with the autofilled name already exists, HX-Redirect issued."""
    user = _make_user(dbsession, "projaddaiexhtmx")
    _make_project(dbsession, user, "ExistAIProjHTMX")
    transaction.commit()
    request = _make_request(
        dbsession, user, method="POST", post={"website": "http://existhtmx.com"}
    )
    request.headers = {"HX-Request": "true"}
    view = ProjectView(request)
    result = view.add_ai()
    assert result.status_code == 303


def test_project_add_ai_get(dbsession):
    """GET add_ai should return form dict."""
    user = _make_user(dbsession, "projaddaiget")
    transaction.commit()
    request = _make_request(dbsession, user, method="GET")
    request.headers = {}
    view = ProjectView(request)
    result = view.add_ai()
    assert "form" in result
