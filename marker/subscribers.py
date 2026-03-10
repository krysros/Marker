from pyramid.i18n import TranslationStringFactory, get_localizer
from sqlalchemy import select

from .models import (
    selected_companies,
    selected_contacts,
    selected_projects,
    selected_tags,
)

_SELECTION_ID_SOURCES = {
    "selected_companies": (
        selected_companies,
        selected_companies.c.company_id,
    ),
    "selected_projects": (
        selected_projects,
        selected_projects.c.project_id,
    ),
    "selected_tags": (
        selected_tags,
        selected_tags.c.tag_id,
    ),
    "selected_contacts": (
        selected_contacts,
        selected_contacts.c.contact_id,
    ),
}


def _selected_ids_loader(request):
    cache = {}
    user = getattr(request, "identity", None)
    user_id = getattr(user, "id", None)

    def selected_ids(name):
        if name in cache:
            return cache[name]

        source = _SELECTION_ID_SOURCES.get(name)
        if source is None or user_id is None:
            cache[name] = set()
            return cache[name]

        table, id_column = source
        ids = set(
            request.dbsession.execute(
                select(id_column).where(table.c.user_id == user_id)
            ).scalars()
        )
        cache[name] = ids
        return ids

    return selected_ids


def add_renderer_globals(event):
    request = event["request"]
    event["_"] = request.translate
    event["localizer"] = request.localizer
    event["selected_ids"] = _selected_ids_loader(request)


tsf = TranslationStringFactory("Marker")


def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)

    def auto_translate(*args, **kwargs):
        return localizer.translate(tsf(*args, **kwargs))

    request.localizer = localizer
    request.translate = auto_translate
