from pyramid.view import view_config

from ..forms.select import get_subdivisions


@view_config(
    route_name="subdivision",
    renderer="subdivision.mako",
    permission="view",
)
def subdivision_view(request):
    country = request.params.get("country")
    subdivisions = get_subdivisions(country)
    return {"subdivisions": subdivisions}
