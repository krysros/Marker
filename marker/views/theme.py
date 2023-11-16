from pyramid.view import view_config
from sqlalchemy import select

from ..models import Theme


@view_config(route_name="theme", renderer="string", permission="view")
def theme_view(request):
    theme = request.dbsession.execute(
        select(Theme).where(Theme.user_id == request.identity.id)
    ).scalar()

    match theme.theme:
        case "light":
            theme.theme = "dark"
        case "dark":
            theme.theme = "light"

    request.response.headers = {"HX-Refresh": "true"}
    return theme.theme
