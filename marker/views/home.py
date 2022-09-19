from pyramid.view import view_config


@view_config(route_name="index", renderer="index.mako")
@view_config(route_name="home", renderer="home.mako")
def home_view(request):
    return {"project": "Marker"}
