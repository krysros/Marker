from urllib.parse import parse_qsl, urlencode


class Filter:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def is_bulk_select_request(request):
    return request.method == "POST" and request.params.get("_select_all") == "1"


def apply_bulk_selection(request, stmt, selected_items):
    checked = request.params.get("checked", "false").lower() == "true"
    items = request.dbsession.execute(stmt).scalars().all()

    if checked:
        for item in items:
            if item not in selected_items:
                selected_items.append(item)
    else:
        for item in items:
            if item in selected_items:
                selected_items.remove(item)


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
