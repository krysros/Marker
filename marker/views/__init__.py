from urllib.parse import parse_qsl, urlencode

from sqlalchemy import func


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


def apply_bulk_selection(request, stmt, selected_items):
    checked = request.params.get("checked", "false").lower() == "true"
    items = request.dbsession.execute(stmt).scalars().all()
    update_selected_items(selected_items, items, checked)


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
    checked = request.params.get("checked", "false").lower() == "true"
    apply_bulk_selection(request, stmt, selected_items)
    set_select_all_state(request, checked)
    return htmx_refresh_response(request)


def htmx_refresh_response(request):
    response = request.response
    response.headers = {"HX-Refresh": "true"}
    response.status_code = 200
    return response
