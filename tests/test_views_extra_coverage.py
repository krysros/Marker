import transaction
from unittest.mock import MagicMock
import time

from pyramid.httpexceptions import HTTPSeeOther
from webob.multidict import MultiDict

from marker.models.company import Company
from marker.models.project import Project
from marker.models.tag import Tag
from marker.models.user import User
from marker.models.contact import Contact
from marker.models.association import (
    selected_companies,
    selected_projects,
    selected_contacts,
    selected_tags,
    companies_stars,
    projects_stars,
    Activity,
)


from marker.views.company import CompanyView
from marker.views.project import ProjectView
from marker.views.tag import TagView, TagAISearchCache
from marker.views.user import UserView

from tests.conftest import DummyRequestWithIdentity

# --- Database helpers ---


def _make_user(dbsession, name="extrauser"):
    user = User(
        name=name, fullname="E U", email=f"{name}@e.com", role="admin", password="pw"
    )
    dbsession.add(user)
    dbsession.flush()
    return user


def _make_tag(dbsession, user, name="ExtraTag"):
    tag = Tag(name=name)
    tag.created_by = user
    dbsession.add(tag)
    dbsession.flush()
    return tag


def _make_company(dbsession, user, name="ExtraCo"):
    company = Company(
        name=name,
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="http://extraco.com",
        color="red",
        NIP="",
        REGON="",
        KRS="",
    )
    company.created_by = user
    dbsession.add(company)
    dbsession.flush()
    return company


def _make_project(dbsession, user, name="ExtraProj"):
    project = Project(
        name=name,
        street="S",
        postcode="00-000",
        city="C",
        subdivision="PL-14",
        country="PL",
        website="http://extraproj.com",
        color="green",
        deadline=None,
        stage="",
        delivery_method="",
    )
    project.created_by = user
    dbsession.add(project)
    dbsession.flush()
    return project


def _make_contact(dbsession, user, company=None, project=None, name="ExtraContact"):
    contact = Contact(
        name=name,
        role="Manager",
        phone="12345",
        email="extra@contact.com",
        color="blue",
    )
    contact.created_by = user
    if company:
        contact.company = company
    if project:
        contact.project = project
    dbsession.add(contact)
    dbsession.flush()
    return contact


def _make_request(dbsession, user, method="GET", params=None, post=None):
    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.method = method
    request.GET = MultiDict(params or {})
    request.POST = MultiDict(post or {})
    request.params = MultiDict(params or {})
    request.locale_name = "en"
    request.translate = lambda x: x
    request.route_url = lambda route_name, *a, **kw: f"/{route_name}"
    request.session = MagicMock()
    request.response = MagicMock()
    request.response.headers = {}
    request.context = MagicMock()
    request.context.user = user
    request.environ = {}
    request.environ["webob._parsed_get_vars"] = (MultiDict(), MultiDict())
    request.environ["webob._parsed_post_vars"] = (MultiDict(post or {}), MultiDict())
    request.environ["webob._parsed_params_vars"] = (
        MultiDict(params or {}),
        MultiDict(),
    )
    request.path_qs = "/"
    return request


# --- Component 5 Tests ---


def test_company_and_project_count(dbsession):
    user = _make_user(dbsession, "cntu")
    _make_company(dbsession, user, "Co1")
    _make_company(dbsession, user, "Co2")
    _make_project(dbsession, user, "Pr1")
    transaction.commit()

    req1 = _make_request(dbsession, user)
    v1 = CompanyView(req1)
    assert v1.count() == 2

    req2 = _make_request(dbsession, user)
    v2 = ProjectView(req2)
    assert v2.count() == 1


def test_company_add_ai_exceptions_logging(monkeypatch, dbsession):
    user = _make_user(dbsession, "aiu")
    transaction.commit()

    req = _make_request(
        dbsession, user, method="POST", post={"website": "http://test-ai.com"}
    )
    monkeypatch.setattr(
        "marker.views.company.company_autofill_from_website",
        lambda *a, **kw: {
            "name": "New Company From Website",
            "street": "Main Street",
            "postcode": "12-345",
            "city": "Warsaw",
            "country": "PL",
        },
    )

    def raising_location_details(*a, **kw):
        raise RuntimeError("Simulated geocode failure")

    monkeypatch.setattr(
        "marker.views.company.location_details", raising_location_details
    )

    original_execute = dbsession.execute

    def mock_execute(statement, *args, **kwargs):
        if "from tag" in str(statement).lower() or "tag.name" in str(statement).lower():
            raise RuntimeError("DB failed tag query")
        return original_execute(statement, *args, **kwargs)

    monkeypatch.setattr(dbsession, "execute", mock_execute)

    view = CompanyView(req)
    result = view.add_ai()
    assert isinstance(result, HTTPSeeOther)


def test_project_add_ai_exceptions_logging(monkeypatch, dbsession):
    user = _make_user(dbsession, "paiu")
    transaction.commit()

    req = _make_request(
        dbsession, user, method="POST", post={"website": "http://test-ai-proj.com"}
    )
    monkeypatch.setattr(
        "marker.views.project.project_autofill_from_website",
        lambda *a, **kw: {
            "name": "New Project From Website",
            "street": "Main Street",
            "postcode": "12-345",
            "city": "Warsaw",
            "country": "PL",
        },
    )
    monkeypatch.setattr("marker.views.project.ProjectForm.validate", lambda self: True)

    def raising_location_details(*a, **kw):

        raise RuntimeError("Simulated geocode failure")

    monkeypatch.setattr(
        "marker.views.project.location_details", raising_location_details
    )

    original_execute = dbsession.execute

    def mock_execute(statement, *args, **kwargs):
        if "from tag" in str(statement).lower() or "tag.name" in str(statement).lower():
            raise RuntimeError("DB failed tag query")
        return original_execute(statement, *args, **kwargs)

    monkeypatch.setattr(dbsession, "execute", mock_execute)

    view = ProjectView(req)
    result = view.add_ai()
    assert isinstance(result, HTTPSeeOther)


# --- Component 6 Tests ---


def test_tag_ai_search_cache_ttl_and_eviction():
    cache = TagAISearchCache(max_size=2, ttl_seconds=1)
    cache.set(1, "query1", [101])
    cache.set(1, "query2", [102])
    cache.set(1, "query3", [103])
    assert cache.get(1, "query1") is None
    assert cache.get(1, "query2") == [102]

    cache.cache[(1, "query2")] = ([102], time.time() - 10)
    assert cache.get(1, "query2") is None

    cache.cache[(1, "query3")] = ([103], time.time() - 10)
    cache.cache[(1, "expired_a")] = ([1], time.time() - 1)
    cache.cache[(1, "expired_b")] = ([2], time.time() - 1)
    cache._cleanup()
    assert len(cache.cache) == 0


def test_match_tags_ai_model_config_exception(monkeypatch):
    monkeypatch.setattr(
        "marker.views.tag.get_configured_model",
        lambda: exec('raise ValueError("not set")'),
    )
    req = DummyRequestWithIdentity()
    req.translate = lambda x: x
    view = TagView(req)
    res = view._match_tags_ai("some-query", ["TagA"])
    assert res == []


def test_match_tags_ai_invalid_retries(monkeypatch):
    req = DummyRequestWithIdentity()
    req.registry = MagicMock()
    req.registry.settings = {"gemini.retries": "invalid-int"}
    monkeypatch.setattr("marker.views.tag.get_configured_model", lambda: "test-model")
    monkeypatch.setenv("GEMINI_API_KEY", "some-key")

    view = TagView(req)
    called_retries = []

    def mock_invoke_text(prompt, model, *, fallback_model=None, retries=2, source=""):
        called_retries.append(retries)
        return "[]"

    monkeypatch.setattr("marker.views.tag.invoke_text", mock_invoke_text)

    view._match_tags_ai("some-query", ["TagA"])
    assert called_retries[0] == 2


def test_match_tags_ai_missing_api_key(monkeypatch):
    req = DummyRequestWithIdentity()
    monkeypatch.setattr("marker.views.tag.get_configured_model", lambda: "test-model")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    view = TagView(req)
    res = view._match_tags_ai("some-query", ["TagA"])
    assert res == []


def test_match_tags_ai_two_stage_exceptions(monkeypatch):
    req = DummyRequestWithIdentity()
    monkeypatch.setattr("marker.views.tag.get_configured_model", lambda: "test-model")
    monkeypatch.setenv("GEMINI_API_KEY", "some-key")

    def raising_invoke_text(*a, **kw):
        raise RuntimeError("simulated kw fail")

    monkeypatch.setattr("marker.views.tag.invoke_text", raising_invoke_text)

    view = TagView(req)
    tags = [f"Tag{i}" for i in range(160)]
    res = view._match_tags_ai("query", tags)
    assert res == []

    def empty_kw_invoke_text(
        prompt, model, *, fallback_model=None, retries=2, source=""
    ):
        if source == "tag_search_ai_keywords":
            return "[]"
        return "[]"

    monkeypatch.setattr("marker.views.tag.invoke_text", empty_kw_invoke_text)

    res2 = view._match_tags_ai("query", tags)
    assert res2 == []


def test_match_tags_ai_final_matching_exception(monkeypatch):
    req = DummyRequestWithIdentity()
    monkeypatch.setattr("marker.views.tag.get_configured_model", lambda: "test-model")
    monkeypatch.setenv("GEMINI_API_KEY", "some-key")

    def bad_json_invoke_text(*a, **kw):
        return "invalid-json"

    monkeypatch.setattr("marker.views.tag.invoke_text", bad_json_invoke_text)

    view = TagView(req)
    res = view._match_tags_ai("query", ["TagA"])
    assert res == []


def test_tag_all_with_ai_query(monkeypatch, dbsession):
    user = _make_user(dbsession, "tagaiu")
    _make_tag(dbsession, user, "AITag")
    transaction.commit()

    req1 = _make_request(dbsession, user, params={"ai_query": "AITag"})
    view1 = TagView(req1)
    monkeypatch.setattr(view1, "_match_tags_ai", lambda q, t: ["AITag"])
    res1 = view1.all()
    assert len(res1["paginator"]) == 1
    assert res1["paginator"][0].name == "AITag"

    req2 = _make_request(dbsession, user, params={"ai_query": "AITag"})
    view2 = TagView(req2)
    called_match = False

    def mock_match(q, t):
        nonlocal called_match
        called_match = True
        return []

    monkeypatch.setattr(view2, "_match_tags_ai", mock_match)
    res2 = view2.all()
    assert len(res2["paginator"]) == 1
    assert not called_match


def test_tag_search_ai_get(dbsession):
    user = _make_user(dbsession, "taggetu")
    transaction.commit()

    req = _make_request(dbsession, user, method="GET")
    view = TagView(req)
    res = view.search_ai()
    assert res["heading"] == "Search tags with AI"


# --- Component 7 Tests ---


def test_user_selected_views_and_counts(dbsession):
    user = _make_user(dbsession, "selecteduser")
    tag = _make_tag(dbsession, user, "SelectedTag")
    company = _make_company(dbsession, user, "SelectedCompany")
    project = _make_project(dbsession, user, "SelectedProject")
    contact = _make_contact(
        dbsession, user, company=company, project=project, name="SelectedContact"
    )

    # Associate tags
    company.tags.append(tag)
    project.tags.append(tag)

    # Link company and project with an Activity
    activity = Activity(company_id=company.id, project_id=project.id)
    dbsession.add(activity)

    # Add selections
    dbsession.execute(
        selected_companies.insert().values(user_id=user.id, company_id=company.id)
    )
    dbsession.execute(
        selected_projects.insert().values(user_id=user.id, project_id=project.id)
    )
    dbsession.execute(
        selected_contacts.insert().values(user_id=user.id, contact_id=contact.id)
    )
    dbsession.execute(selected_tags.insert().values(user_id=user.id, tag_id=tag.id))
    dbsession.execute(
        companies_stars.insert().values(user_id=user.id, company_id=company.id)
    )
    dbsession.execute(
        projects_stars.insert().values(user_id=user.id, project_id=project.id)
    )

    transaction.commit()

    # 1. Test selected tags views (selected_companies_tags, selected_projects_tags, selected_contacts_tags)
    req = _make_request(dbsession, user)
    view = UserView(req)

    # selected_companies_tags
    res_co_tags = view.selected_companies_tags()
    assert len(res_co_tags["paginator"]) == 1
    assert res_co_tags["paginator"][0].name == "SelectedTag"

    # selected_projects_tags
    res_pr_tags = view.selected_projects_tags()
    assert len(res_pr_tags["paginator"]) == 1
    assert res_pr_tags["paginator"][0].name == "SelectedTag"

    # selected_contacts_tags
    res_con_tags = view.selected_contacts_tags()
    assert len(res_con_tags["paginator"]) == 1
    assert res_con_tags["paginator"][0].name == "SelectedTag"

    # 2. Test selected projects/companies cross views (selected_companies_projects, selected_projects_companies)
    # selected_companies_projects
    res_co_projects = view.selected_companies_projects()
    assert len(res_co_projects["paginator"]) == 1
    assert res_co_projects["paginator"][0].name == "SelectedProject"

    # selected_projects_companies
    res_pr_companies = view.selected_projects_companies()
    assert len(res_pr_companies["paginator"]) == 1
    assert res_pr_companies["paginator"][0].name == "SelectedCompany"

    # 3. Test counts (lines 6212-6288)
    assert view.selected_companies_count() == 1
    assert view.selected_projects_count() == 1
    assert view.selected_tags_count() == 1
    assert view.selected_contacts_count() == 1
    assert view.companies_stars_count() == 1
    assert view.projects_stars_count() == 1


def test_tag_ai_search_cache_direct_expiry_branch(monkeypatch):
    import time
    from marker.views.tag import TagAISearchCache

    cache = TagAISearchCache(max_size=10, ttl_seconds=10)

    times = [1000.0, 1005.0]

    def mock_time():
        if times:
            return times.pop(0)
        return 1005.0

    monkeypatch.setattr(time, "time", mock_time)

    # Directly set a key with absolute expiry = 1002.0
    cache.cache[(1, "expired_test")] = ([999], 1002.0)

    # Retrieve it. Since 1005.0 > 1002.0, it will execute line 77: del self.cache[key]
    val = cache.get(1, "expired_test")
    assert val is None
    assert (1, "expired_test") not in cache.cache


def test_user_selected_views_parameter_combinations_and_filters(dbsession, monkeypatch):
    user = _make_user(dbsession, "paramuser")
    tag = _make_tag(dbsession, user, "ParamTag")
    company = _make_company(dbsession, user, "ParamCompany")
    project = _make_project(dbsession, user, "ParamProject")

    # Associate tag
    company.tags.append(tag)
    project.tags.append(tag)

    # Link company and project with an Activity
    activity = Activity(company_id=company.id, project_id=project.id)
    dbsession.add(activity)

    # Add selections
    dbsession.execute(
        selected_companies.insert().values(user_id=user.id, company_id=company.id)
    )
    dbsession.execute(
        selected_projects.insert().values(user_id=user.id, project_id=project.id)
    )
    dbsession.execute(selected_tags.insert().values(user_id=user.id, tag_id=tag.id))

    transaction.commit()

    # 1. Test invalid sort and order fallback, plus category parameter
    req = _make_request(
        dbsession,
        user,
        params={
            "sort": "invalid_sort_name",
            "order": "invalid_order_dir",
            "category": "companies",
        },
    )
    view = UserView(req)

    res1 = view.selected_companies_tags()
    assert len(res1["paginator"]) == 1

    res2 = view.selected_projects_tags()
    assert len(res2["paginator"]) == 1

    res3 = view.selected_contacts_tags()
    assert (
        len(res3["paginator"]) == 0
    )  # No selected contacts tags because no selected contacts exist

    # 2. Test bulk select request branches (using is_bulk_select_request monkeypatch)
    monkeypatch.setattr("marker.views.user.is_bulk_select_request", lambda req: True)
    # Mock handle_bulk_selection to avoid DB issues
    monkeypatch.setattr(
        "marker.views.user.handle_bulk_selection", lambda *a: "bulk_result"
    )

    assert view.selected_companies_tags() == "bulk_result"
    assert view.selected_projects_tags() == "bulk_result"
    assert view.selected_contacts_tags() == "bulk_result"
    assert view.selected_companies_projects() == "bulk_result"
    assert view.selected_projects_companies() == "bulk_result"

    # Restore standard bulk select
    monkeypatch.setattr("marker.views.user.is_bulk_select_request", lambda req: False)

    # 3. Test selected projects filters (status in_progress, status completed, color, country, subdivision, stage, delivery_method, object_category, asc/desc order)
    # Set up some filters that will be applied to the query
    project.stage = "concept"
    project.delivery_method = "general_contractor"
    project.object_category = "residential"
    dbsession.flush()

    req_proj_filters = _make_request(
        dbsession,
        user,
        params={
            "status": "in_progress",
            "color": "green",
            "country": "PL",
            "subdivision": "PL-14",
            "stage": "concept",
            "delivery_method": "general_contractor",
            "object_category": "residential",
            "sort": "name",
            "order": "asc",
        },
    )
    view_proj = UserView(req_proj_filters)
    # Set project deadline to future to match status "in_progress"
    import datetime

    project.deadline = datetime.datetime.now() + datetime.timedelta(days=10)
    dbsession.flush()

    res_proj = view_proj.selected_companies_projects()
    assert len(res_proj["paginator"]) == 1

    # Try completed status and other order direction
    req_proj_filters2 = _make_request(
        dbsession,
        user,
        params={
            "status": "completed",
            "order": "desc",
        },
    )
    # Set project deadline to past to match status "completed"
    project.deadline = datetime.datetime.now() - datetime.timedelta(days=10)
    dbsession.flush()
    res_proj2 = UserView(req_proj_filters2).selected_companies_projects()
    assert len(res_proj2["paginator"]) == 1

    # 4. Test selected companies filters (color, country, subdivision, asc/desc order)
    req_co_filters = _make_request(
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
    view_co = UserView(req_co_filters)
    res_co = view_co.selected_projects_companies()
    assert len(res_co["paginator"]) == 1
