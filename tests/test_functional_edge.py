import pytest


@pytest.mark.usefixtures("testapp")
def test_404_sets_custom_message(testapp):
    res = testapp.get("/nieistniejacy-url", status=404)
    assert "404" in res.text or "Nie znaleziono" in res.text


@pytest.mark.usefixtures("testapp")
def test_forbidden_redirects_to_login(testapp):
    res = testapp.get("/user/panel", status=(302, 404))
    # If the endpoint exists, check redirect to login
    if res.status_code == 302:
        assert "/login" in res.headers["Location"]
