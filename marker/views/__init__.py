from urllib.parse import parse_qsl, urlencode

from sqlalchemy import delete, func, insert, literal, select
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


def sort_column(model, sort_key):
    column = getattr(model, sort_key)
    if sort_key == "name":
        return func.lower(column)
    return column


def is_bulk_select_request(request):
    return request.method == "POST" and request.params.get("_select_all") == "1"


def update_selected_items(selected_items, items, checked):
    if not items:
        return

    items_by_id = {
        item.id: item for item in items if getattr(item, "id", None) is not None
    }
    if not items_by_id:
        return

    if checked:
        selected_ids = {
            item.id
            for item in selected_items
            if getattr(item, "id", None) is not None
        }
        for item_id, item in items_by_id.items():
            if item_id not in selected_ids:
                selected_items.append(item)
        return

    remove_ids = set(items_by_id.keys())
    selected_items[:] = [
        item
        for item in selected_items
        if getattr(item, "id", None) not in remove_ids
    ]


def _resolve_selection_target(selected_items):
    adapter = getattr(selected_items, "_sa_adapter", None)
    relationship_key = getattr(getattr(adapter, "attr", None), "key", None)
    if not relationship_key:
        return None

    return _SELECTION_TARGETS.get(relationship_key)


def _selected_item_ids_subquery(stmt, selected_entity_id_column):
    return (
        stmt.order_by(None)
        .with_only_columns(selected_entity_id_column.label("item_id"))
        .distinct()
        .subquery()
    )


def _coerce_bulk_checked(request):
    raw_checked = request.params.get("checked")

    if raw_checked is None:
        # Treat select_all as a toggle button when no explicit value is sent.
        current = request.session.get("select_all_states", {}).get(
            _select_all_state_key(request),
            False,
        )
        return not current

    if isinstance(raw_checked, bool):
        return raw_checked

    return str(raw_checked).strip().lower() in {"1", "true", "on", "yes"}


def apply_bulk_selection(request, stmt, selected_items):
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


def _select_all_state_key(request):
    path, _, qs = request.path_qs.partition("?")
    params = [
        (key, value)
        for key, value in parse_qsl(qs, keep_blank_values=True)
        if key != "_select_all"
    ]
    normalized_qs = urlencode(params, doseq=True)
    return f"{path}?{normalized_qs}" if normalized_qs else path


def set_select_all_state(request, checked):
    states = request.session.setdefault("select_all_states", {})
    states[_select_all_state_key(request)] = bool(checked)


def handle_bulk_selection(request, stmt, selected_items):
    checked = _coerce_bulk_checked(request)
    apply_bulk_selection(request, stmt, selected_items)
    set_select_all_state(request, checked)
    return htmx_refresh_response(request)


def htmx_refresh_response(request):
    response = request.response
    response.headers = {"HX-Refresh": "true"}
    response.status_code = 200
    return response
