from marker.views.home import home_view


def test_home_view_failure(app_request):
    info = home_view(app_request)
    assert info["project"] == "Marker"
