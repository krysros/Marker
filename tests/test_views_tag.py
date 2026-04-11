"""Tests for marker/views/tag.py"""

from unittest.mock import MagicMock

import pytest
import transaction
from pyramid.httpexceptions import HTTPSeeOther
from webob.multidict import MultiDict

import marker.forms.ts
from marker.models.company import Company
from marker.models.project import Project
from marker.models.tag import Tag
from marker.models.user import User
from marker.views.tag import TagView
from tests.conftest import DummyRequestWithIdentity


@pytest.fixture(autouse=True)
def patch_translationstring_str(monkeypatch):
    monkeypatch.setattr(
        marker.forms.ts.TranslationString, "__str__", lambda self: self.msg
    )
    yield


def _make_user(dbsession, name="taguser"):
    user = User(
        name=name, fullname="T U", email=f"{name}@e.com", role="admin", password="pw"
    )
    dbsession.add(user)
    dbsession.flush()
    return user


def _make_tag(dbsession, user, name="TestTag"):
    tag = Tag(name=name)
    tag.created_by = user
    dbsession.add(tag)
    dbsession.flush()
    return tag


def _make_company(dbsession, user, name="TagTestCo"):
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


def _make_project(dbsession, user, name="TagTestProj"):
    project = Project(
        name=name,
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="",
        color="green",
        deadline=None,
        stage="",
        delivery_method="",
    )
    project.created_by = user
    dbsession.add(project)
    dbsession.flush()
    return project


def _make_request(dbsession, user, tag=None, method="GET", params=None, post=None):
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = method
    request.GET = MultiDict(params or {})
    request.POST = MultiDict(post or {})
    request.params = MultiDict(params or {})
    request.locale_name = "en"
    request.translate = lambda x: x
    request.route_url = lambda *a, **kw: "/tag"
    request.session = MagicMock()
    request.response = MagicMock()
    request.response.headers = {}
    request.context = MagicMock()
    if tag:
        request.context.tag = tag
    request.environ = {}
    request.environ["webob._parsed_get_vars"] = (MultiDict(), MultiDict())
    request.environ["webob._parsed_post_vars"] = (MultiDict(post or {}), MultiDict())
    request.environ["webob._parsed_params_vars"] = (
        MultiDict(params or {}),
        MultiDict(),
    )
    request.path_qs = "/tag"
    return request


# --- all() ---


def test_tag_all_default(dbsession):
    user = _make_user(dbsession)
    _make_tag(dbsession, user)
    transaction.commit()
    request = _make_request(dbsession, user)
    view = TagView(request)
    result = view.all()
    assert "paginator" in result
    assert "counter" in result
    assert "form" in result


def test_tag_all_filter_name_unique(dbsession):
    user = _make_user(dbsession, "tagnameuser")
    _make_tag(dbsession, user, "UniqueTagName")
    transaction.commit()
    request = _make_request(dbsession, user, params={"name": "Unique"})
    view = TagView(request)
    result = view.all()
    assert result["q"]["name"] == "Unique"


def test_tag_all_filter_category_companies(dbsession):
    user = _make_user(dbsession, "tagcatuser")
    tag = _make_tag(dbsession, user, "CatTag")
    company = _make_company(dbsession, user)
    company.tags.append(tag)
    transaction.commit()
    request = _make_request(dbsession, user, params={"category": "companies"})
    view = TagView(request)
    result = view.all()
    assert result["q"]["category"] == "companies"


def test_tag_all_filter_category_projects(dbsession):
    user = _make_user(dbsession, "tagprojcatuser")
    tag = _make_tag(dbsession, user, "ProjCatTag")
    project = _make_project(dbsession, user)
    project.tags.append(tag)
    transaction.commit()
    request = _make_request(dbsession, user, params={"category": "projects"})
    view = TagView(request)
    result = view.all()
    assert result["q"]["category"] == "projects"


def test_tag_all_sort_asc(dbsession):
    user = _make_user(dbsession, "tagsortascuser")
    transaction.commit()
    request = _make_request(dbsession, user, params={"sort": "name", "order": "asc"})
    view = TagView(request)
    result = view.all()
    assert result["q"]["order"] == "asc"


# --- count() ---


def test_tag_count_empty(dbsession):
    user = _make_user(dbsession, "tagcntuser")
    transaction.commit()
    request = _make_request(dbsession, user)
    view = TagView(request)
    result = view.count()
    assert isinstance(result, int)


# --- view() ---


def test_tag_view(dbsession):
    user = _make_user(dbsession, "tagviewuser")
    tag = _make_tag(dbsession, user, "ViewTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag)
    view = TagView(request)
    result = view.view()
    assert "tag" in result
    assert "tag_pills" in result
    assert result["tag"].name == "ViewTag"


# --- map_companies() ---


def test_tag_map_companies(dbsession):
    user = _make_user(dbsession, "tagmapcouser")
    tag = _make_tag(dbsession, user, "MapCoTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag)
    view = TagView(request)
    result = view.map_companies()
    assert "tag" in result
    assert "url" in result


def test_tag_map_companies_filters_empty(dbsession):
    user = _make_user(dbsession, "tagmapcofl")
    tag = _make_tag(dbsession, user, "MapCoFlTag")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={"color": "red", "country": "PL", "subdivision": "PL-14"},
    )
    view = TagView(request)
    result = view.map_companies()
    assert result["q"]["color"] == "red"


# --- map_projects() ---


def test_tag_map_projects(dbsession):
    user = _make_user(dbsession, "tagmappruser")
    tag = _make_tag(dbsession, user, "MapPrTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag)
    view = TagView(request)
    result = view.map_projects()
    assert "tag" in result


def test_tag_map_projects_filters(dbsession):
    user = _make_user(dbsession, "tagmapprfl")
    tag = _make_tag(dbsession, user, "MapPrFlTag")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "stage": "draft",
            "status": "in_progress",
            "delivery_method": "courier",
            "color": "green",
            "country": "PL",
        },
    )
    view = TagView(request)
    result = view.map_projects()
    assert result["q"]["stage"] == "draft"


def test_tag_map_projects_status_completed(dbsession):
    user = _make_user(dbsession, "tagmapprcomp")
    tag = _make_tag(dbsession, user, "MapPrCompTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag, params={"status": "completed"})
    view = TagView(request)
    result = view.map_projects()
    assert result["q"]["status"] == "completed"


# --- json_companies() ---


def test_tag_json_companies(dbsession):
    user = _make_user(dbsession, "tagjsoncouser")
    tag = _make_tag(dbsession, user, "JsonCoTag")
    company = _make_company(dbsession, user, "JsonCoCompany")
    company.tags.append(tag)
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag)
    view = TagView(request)
    result = view.json_companies()
    assert isinstance(result, list)
    assert len(result) >= 1


def test_tag_json_companies_bbox_empty(dbsession):
    user = _make_user(dbsession, "tagjsoncobbox")
    tag = _make_tag(dbsession, user, "JsonCoBboxTag")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={"north": "54", "south": "50", "east": "22", "west": "18"},
    )
    view = TagView(request)
    result = view.json_companies()
    assert isinstance(result, list)


def test_tag_json_companies_bbox_invalid(dbsession):
    user = _make_user(dbsession, "tagjsoncobboxinv")
    tag = _make_tag(dbsession, user, "JsonCoInvTag")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={"north": "bad", "south": "bad", "east": "bad", "west": "bad"},
    )
    view = TagView(request)
    result = view.json_companies()
    assert isinstance(result, list)


# --- json_projects() ---


def test_tag_json_projects(dbsession):
    user = _make_user(dbsession, "tagjsonpruser")
    tag = _make_tag(dbsession, user, "JsonPrTag")
    project = _make_project(dbsession, user, "JsonPrProject")
    project.tags.append(tag)
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag)
    view = TagView(request)
    result = view.json_projects()
    assert isinstance(result, list)


def test_tag_json_projects_filters(dbsession):
    user = _make_user(dbsession, "tagjsonprfl")
    tag = _make_tag(dbsession, user, "JsonPrFlTag")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "stage": "draft",
            "status": "in_progress",
            "delivery_method": "courier",
            "color": "green",
            "country": "PL",
            "north": "54",
            "south": "50",
            "east": "22",
            "west": "18",
        },
    )
    view = TagView(request)
    result = view.json_projects()
    assert isinstance(result, list)


def test_tag_json_projects_status_completed(dbsession):
    user = _make_user(dbsession, "tagjsonprcomp")
    tag = _make_tag(dbsession, user, "JsonPrCompTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag, params={"status": "completed"})
    view = TagView(request)
    result = view.json_projects()
    assert isinstance(result, list)


# --- companies() ---


def test_tag_companies(dbsession):
    user = _make_user(dbsession, "tagcouser")
    tag = _make_tag(dbsession, user, "CoTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag)
    view = TagView(request)
    result = view.companies()
    assert "paginator" in result
    assert "tag" in result


def test_tag_companies_with_filters(dbsession):
    user = _make_user(dbsession, "tagcofluser")
    tag = _make_tag(dbsession, user, "CoFlTag")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "color": "red",
            "country": "PL",
            "subdivision": "PL-14",
            "sort": "name",
            "order": "asc",
        },
    )
    view = TagView(request)
    result = view.companies()
    assert result["q"]["color"] == "red"


def test_tag_companies_sort_stars(dbsession):
    user = _make_user(dbsession, "tagcostaruser")
    tag = _make_tag(dbsession, user, "CoStarTag")
    company = _make_company(dbsession, user, "CoStarCo")
    company.tags.append(tag)
    user.companies_stars.append(company)
    transaction.commit()
    request = _make_request(
        dbsession, user, tag=tag, params={"sort": "stars", "order": "desc"}
    )
    view = TagView(request)
    result = view.companies()
    assert result["q"]["sort"] == "stars"


def test_tag_companies_sort_stars_asc(dbsession):
    user = _make_user(dbsession, "tagcostarasc")
    tag = _make_tag(dbsession, user, "CoStarAscTag")
    company = _make_company(dbsession, user, "CoStarAscCo")
    company.tags.append(tag)
    user.companies_stars.append(company)
    transaction.commit()
    request = _make_request(
        dbsession, user, tag=tag, params={"sort": "stars", "order": "asc"}
    )
    view = TagView(request)
    result = view.companies()
    assert result["q"]["order"] == "asc"


def test_tag_companies_sort_comments(dbsession):
    user = _make_user(dbsession, "tagcocmtuser")
    tag = _make_tag(dbsession, user, "CoCmtTag")
    from marker.models.comment import Comment

    company = _make_company(dbsession, user, "CoCmtCo")
    company.tags.append(tag)
    comment = Comment(comment="test")
    comment.created_by = user
    company.comments.append(comment)
    transaction.commit()
    request = _make_request(
        dbsession, user, tag=tag, params={"sort": "comments", "order": "desc"}
    )
    view = TagView(request)
    result = view.companies()
    assert result["q"]["sort"] == "comments"


def test_tag_companies_sort_comments_asc(dbsession):
    user = _make_user(dbsession, "tagcocmtasc")
    tag = _make_tag(dbsession, user, "CoCmtAscTag")
    from marker.models.comment import Comment

    company = _make_company(dbsession, user, "CoCmtAscCo")
    company.tags.append(tag)
    comment = Comment(comment="test asc")
    comment.created_by = user
    company.comments.append(comment)
    transaction.commit()
    request = _make_request(
        dbsession, user, tag=tag, params={"sort": "comments", "order": "asc"}
    )
    view = TagView(request)
    result = view.companies()
    assert result["q"]["order"] == "asc"


# --- projects() ---


def test_tag_projects(dbsession):
    user = _make_user(dbsession, "tagpruser")
    tag = _make_tag(dbsession, user, "PrTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag)
    view = TagView(request)
    result = view.projects()
    assert "paginator" in result
    assert "tag" in result


def test_tag_projects_with_filters(dbsession):
    user = _make_user(dbsession, "tagprfluser")
    tag = _make_tag(dbsession, user, "PrFlTag")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "stage": "draft",
            "color": "green",
            "status": "in_progress",
            "delivery_method": "courier",
            "country": "PL",
            "sort": "name",
            "order": "asc",
        },
    )
    view = TagView(request)
    result = view.projects()
    assert result["q"]["stage"] == "draft"


def test_tag_projects_status_completed(dbsession):
    user = _make_user(dbsession, "tagprcompuser")
    tag = _make_tag(dbsession, user, "PrCompTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag, params={"status": "completed"})
    view = TagView(request)
    result = view.projects()
    assert result["q"]["status"] == "completed"


def test_tag_projects_sort_stars(dbsession):
    user = _make_user(dbsession, "tagprstaruser")
    tag = _make_tag(dbsession, user, "PrStarTag")
    project = _make_project(dbsession, user, "PrStarProj")
    project.tags.append(tag)
    user.projects_stars.append(project)
    transaction.commit()
    request = _make_request(
        dbsession, user, tag=tag, params={"sort": "stars", "order": "desc"}
    )
    view = TagView(request)
    result = view.projects()
    assert result["q"]["sort"] == "stars"


def test_tag_projects_sort_comments(dbsession):
    user = _make_user(dbsession, "tagprcmtuser")
    tag = _make_tag(dbsession, user, "PrCmtTag")
    from marker.models.comment import Comment

    project = _make_project(dbsession, user, "PrCmtProj")
    project.tags.append(tag)
    comment = Comment(comment="proj comment")
    comment.created_by = user
    project.comments.append(comment)
    transaction.commit()
    request = _make_request(
        dbsession, user, tag=tag, params={"sort": "comments", "order": "desc"}
    )
    view = TagView(request)
    result = view.projects()
    assert result["q"]["sort"] == "comments"


# --- export_companies() ---


def test_tag_export_companies(dbsession):
    user = _make_user(dbsession, "tagexcouser")
    tag = _make_tag(dbsession, user, "ExCoTag")
    company = _make_company(dbsession, user, "ExCoCo")
    company.tags.append(tag)
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag)
    view = TagView(request)
    result = view.export_companies()
    assert result.content_type.startswith("application/vnd.openxmlformats")


# --- export_projects() ---


def test_tag_export_projects(dbsession):
    user = _make_user(dbsession, "tagexpruser")
    tag = _make_tag(dbsession, user, "ExPrTag")
    project = _make_project(dbsession, user, "ExPrProj")
    project.tags.append(tag)
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag)
    view = TagView(request)
    result = view.export_projects()
    assert result.content_type.startswith("application/vnd.openxmlformats")


# --- count_companies() / count_projects() ---
# Note: These view methods share names with instance attributes set in __init__,
# so we must call them via the unbound class method to avoid the attribute shadow.


def test_tag_count_companies(dbsession):
    user = _make_user(dbsession, "tagcntcouser")
    tag = _make_tag(dbsession, user, "CntCoTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag)
    view = TagView(request)
    result = TagView.count_companies(view)
    assert isinstance(result, int)


def test_tag_count_projects(dbsession):
    user = _make_user(dbsession, "tagcntpruser")
    tag = _make_tag(dbsession, user, "CntPrTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag)
    view = TagView(request)
    result = TagView.count_projects(view)
    assert isinstance(result, int)


# --- add() ---


def test_tag_add_get(dbsession):
    user = _make_user(dbsession, "tagaddgetuser")
    transaction.commit()
    request = _make_request(dbsession, user, method="GET", post={})
    view = TagView(request)
    result = view.add()
    assert "form" in result
    assert "heading" in result


def test_tag_add_post(dbsession):
    user = _make_user(dbsession, "tagaddpostuser")
    transaction.commit()
    request = _make_request(dbsession, user, method="POST", post={"name": "NewTag123"})
    view = TagView(request)
    result = view.add()
    assert isinstance(result, HTTPSeeOther)


# --- edit() ---


def test_tag_edit_get(dbsession):
    user = _make_user(dbsession, "tageditgetuser")
    tag = _make_tag(dbsession, user, "EditGetTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag, method="GET", post={})
    view = TagView(request)
    result = view.edit()
    assert "form" in result


def test_tag_edit_post(dbsession):
    user = _make_user(dbsession, "tageditpostuser")
    tag = _make_tag(dbsession, user, "EditPostTag")
    transaction.commit()
    request = _make_request(
        dbsession, user, tag=tag, method="POST", post={"name": "EditPostTag"}
    )
    view = TagView(request)
    result = view.edit()
    assert isinstance(result, HTTPSeeOther)


# --- delete() ---


def test_tag_delete(dbsession):
    user = _make_user(dbsession, "tagdeleteuser")
    tag = _make_tag(dbsession, user, "DeleteTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag, method="POST")
    view = TagView(request)
    result = view.delete()
    assert result.status_code == 303


# --- tag_del_row() ---


def test_tag_del_row(dbsession):
    user = _make_user(dbsession, "tagdelrowuser")
    tag = _make_tag(dbsession, user, "DelRowTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag, method="POST")
    view = TagView(request)
    result = view.tag_del_row()
    assert result == ""


# --- check() ---


def test_tag_check(dbsession):
    user = _make_user(dbsession, "tagcheckuser")
    tag = _make_tag(dbsession, user, "CheckTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag, method="POST")
    view = TagView(request)
    result = view.check()
    assert "checked" in result


# --- select() ---


def test_tag_select(dbsession):
    user = _make_user(dbsession, "tagselectuser")
    _make_tag(dbsession, user, "SelectTag")
    transaction.commit()
    request = _make_request(dbsession, user, params={"name": "Select"})
    view = TagView(request)
    result = view.select()
    assert "tags" in result


def test_tag_select_empty(dbsession):
    user = _make_user(dbsession, "tagselectempty")
    transaction.commit()
    request = _make_request(dbsession, user, params={})
    view = TagView(request)
    result = view.select()
    assert result["tags"] == []


# --- search() ---


def test_tag_search_get(dbsession):
    user = _make_user(dbsession, "tagsearchget")
    transaction.commit()
    request = _make_request(dbsession, user, method="GET", post={})
    view = TagView(request)
    result = view.search()
    assert "form" in result


def test_tag_search_post(dbsession):
    user = _make_user(dbsession, "tagsearchpost")
    transaction.commit()
    request = _make_request(dbsession, user, method="POST", post={"name": "SomeTag"})
    view = TagView(request)
    result = view.search()
    assert isinstance(result, HTTPSeeOther)


# --- add_company() ---


def test_tag_add_company_get(dbsession):
    user = _make_user(dbsession, "tagaddcoget")
    tag = _make_tag(dbsession, user, "AddCoGetTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag, method="GET", post={})
    view = TagView(request)
    result = view.add_company()
    assert "form" in result


def test_tag_add_company_post(dbsession):
    user = _make_user(dbsession, "tagaddcopost")
    tag = _make_tag(dbsession, user, "AddCoPostTag")
    company = _make_company(dbsession, user, "AddCoPostCo")
    transaction.commit()
    request = _make_request(
        dbsession, user, tag=tag, method="POST", post={"name": company.name}
    )
    view = TagView(request)
    result = view.add_company()
    assert isinstance(result, HTTPSeeOther)


# --- add_project() ---


def test_tag_add_project_get(dbsession):
    user = _make_user(dbsession, "tagaddprget")
    tag = _make_tag(dbsession, user, "AddPrGetTag")
    transaction.commit()
    request = _make_request(dbsession, user, tag=tag, method="GET", post={})
    view = TagView(request)
    result = view.add_project()
    assert "form" in result


def test_tag_add_project_post(dbsession):
    user = _make_user(dbsession, "tagaddprpost")
    tag = _make_tag(dbsession, user, "AddPrPostTag")
    project = _make_project(dbsession, user, "AddPrPostProj")
    transaction.commit()
    request = _make_request(
        dbsession, user, tag=tag, method="POST", post={"name": project.name}
    )
    view = TagView(request)
    result = view.add_project()
    assert isinstance(result, HTTPSeeOther)


# ===========================================================================
# Phase 2 – remaining tag.py coverage gaps
# ===========================================================================


def test_tag_all_filter_name_with_data(dbsession):
    user = _make_user(dbsession, "tagfiltname")
    _make_tag(dbsession, user, "TagFiltNameTag")
    transaction.commit()
    request = _make_request(dbsession, user, params={"name": "TagFiltName"})
    view = TagView(request)
    result = view.all()
    assert result["q"]["name"] == "TagFiltName"


def test_tag_all_category_companies(dbsession):
    user = _make_user(dbsession, "tagcatco")
    tag = _make_tag(dbsession, user, "TagCatCoTag")
    co = _make_company(dbsession, user, "TagCatCoCo")
    tag.companies.append(co)
    transaction.commit()
    request = _make_request(dbsession, user, params={"category": "companies"})
    view = TagView(request)
    result = view.all()
    assert result["q"]["category"] == "companies"


def test_tag_all_category_projects(dbsession):
    user = _make_user(dbsession, "tagcatpj")
    tag = _make_tag(dbsession, user, "TagCatPjTag")
    proj = _make_project(dbsession, user, "TagCatPjProj")
    tag.projects.append(proj)
    transaction.commit()
    request = _make_request(dbsession, user, params={"category": "projects"})
    view = TagView(request)
    result = view.all()
    assert result["q"]["category"] == "projects"


def test_tag_all_order_asc(dbsession):
    user = _make_user(dbsession, "tagascord")
    _make_tag(dbsession, user, "TagAscOrdTag")
    transaction.commit()
    request = _make_request(dbsession, user, params={"order": "asc"})
    view = TagView(request)
    result = view.all()
    assert result["q"]["order"] == "asc"


def test_tag_all_bulk_select(dbsession):
    user = _make_user(dbsession, "tagbulksel")
    _make_tag(dbsession, user, "TagBulkSelTag")
    transaction.commit()
    request = _make_request(
        dbsession, user, method="POST", params={"_select_all": "1", "checked": "1"}
    )
    request.params = MultiDict({"_select_all": "1", "checked": "1"})
    view = TagView(request)
    result = view.all()
    assert result is request.response


def test_tag_count_with_tag(dbsession):
    user = _make_user(dbsession, "tagcount")
    _make_tag(dbsession, user, "TagCountTag")
    transaction.commit()
    request = _make_request(dbsession, user)
    view = TagView(request)
    result = view.count()
    assert isinstance(result, int)


def test_tag_view_with_selection(dbsession):
    user = _make_user(dbsession, "tagviewsel")
    tag = _make_tag(dbsession, user, "TagViewSelTag")
    co = _make_company(dbsession, user, "TagViewSelCo")
    proj = _make_project(dbsession, user, "TagViewSelProj")
    tag.companies.append(co)
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(dbsession, user, tag=tag)
    request.matched_route = MagicMock()
    request.matched_route.name = "tag_view"
    view = TagView(request)
    result = view.view()
    assert "tag" in result
    assert "is_tag_selected" in result
    assert "tag_pills" in result


def test_tag_map_companies_filters_with_data(dbsession):
    user = _make_user(dbsession, "tagmapcofl")
    tag = _make_tag(dbsession, user, "TagMapCoFlTag")
    co = _make_company(dbsession, user, "TagMapCoFlCo")
    co.color = "red"
    tag.companies.append(co)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "color": "red",
            "country": "PL",
            "subdivision": "PL-14",
        },
    )
    view = TagView(request)
    result = view.map_companies()
    assert "q" in result
    assert result["q"]["color"] == "red"


def test_tag_map_projects_status_filters(dbsession):
    import datetime

    user = _make_user(dbsession, "tagmappjst")
    tag = _make_tag(dbsession, user, "TagMapPjStTag")
    proj = _make_project(dbsession, user, "TagMapPjStProj")
    proj.deadline = datetime.datetime.now() + datetime.timedelta(days=10)
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "status": "in_progress",
        },
    )
    view = TagView(request)
    result = view.map_projects()
    assert result["q"]["status"] == "in_progress"


def test_tag_map_projects_completed(dbsession):
    import datetime

    user = _make_user(dbsession, "tagmappjcomp")
    tag = _make_tag(dbsession, user, "TagMapPjCompTag")
    proj = _make_project(dbsession, user, "TagMapPjCompProj")
    proj.deadline = datetime.datetime.now() - datetime.timedelta(days=10)
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "status": "completed",
        },
    )
    view = TagView(request)
    result = view.map_projects()
    assert result["q"]["status"] == "completed"


# --- Cover lines 338, 341: json_companies color and country filters ---


def test_tag_json_companies_color(dbsession):
    user = _make_user(dbsession, "tagjccolor")
    tag = _make_tag(dbsession, user, "TagJcColorTag")
    co = _make_company(dbsession, user, "TagJcColorCo")
    co.color = "red"
    co.latitude = 50.0
    co.longitude = 20.0
    tag.companies.append(co)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(dbsession, user, tag=tag, params={"color": "red"})
    view = TagView(request)
    result = view.json_companies()
    assert isinstance(result, list)


def test_tag_json_companies_country(dbsession):
    user = _make_user(dbsession, "tagjccountry")
    tag = _make_tag(dbsession, user, "TagJcCountryTag")
    co = _make_company(dbsession, user, "TagJcCountryCo")
    co.latitude = 50.0
    co.longitude = 20.0
    tag.companies.append(co)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(dbsession, user, tag=tag, params={"country": "PL"})
    view = TagView(request)
    result = view.json_companies()
    assert isinstance(result, list)


def test_tag_json_companies_bbox_with_location(dbsession):
    user = _make_user(dbsession, "tagjcbbox")
    tag = _make_tag(dbsession, user, "TagJcBboxTag")
    co = _make_company(dbsession, user, "TagJcBboxCo")
    co.latitude = 50.0
    co.longitude = 20.0
    tag.companies.append(co)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "north": "51",
            "south": "49",
            "east": "21",
            "west": "19",
        },
    )
    view = TagView(request)
    result = view.json_companies()
    assert isinstance(result, list)


def test_tag_json_projects_bbox_valid(dbsession):
    user = _make_user(dbsession, "tagjpbbox")
    tag = _make_tag(dbsession, user, "TagJpBboxTag")
    proj = _make_project(dbsession, user, "TagJpBboxProj")
    proj.latitude = 50.0
    proj.longitude = 20.0
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "north": "51",
            "south": "49",
            "east": "21",
            "west": "19",
        },
    )
    view = TagView(request)
    result = view.json_projects()
    assert isinstance(result, list)


def test_tag_export_companies_stars_asc(dbsession):
    user = _make_user(dbsession, "tagecstarasc")
    tag = _make_tag(dbsession, user, "TagEcStarAscTag")
    co = _make_company(dbsession, user, "TagEcStarAscCo")
    tag.companies.append(co)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "sort": "stars",
            "order": "asc",
        },
    )
    view = TagView(request)
    result = view.export_companies()
    assert result is not None


def test_tag_export_companies_stars_desc(dbsession):
    user = _make_user(dbsession, "tagecstardesc")
    tag = _make_tag(dbsession, user, "TagEcStarDescTag")
    co = _make_company(dbsession, user, "TagEcStarDescCo")
    tag.companies.append(co)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "sort": "stars",
            "order": "desc",
        },
    )
    view = TagView(request)
    result = view.export_companies()
    assert result is not None


def test_tag_export_companies_name_desc(dbsession):
    user = _make_user(dbsession, "tagecnmdesc")
    tag = _make_tag(dbsession, user, "TagEcNmDescTag")
    co = _make_company(dbsession, user, "TagEcNmDescCo")
    tag.companies.append(co)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "sort": "name",
            "order": "desc",
        },
    )
    view = TagView(request)
    result = view.export_companies()
    assert result is not None


def test_tag_projects_stars_asc(dbsession):
    user = _make_user(dbsession, "tagpjstarasc")
    tag = _make_tag(dbsession, user, "TagPjStarAscTag")
    proj = _make_project(dbsession, user, "TagPjStarAscProj")
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "sort": "stars",
            "order": "asc",
        },
    )
    view = TagView(request)
    result = view.projects()
    assert "paginator" in result


def test_tag_projects_comments_asc(dbsession):
    from marker.models.comment import Comment

    user = _make_user(dbsession, "tagpjcmtasc")
    tag = _make_tag(dbsession, user, "TagPjCmtAscTag")
    proj = _make_project(dbsession, user, "TagPjCmtAscProj")
    cmt = Comment(comment="c")
    cmt.created_by = user
    proj.comments.append(cmt)
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "sort": "comments",
            "order": "asc",
        },
    )
    view = TagView(request)
    result = view.projects()
    assert "paginator" in result


def test_tag_export_projects_stars_asc(dbsession):
    user = _make_user(dbsession, "tagepstarasc")
    tag = _make_tag(dbsession, user, "TagEpStarAscTag")
    proj = _make_project(dbsession, user, "TagEpStarAscProj")
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "sort": "stars",
            "order": "asc",
        },
    )
    view = TagView(request)
    result = view.export_projects()
    assert result is not None


def test_tag_export_projects_stars_desc(dbsession):
    user = _make_user(dbsession, "tagepstardesc")
    tag = _make_tag(dbsession, user, "TagEpStarDescTag")
    proj = _make_project(dbsession, user, "TagEpStarDescProj")
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "sort": "stars",
            "order": "desc",
        },
    )
    view = TagView(request)
    result = view.export_projects()
    assert result is not None


def test_tag_export_projects_name_desc(dbsession):
    user = _make_user(dbsession, "tagepnmdesc")
    tag = _make_tag(dbsession, user, "TagEpNmDescTag")
    proj = _make_project(dbsession, user, "TagEpNmDescProj")
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "sort": "name",
            "order": "desc",
        },
    )
    view = TagView(request)
    result = view.export_projects()
    assert result is not None


def test_tag_map_projects_stage_delivery(dbsession):
    user = _make_user(dbsession, "tagmappjstdm")
    tag = _make_tag(dbsession, user, "TagMapPjStDmTag")
    proj = _make_project(dbsession, user, "TagMapPjStDmProj")
    proj.stage = "design"
    proj.delivery_method = "general_contractor"
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "stage": "design",
            "delivery_method": "general_contractor",
        },
    )
    view = TagView(request)
    result = view.map_projects()
    assert result["q"]["stage"] == "design"
    assert result["q"]["delivery_method"] == "general_contractor"


def test_tag_json_companies_bbox_with_company(dbsession):
    user = _make_user(dbsession, "tagjsoncobbox")
    tag = _make_tag(dbsession, user, "TagJsonCoBboxTag")
    co = _make_company(dbsession, user, "TagJsonCoBboxCo")
    co.latitude = 50.0
    co.longitude = 20.0
    tag.companies.append(co)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "north": "51",
            "south": "49",
            "east": "21",
            "west": "19",
        },
    )
    view = TagView(request)
    result = view.json_companies()
    assert isinstance(result, list)


def test_tag_json_companies_subdivision(dbsession):
    user = _make_user(dbsession, "tagjsoncosd")
    tag = _make_tag(dbsession, user, "TagJsonCoSdTag")
    co = _make_company(dbsession, user, "TagJsonCoSdCo")
    co.latitude = 50.0
    co.longitude = 20.0
    tag.companies.append(co)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "subdivision": "PL-14",
        },
    )
    view = TagView(request)
    result = view.json_companies()
    assert isinstance(result, list)


def test_tag_map_projects_subdivision(dbsession):
    user = _make_user(dbsession, "tagmappjsub")
    tag = _make_tag(dbsession, user, "TagMapPjSubTag")
    proj = _make_project(dbsession, user, "TagMapPjSubProj")
    proj.latitude = 50.0
    proj.longitude = 20.0
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "subdivision": "PL-14",
        },
    )
    view = TagView(request)
    result = view.map_projects()
    assert "q" in result


def test_tag_json_projects_subdivision(dbsession):
    user = _make_user(dbsession, "tagjsonpjsub")
    tag = _make_tag(dbsession, user, "TagJsonPjSubTag")
    proj = _make_project(dbsession, user, "TagJsonPjSubProj")
    proj.latitude = 50.0
    proj.longitude = 20.0
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "subdivision": "PL-14",
        },
    )
    view = TagView(request)
    result = view.json_projects()
    assert isinstance(result, list)


def test_tag_json_projects_bbox(dbsession):
    user = _make_user(dbsession, "tagjsonpjbbox")
    tag = _make_tag(dbsession, user, "TagJsonPjBboxTag")
    proj = _make_project(dbsession, user, "TagJsonPjBboxProj")
    proj.latitude = 50.0
    proj.longitude = 20.0
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "north": "51",
            "south": "49",
            "east": "21",
            "west": "19",
        },
    )
    view = TagView(request)
    result = view.json_projects()
    assert isinstance(result, list)


def test_tag_companies_bulk_select(dbsession):
    user = _make_user(dbsession, "tagcobulk")
    tag = _make_tag(dbsession, user, "TagCoBulkTag")
    co = _make_company(dbsession, user, "TagCoBulkCo")
    tag.companies.append(co)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        method="POST",
        params={
            "_select_all": "1",
            "checked": "1",
        },
    )
    view = TagView(request)
    result = view.companies()
    assert result is request.response


def test_tag_projects_subdivision(dbsession):
    user = _make_user(dbsession, "tagpjsub")
    tag = _make_tag(dbsession, user, "TagPjSubTag")
    proj = _make_project(dbsession, user, "TagPjSubProj")
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "subdivision": "PL-14",
        },
    )
    view = TagView(request)
    result = view.projects()
    assert "q" in result


def test_tag_projects_delivery_method(dbsession):
    user = _make_user(dbsession, "tagpjdm")
    tag = _make_tag(dbsession, user, "TagPjDmTag")
    proj = _make_project(dbsession, user, "TagPjDmProj")
    proj.delivery_method = "general_contractor"
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "delivery_method": "general_contractor",
        },
    )
    view = TagView(request)
    result = view.projects()
    assert result["q"]["delivery_method"] == "general_contractor"


def test_tag_projects_bulk_select(dbsession):
    user = _make_user(dbsession, "tagpjbulk")
    tag = _make_tag(dbsession, user, "TagPjBulkTag")
    proj = _make_project(dbsession, user, "TagPjBulkProj")
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        method="POST",
        params={
            "_select_all": "1",
            "checked": "1",
        },
    )
    view = TagView(request)
    result = view.projects()
    assert result is request.response


def test_tag_json_projects_bbox_invalid(dbsession):
    """Cover lines 432-433: json_projects bbox with invalid coords (except handler)."""
    user = _make_user(dbsession, "tagjpbboxinv")
    tag = _make_tag(dbsession, user, "TagJpBboxInvTag")
    proj = _make_project(dbsession, user, "TagJpBboxInvProj")
    proj.latitude = 50.0
    proj.longitude = 20.0
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "north": "abc",
            "south": "49",
            "east": "21",
            "west": "19",
        },
    )
    view = TagView(request)
    result = view.json_projects()
    assert isinstance(result, list)


def test_tag_export_companies_name_asc(dbsession):
    """Cover line 620: export_companies non-stars sort asc."""
    user = _make_user(dbsession, "tagecnmasc")
    tag = _make_tag(dbsession, user, "TagEcNmAscTag")
    co = _make_company(dbsession, user, "TagEcNmAscCo")
    tag.companies.append(co)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "sort": "name",
            "order": "asc",
        },
    )
    view = TagView(request)
    result = view.export_companies()
    assert result is not None


def test_tag_export_projects_name_asc(dbsession):
    """Cover line 835: export_projects non-stars sort asc."""
    user = _make_user(dbsession, "tagepnmasc")
    tag = _make_tag(dbsession, user, "TagEpNmAscTag")
    proj = _make_project(dbsession, user, "TagEpNmAscProj")
    tag.projects.append(proj)
    tag_id = tag.id
    transaction.commit()
    tag = dbsession.get(Tag, tag_id)
    request = _make_request(
        dbsession,
        user,
        tag=tag,
        params={
            "sort": "name",
            "order": "asc",
        },
    )
    view = TagView(request)
    result = view.export_projects()
    assert result is not None


# ===========================================================================
# Date range filtering tests
# ===========================================================================


def test_tag_all_date_from(dbsession):
    user = _make_user(dbsession, "tagdtf1")
    _make_tag(dbsession, user, "DtFromTag")
    transaction.commit()
    request = _make_request(dbsession, user, params={"date_from": "2020-01-01T00:00"})
    view = TagView(request)
    result = view.all()
    assert result["q"]["date_from"] == "2020-01-01T00:00"
    assert result["counter"] >= 1


def test_tag_all_date_to(dbsession):
    user = _make_user(dbsession, "tagdtt1")
    _make_tag(dbsession, user, "DtToTag")
    transaction.commit()
    request = _make_request(dbsession, user, params={"date_to": "2030-01-01T00:00"})
    view = TagView(request)
    result = view.all()
    assert result["q"]["date_to"] == "2030-01-01T00:00"
    assert result["counter"] >= 1


def test_tag_all_date_range(dbsession):
    user = _make_user(dbsession, "tagdtr1")
    _make_tag(dbsession, user, "DtRangeTag")
    transaction.commit()
    request = _make_request(
        dbsession,
        user,
        params={"date_from": "2020-01-01T00:00", "date_to": "2030-01-01T00:00"},
    )
    view = TagView(request)
    result = view.all()
    assert result["q"]["date_from"] == "2020-01-01T00:00"
    assert result["q"]["date_to"] == "2030-01-01T00:00"
    assert result["counter"] >= 1


def test_tag_companies_date_from(dbsession):
    user = _make_user(dbsession, "tagcodf")
    tag = _make_tag(dbsession, user, "CoDfTag")
    company = _make_company(dbsession, user, "CoDfCo")
    tag.companies.append(company)
    transaction.commit()
    request = _make_request(
        dbsession, user, tag=tag, params={"date_from": "2020-01-01T00:00"}
    )
    view = TagView(request)
    result = view.companies()
    assert result["q"]["date_from"] == "2020-01-01T00:00"


def test_tag_companies_date_to(dbsession):
    user = _make_user(dbsession, "tagcodt")
    tag = _make_tag(dbsession, user, "CoDtTag")
    company = _make_company(dbsession, user, "CoDtCo")
    tag.companies.append(company)
    transaction.commit()
    request = _make_request(
        dbsession, user, tag=tag, params={"date_to": "2030-01-01T00:00"}
    )
    view = TagView(request)
    result = view.companies()
    assert result["q"]["date_to"] == "2030-01-01T00:00"


def test_tag_projects_date_from(dbsession):
    user = _make_user(dbsession, "tagprdf")
    tag = _make_tag(dbsession, user, "PrDfTag")
    proj = _make_project(dbsession, user, "PrDfProj")
    tag.projects.append(proj)
    transaction.commit()
    request = _make_request(
        dbsession, user, tag=tag, params={"date_from": "2020-01-01T00:00"}
    )
    view = TagView(request)
    result = view.projects()
    assert result["q"]["date_from"] == "2020-01-01T00:00"


def test_tag_projects_date_to(dbsession):
    user = _make_user(dbsession, "tagprdt")
    tag = _make_tag(dbsession, user, "PrDtTag")
    proj = _make_project(dbsession, user, "PrDtProj")
    tag.projects.append(proj)
    transaction.commit()
    request = _make_request(
        dbsession, user, tag=tag, params={"date_to": "2030-01-01T00:00"}
    )
    view = TagView(request)
    result = view.projects()
    assert result["q"]["date_to"] == "2030-01-01T00:00"
