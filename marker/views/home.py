from pyramid.view import view_config


@view_config(route_name="home", renderer="home.mako")
def home_view(request):
    return {"project": "Marker"}


@view_config(route_name="theme", request_method="POST", renderer="string")
def theme_view(request):
    theme = request.matchdict["theme"]
    if theme == "light":
        return "<i class='bi bi-sun-fill'></i>"
    elif theme == "dark":
        return "<i class='bi bi-moon-stars-fill'></i>"
    else:
        return "<i class='bi bi-circle-half'></i>"
