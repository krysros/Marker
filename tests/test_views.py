from marker import models
from marker.views.home import home_view
from marker.views.notfound import notfound_view


def test_home_view_failure(app_request):
    info = home_view(app_request)
    assert info['project'] == 'marker'

# def test_home_view_success(app_request, dbsession):
#     model = models.MyModel(name='one', value=55)
#     dbsession.add(model)
#     dbsession.flush()

#     info = home_view(app_request)
#     assert app_request.response.status_int == 200
#     assert info['one'].name == 'one'
#     assert info['project'] == 'Pyramid Scaffold'

def test_notfound_view(app_request):
    info = notfound_view(app_request)
    assert app_request.response.status_int == 404
    assert info == {}
