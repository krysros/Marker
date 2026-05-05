from unittest.mock import MagicMock, patch

import pytest

from marker.utils.uptime import (
    _badge_class,
    _normalize_url,
    check_website_uptime,
    clear_uptime_cache,
    render_uptime_badge,
)


@pytest.fixture(autouse=True)
def clear_cache_each_test():
    clear_uptime_cache()
    yield


def test_normalize_url_variants():
    assert _normalize_url("") == ""
    assert _normalize_url(" example.com ") == "https://example.com"
    assert _normalize_url("http://example.com") == "http://example.com"


def test_badge_class_all_branches():
    assert _badge_class(None) == "bg-dark"
    assert _badge_class(200) == "bg-success"
    assert _badge_class(302) == "bg-info"
    assert _badge_class(403) == "bg-warning"
    assert _badge_class(404) == "bg-dark"
    assert _badge_class(418) == "bg-warning"
    assert _badge_class(503) == "bg-danger"
    assert _badge_class(102) == "bg-secondary"


def test_check_uptime_no_url():
    assert check_website_uptime("") == {"status_code": None, "error": "No URL"}


def test_check_uptime_success_and_cache_hit():
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        first = check_website_uptime("example.com", ttl_seconds=300)
        second = check_website_uptime("example.com", ttl_seconds=300)

    assert first == {"status_code": 200}
    assert second == {"status_code": 200}
    assert mock_open.call_count == 1


def test_check_uptime_cache_expired_triggers_second_request(monkeypatch):
    times = iter([1000.0, 2000.0])
    monkeypatch.setattr("marker.utils.uptime.time.time", lambda: next(times))

    resp1 = MagicMock()
    resp1.status = 200
    resp1.__enter__ = lambda s: s
    resp1.__exit__ = MagicMock(return_value=False)

    resp2 = MagicMock()
    resp2.status = 201
    resp2.__enter__ = lambda s: s
    resp2.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", side_effect=[resp1, resp2]) as mock_open:
        first = check_website_uptime("https://example.com", ttl_seconds=10)
        second = check_website_uptime("https://example.com", ttl_seconds=10)

    assert first == {"status_code": 200}
    assert second == {"status_code": 201}
    assert mock_open.call_count == 2


def test_check_uptime_http_error():
    import urllib.error

    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.HTTPError(
            "https://example.com/404", 404, "Not Found", {}, None
        ),
    ):
        result = check_website_uptime("https://example.com/404")
    assert result == {"status_code": 404}


def test_check_uptime_generic_error():
    with patch("urllib.request.urlopen", side_effect=OSError("Connection refused")):
        result = check_website_uptime("https://bad.invalid")
    assert result["status_code"] is None
    assert "Connection refused" in result["error"]


def test_render_badge_no_url():
    html = render_uptime_badge({"status_code": None, "error": "No URL"})
    assert 'class="badge bg-secondary"' in html
    assert ">-<" in html


def test_render_badge_error_escapes_html():
    html = render_uptime_badge({"status_code": None, "error": 'x"<y>'})
    assert 'class="badge bg-dark"' in html
    assert "Error" in html
    assert "x&quot;&lt;y&gt;" in html


@pytest.mark.parametrize(
    "code,css",
    [
        (200, "bg-success"),
        (302, "bg-info"),
        (403, "bg-warning"),
        (404, "bg-dark"),
        (418, "bg-warning"),
        (503, "bg-danger"),
        (102, "bg-secondary"),
    ],
)
def test_render_badge_status_classes(code, css):
    html = render_uptime_badge({"status_code": code})
    assert f'class="badge {css}"' in html
    assert f">{code}<" in html