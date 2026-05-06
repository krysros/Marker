import html
import threading
import time
import urllib.error
import urllib.request

_CACHE = {}
_CACHE_LOCK = threading.Lock()


def clear_uptime_cache():
    with _CACHE_LOCK:
        _CACHE.clear()


def _normalize_url(url):
    value = (url or "").strip()
    if not value:
        return ""
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    return value


def _badge_class(code):
    if code is None:
        return "bg-dark"
    if 200 <= code < 300:
        return "bg-success"
    if 300 <= code < 400:
        return "bg-info"
    if code == 403:
        return "bg-warning"
    if code == 404:
        return "bg-dark"
    if 400 <= code < 500:
        return "bg-warning"
    if code >= 500:
        return "bg-danger"
    return "bg-secondary"


def check_website_uptime(url, timeout=4.0, ttl_seconds=300):
    normalized = _normalize_url(url)
    if not normalized:
        return {"status_code": None, "error": "No URL"}

    now = time.time()
    with _CACHE_LOCK:
        cached = _CACHE.get(normalized)
        if cached and now < cached["expires_at"]:
            return cached["result"]

    try:
        req = urllib.request.Request(normalized, method="HEAD")
        req.add_header("User-Agent", "Marker/1.0")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = {"status_code": resp.status}
    except urllib.error.HTTPError as exc:
        result = {"status_code": exc.code}
    except Exception as exc:
        result = {"status_code": None, "error": str(exc)}

    with _CACHE_LOCK:
        _CACHE[normalized] = {
            "expires_at": now + ttl_seconds,
            "result": result,
        }
    return result


def render_uptime_badge(result):
    code = result.get("status_code")
    error = result.get("error")

    if code is None and error == "No URL":
        return '<span class="badge bg-secondary">-</span>'

    if code is None:
        return (
            f'<span class="badge bg-dark" title="{html.escape(str(error or "Error"))}">'
            "Error"
            "</span>"
        )

    return f'<span class="badge {_badge_class(code)}">{code}</span>'
