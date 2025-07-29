from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config


@view_config(route_name="set_locale")
def set_locale(request):
    locale = request.matchdict.get("locale")
    referrer = request.referrer or request.route_url("home")
    response = HTTPFound(location=referrer)
    response.set_cookie("_LOCALE_", locale, max_age=31536000, path="/")
    return response
