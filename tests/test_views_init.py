"""Tests for marker/views/__init__.py"""

from types import SimpleNamespace
from unittest.mock import MagicMock

from pyramid.testing import DummyRequest

from marker.views import (
    _coerce_bulk_checked,
    htmx_refresh_response,
    normalize_ci_value,
    safe_redirect_target,
    update_selected_items,
)


def test_safe_redirect_target_empty():
    request = DummyRequest()
    request.host_url = "http://localhost"
    assert safe_redirect_target(request, "", "/fallback") == "/fallback"
    assert safe_redirect_target(request, None, "/fallback") == "/fallback"


def test_safe_redirect_target_valid_local():
    request = DummyRequest()
    request.host_url = "http://localhost"
    assert safe_redirect_target(request, "/home", "/fallback") == "/home"


def test_safe_redirect_target_double_slash():
    request = DummyRequest()
    request.host_url = "http://localhost"
    assert safe_redirect_target(request, "//evil.com", "/fallback") == "/fallback"


def test_safe_redirect_target_relative_path():
    request = DummyRequest()
    request.host_url = "http://localhost"
    assert safe_redirect_target(request, "relative", "/fallback") == "/fallback"


def test_safe_redirect_target_external_url():
    request = DummyRequest()
    request.host_url = "http://localhost"
    assert (
        safe_redirect_target(request, "http://evil.com/path", "/fallback")
        == "/fallback"
    )


def test_safe_redirect_target_same_origin():
    request = DummyRequest()
    request.host_url = "http://localhost"
    result = safe_redirect_target(request, "http://localhost/path", "/fallback")
    assert result == "http://localhost/path"


def test_safe_redirect_target_different_scheme():
    request = DummyRequest()
    request.host_url = "https://localhost"
    result = safe_redirect_target(request, "http://localhost/path", "/fallback")
    assert result == "/fallback"


def test_safe_redirect_target_ftp_scheme():
    request = DummyRequest()
    request.host_url = "http://localhost"
    result = safe_redirect_target(request, "ftp://localhost/path", "/fallback")
    assert result == "/fallback"


def test_normalize_ci_value():
    assert normalize_ci_value("ABC") == "abc"
    assert normalize_ci_value("ĄĆĘ") == "ąćę"
    assert normalize_ci_value("ŁÓŚŹ") == "łóśź"


def test_update_selected_items_add():
    selected = []
    items = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
    update_selected_items(selected, items, checked=True)
    assert len(selected) == 2


def test_update_selected_items_remove():
    item = SimpleNamespace(id=1)
    selected = [item, SimpleNamespace(id=2)]
    update_selected_items(selected, [item], checked=False)
    assert len(selected) == 1
    assert selected[0].id == 2


def test_update_selected_items_empty():
    selected = []
    update_selected_items(selected, [], checked=True)
    assert len(selected) == 0


def test_update_selected_items_none_id():
    selected = []
    items = [SimpleNamespace(id=None)]
    update_selected_items(selected, items, checked=True)
    assert len(selected) == 0


def test_update_selected_items_no_duplicate():
    item = SimpleNamespace(id=1)
    selected = [item]
    update_selected_items(selected, [SimpleNamespace(id=1)], checked=True)
    assert len(selected) == 1


def test_coerce_bulk_checked_true():
    request = DummyRequest()
    request.params = {"checked": "1"}
    request.session = {}
    request.path_qs = "/test"
    assert _coerce_bulk_checked(request) is True


def test_coerce_bulk_checked_false():
    request = DummyRequest()
    request.params = {"checked": "0"}
    request.session = {}
    request.path_qs = "/test"
    assert _coerce_bulk_checked(request) is False


def test_coerce_bulk_checked_yes():
    request = DummyRequest()
    request.params = {"checked": "yes"}
    request.session = {}
    request.path_qs = "/test"
    assert _coerce_bulk_checked(request) is True


def test_coerce_bulk_checked_bool():
    request = DummyRequest()
    request.params = {"checked": True}
    request.session = {}
    request.path_qs = "/test"
    assert _coerce_bulk_checked(request) is True

    request = DummyRequest()
    request.params = {}
    request.session = {"select_all_states": {"/test": True}}
    request.path_qs = "/test"
    # In new logic, default is always True if 'checked' is not provided
    assert _coerce_bulk_checked(request) is True


def test_coerce_bulk_checked_bool_false():
    request = DummyRequest()
    request.params = {"checked": False}
    request.session = {}
    request.path_qs = "/test"
    assert _coerce_bulk_checked(request) is False


def test_resolve_selection_target_none():
    """_resolve_selection_target returns None for plain list."""
    from marker.views import _resolve_selection_target

    assert _resolve_selection_target([]) is None


def test_toggle_selected_item_none_id():
    from marker.views import toggle_selected_item

    request = MagicMock()
    result = toggle_selected_item(request, MagicMock(), MagicMock(), None)
    assert result is False


def test_toggle_selected_item_deselect(dbsession):
    """toggle_selected_item removes an existing selection."""
    import transaction

    from marker.models import Company, User, selected_companies
    from marker.views import toggle_selected_item

    user = User(
        name="toguser", fullname="Tog", email="tog@e.com", role="admin", password="pw"
    )
    dbsession.add(user)
    dbsession.flush()
    co = Company(
        name="TogCo",
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
    user.selected_companies.append(co)
    transaction.commit()

    user = dbsession.execute(
        __import__("sqlalchemy").select(User).filter(User.name == "toguser")
    ).scalar_one()
    co = dbsession.execute(
        __import__("sqlalchemy").select(Company).filter(Company.name == "TogCo")
    ).scalar_one()

    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    result = toggle_selected_item(
        request, selected_companies, selected_companies.c.company_id, co.id
    )
    assert result is False


def test_apply_bulk_selection_deselect(dbsession):
    """apply_bulk_selection handles unchecked (deselect) path."""
    import transaction
    from sqlalchemy import select as sa_select

    from marker.models import Company, User, selected_companies
    from marker.views import apply_bulk_selection

    user = User(
        name="bulkdel", fullname="BD", email="bd@e.com", role="admin", password="pw"
    )
    dbsession.add(user)
    dbsession.flush()
    co = Company(
        name="BulkDelCo",
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
    user.selected_companies.append(co)
    transaction.commit()

    user = dbsession.execute(
        sa_select(User).filter(User.name == "bulkdel")
    ).scalar_one()

    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.params = {"checked": "0"}
    request.session = {}
    request.path_qs = "/test"

    stmt = sa_select(Company).filter(Company.created_by == user)
    apply_bulk_selection(request, stmt, user.selected_companies)
    # After deselect, should have 0 selected
    remaining = dbsession.execute(
        sa_select(selected_companies).where(selected_companies.c.user_id == user.id)
    ).all()
    assert len(remaining) == 0


def test_coerce_bulk_checked_toggle_default_false():
    request = DummyRequest()
    request.params = {}
    request.session = {}
    request.path_qs = "/test"
    assert _coerce_bulk_checked(request) is True


def test_htmx_refresh_response():
    request = DummyRequest()
    request.response = MagicMock()
    request.response.headers = {}
    result = htmx_refresh_response(request)
    assert result.headers["HX-Refresh"] == "true"


def test_safe_redirect_target_with_query():
    request = DummyRequest()
    request.host_url = "http://localhost"
    result = safe_redirect_target(request, "/path?key=value", "/fallback")
    assert "key=value" in result


def test_safe_redirect_target_valueerror():
    """urlsplit raises ValueError for invalid IPv6 URLs."""
    request = DummyRequest()
    request.host_url = "http://localhost"
    result = safe_redirect_target(request, "http://[invalid", "/fallback")
    assert result == "/fallback"


def test_apply_bulk_selection_plain_list(dbsession):
    """apply_bulk_selection falls back to in-memory update for plain lists."""
    from sqlalchemy import select as sa_select

    from marker.models import Company, User
    from marker.views import apply_bulk_selection

    user = User(
        name="plainlst", fullname="PL", email="pl@e.com", role="admin", password="pw"
    )
    dbsession.add(user)
    dbsession.flush()
    co = Company(
        name="PlainCo",
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
    import transaction

    transaction.commit()

    user = dbsession.execute(
        sa_select(User).filter(User.name == "plainlst")
    ).scalar_one()

    from tests.conftest import DummyRequestWithIdentity

    request = DummyRequestWithIdentity()
    request.dbsession = dbsession
    request.identity = user
    request.params = {"checked": "1"}
    request.session = {}
    request.path_qs = "/test"

    selected = []  # plain list, not an SA relationship
    stmt = sa_select(Company).filter(Company.created_by == user)
    apply_bulk_selection(request, stmt, selected)
    assert len(selected) == 1
    assert selected[0].name == "PlainCo"
