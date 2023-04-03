from pyramid.view import view_config

from ..forms.select import select_subdivisions


@view_config(
    route_name="subdivision",
    renderer="subdivision.mako",
    permission="view",
)
def subdivision_view(request):
    country = request.params.get("country")
    subdivisions = select_subdivisions(country)
    return {"subdivisions": subdivisions}
