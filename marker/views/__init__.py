from urllib.parse import parse_qsl, urlencode
import datetime
import math

from pyramid.httpexceptions import HTTPFound
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


DELETE_LIMIT_COUNT = 10
DELETE_LIMIT_WINDOW = datetime.timedelta(minutes=1)
DELETE_BLOCK_DURATION = datetime.timedelta(hours=1)


def _delete_block_response(request):
    if request.headers.get("HX-Request") == "true":
        return htmx_refresh_response(request)
    referrer = request.referrer or request.route_url("home")
    return HTTPFound(location=referrer)


def enforce_delete_rate_limit(request, records_to_delete=1):
    user = request.identity
    if user is None:
        return None

    if user.role != "editor":
        return None

    now = datetime.datetime.now()
    _ = request.translate

    blocked_until = user.delete_blocked_until
    if blocked_until and blocked_until > now:
        minutes_left = math.ceil((blocked_until - now).total_seconds() / 60)
        request.session.flash(
            _("warning:Deletion is blocked. Try again in %s minutes.")
            % minutes_left
        )
        return _delete_block_response(request)

    if records_to_delete <= 0:
        return None

    window_start = user.delete_window_start
    window_count = user.delete_window_count or 0

    if not window_start or now - window_start > DELETE_LIMIT_WINDOW:
        window_start = now
        window_count = 0

    new_count = window_count + records_to_delete
    if new_count > DELETE_LIMIT_COUNT:
        user.delete_blocked_until = now + DELETE_BLOCK_DURATION
        user.delete_window_start = now
        user.delete_window_count = 0
        request.session.flash(
            _(
                "warning:You deleted more than 10 records in 1 minute. "
                "Deleting is blocked for 60 minutes."
            )
        )
        return _delete_block_response(request)

    user.delete_window_start = window_start
    user.delete_window_count = new_count
    return None
