from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..security_settings import get_cookie_samesite, get_cookie_secure
from . import safe_redirect_target


@view_config(route_name="set_locale")
def set_locale(request):
    locale = request.matchdict.get("locale")
    fallback_url = request.route_url("home")
    referrer = safe_redirect_target(request, request.referrer, fallback_url)

    response = HTTPFound(location=referrer)
    settings = request.registry.settings
    response.set_cookie(
        "_LOCALE_",
        locale,
        max_age=31536000,
        path="/",
        secure=get_cookie_secure(settings),
        httponly=True,
        samesite=get_cookie_samesite(settings),
    )
    return response
