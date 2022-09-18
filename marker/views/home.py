from pyramid.view import view_config


@view_config(route_name="home", renderer="home.mako")
@view_config(route_name="welcome", renderer="welcome.mako")
def home_view(request):
    return {"project": "Marker"}
