from marker.forms.select import select_subdivisions
from marker.views.home import home_view


def test_home_view_failure(app_request):
    info = home_view(app_request)
    assert info["project"] == "Marker"


def test_select_subdivisions_returns_default_option_for_unknown_country():
    assert select_subdivisions("ZZ") == [("", "---")]
