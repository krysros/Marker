from pyramid.view import view_config


@view_config(route_name="home", renderer="home.mako")
def home_view(request):
    return {"project": "Marker"}


@view_config(route_name="color_scheme", renderer="string", permission="view")
def color_scheme_view(request):
    session = request.session
    color_scheme = session.get("color_scheme", "light")

    match color_scheme:
        case "light":
            theme = "dark"
        case "dark":
            theme = "light"

    session["color_scheme"] = theme
    request.response.headers = {"HX-Refresh": "true"}
    return theme
