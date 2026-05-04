from urllib.parse import urlsplit

from pyramid.i18n import TranslationString as _
from sqlalchemy import String, Text, delete, func, insert, literal, select
from zope.sqlalchemy import mark_changed

from ..models import (
    Company,
    Contact,
    Project,
    Tag,
    selected_companies,
    selected_contacts,
    selected_projects,
    selected_tags,
)

_SELECTION_TARGETS = {
    "selected_companies": (
        selected_companies,
        selected_companies.c.company_id,
        Company.id,
    ),
    "selected_projects": (
        selected_projects,
        selected_projects.c.project_id,
        Project.id,
    ),
    "selected_tags": (
        selected_tags,
        selected_tags.c.tag_id,
        Tag.id,
    ),
    "selected_contacts": (
        selected_contacts,
        selected_contacts.c.contact_id,
        Contact.id,
    ),
}


class Filter:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def normalized_tags_from_request(request):
    """Return deduplicated tag names from request params (case-insensitive dedup)."""
    seen = set()
    tags = []
    for value in request.params.getall("tag"):
        name = value.strip()
        normalized = name.lower()
        if name and normalized not in seen:
            seen.add(normalized)
            tags.append(name)
    return tags


def sort_column(model, sort_key):
    """Return column for sorting, using Polish collation if string."""
    column = getattr(model, sort_key)
    if isinstance(getattr(column, "type", None), (String, Text)):
        return polish_sort_expression(column)
    return column


def apply_order(stmt, col, order, *tiebreaks):
    """Apply ascending or descending ordering to stmt by col, with optional tiebreaks."""
    direction = col.asc() if order == "asc" else col.desc()
    return stmt.order_by(direction, *tiebreaks)


def normalize_ci_expression(column):
    """Return SQL expression for case-insensitive, accent-insensitive comparison (Polish)."""
    return func.unicode_lower(column)


def polish_sort_expression(expression):
    """Return SQL expression for sorting according to Polish alphabet."""
    return expression.collate("POLISH_CI")


def normalize_ci_value(value):
    """Return normalized string for case-insensitive, accent-insensitive comparison (Polish)."""
    return str(value).lower()


def contains_ci(column, value):
    """Return SQL LIKE expression for case-insensitive, accent-insensitive containment (Polish)."""
    return normalize_ci_expression(column).like("%" + normalize_ci_value(value) + "%")


def safe_redirect_target(request, target, fallback_url):
    """Return a safe redirect target, falling back to fallback_url if unsafe."""
    if not target:
        return fallback_url

    try:
        parsed = urlsplit(str(target))
    except ValueError:
        return fallback_url

    if parsed.scheme or parsed.netloc:
        current = urlsplit(request.host_url)
        if (
            parsed.scheme not in {"http", "https"}
            or parsed.scheme != current.scheme
            or parsed.netloc.lower() != current.netloc.lower()
        ):
            return fallback_url
        return parsed.geturl()

    if not parsed.path.startswith("/") or parsed.path.startswith("//"):
        return fallback_url

    return parsed.geturl()


def is_bulk_select_request(request):
    """Return True if request is POST with _select_all=1."""
    return request.method == "POST" and request.params.get("_select_all") == "1"


def update_selected_items(selected_items, items, checked):
    """Update selected_items by adding or removing items based on checked flag."""
    if not items:
        return

    items_by_id = {
        item.id: item for item in items if getattr(item, "id", None) is not None
    }
    if not items_by_id:
        return

    if checked:
        selected_ids = {
            item.id for item in selected_items if getattr(item, "id", None) is not None
        }
        for item_id, item in items_by_id.items():
            if item_id not in selected_ids:
                selected_items.append(item)
        return

    remove_ids = set(items_by_id.keys())
    selected_items[:] = [
        item for item in selected_items if getattr(item, "id", None) not in remove_ids
    ]


def _resolve_selection_target(selected_items):
    """Return the selection target tuple for the given selected_items collection."""
    adapter = getattr(selected_items, "_sa_adapter", None)
    relationship_key = getattr(getattr(adapter, "attr", None), "key", None)
    if not relationship_key:
        return None

    return _SELECTION_TARGETS.get(relationship_key)


def _selected_item_ids_subquery(stmt, selected_entity_id_column):
    """Return a subquery of item IDs from the given statement and entity ID column."""
    return (
        stmt.order_by(None)
        .with_only_columns(selected_entity_id_column.label("item_id"))
        .distinct()
        .subquery()
    )


def _coerce_bulk_checked(request):
    """Return boolean value for bulk selection (select all) based on request params.
    If 'checked' is not provided, defaults to True (e.g. clicking 'Select all')."""
    raw_checked = request.params.get("checked")
    if raw_checked is None:
        # Default: select_all = True if 'checked' is not provided (e.g. clicking 'Select all')
        return True
    if isinstance(raw_checked, bool):
        return raw_checked
    return str(raw_checked).strip().lower() in {"1", "true", "on", "yes"}


def apply_bulk_selection(request, stmt, selected_items):
    """Apply bulk selection or deselection to the selected_items collection or selection table."""
    checked = _coerce_bulk_checked(request)
    target = _resolve_selection_target(selected_items)

    # Fallback keeps compatibility for unexpected collection types.
    if target is None:
        items = request.dbsession.execute(stmt).scalars().all()
        update_selected_items(selected_items, items, checked)
        return

    selection_table, selected_column, selected_entity_id_column = target
    user_column = selection_table.c.user_id
    item_ids_subquery = _selected_item_ids_subquery(stmt, selected_entity_id_column)
    user_id = request.identity.id

    if checked:
        existing_for_user = (
            select(1)
            .select_from(selection_table)
            .where(
                selected_column == item_ids_subquery.c.item_id,
                user_column == user_id,
            )
            .exists()
        )

        rows_to_insert = select(
            item_ids_subquery.c.item_id,
            literal(user_id).label(user_column.name),
        ).where(~existing_for_user)

        request.dbsession.execute(
            insert(selection_table).from_select(
                [selected_column.name, user_column.name],
                rows_to_insert,
            )
        )
        mark_changed(request.dbsession)
        return

    request.dbsession.execute(
        delete(selection_table).where(
            user_column == user_id,
            selected_column.in_(select(item_ids_subquery.c.item_id)),
        )
    )
    mark_changed(request.dbsession)


def toggle_selected_item(request, selection_table, selected_column, item_id):
    """Toggle selection of a single item for the current user in the selection table.
    Returns True if selected, False if deselected."""
    if item_id is None:
        return False

    user_column = selection_table.c.user_id
    user_id = request.identity.id
    exists = (
        request.dbsession.execute(
            select(1)
            .select_from(selection_table)
            .where(user_column == user_id, selected_column == item_id)
            .limit(1)
        ).first()
        is not None
    )

    if exists:
        request.dbsession.execute(
            delete(selection_table).where(
                user_column == user_id,
                selected_column == item_id,
            )
        )
        mark_changed(request.dbsession)
        return False

    request.dbsession.execute(
        insert(selection_table).values(
            {
                selected_column.name: item_id,
                user_column.name: user_id,
            }
        )
    )
    mark_changed(request.dbsession)
    return True


def selected_ids_for_items(request, selection_table, selected_column, item_ids):
    """Return selected item IDs (for current user) intersecting with item_ids."""
    ids = [item_id for item_id in item_ids if item_id is not None]
    if not ids:
        return set()

    rows = (
        request.dbsession.execute(
            select(selected_column).where(
                selection_table.c.user_id == request.identity.id,
                selected_column.in_(ids),
            )
        )
        .scalars()
        .all()
    )
    return set(rows)


def clear_selected_rows(request, selection_table, selected_column, item_ids):
    """Remove selected rows for the given item_ids from the selection table for the current user."""
    ids = {item_id for item_id in item_ids if item_id is not None}
    if not ids:
        return

    request.dbsession.execute(delete(selection_table).where(selected_column.in_(ids)))
    mark_changed(request.dbsession)

    # No-op: session-based select_all state is not used in the new implementation.
    pass


def handle_bulk_selection(request, stmt, selected_items):
    """Handle a bulk selection request and return an HTMX refresh response."""
    apply_bulk_selection(request, stmt, selected_items)
    # Removed set_select_all_state, select_all state is now computed dynamically.
    return htmx_refresh_response(request)


def htmx_refresh_response(request):
    """Return a response with the HX-Refresh header for HTMX."""
    response = request.response
    response.headers = {"HX-Refresh": "true"}
    response.status_code = 200
    return response
