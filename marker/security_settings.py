import os

from pyramid.settings import asbool

_MIN_SECRET_LENGTH = 32
_WEAK_SECRET_VALUES = {
    "",
    "seekrit",
    "real-seekrit",
    "test-seekrit",
    "itsaseekreet",
    "real-itsaseekreet",
    "test-itsaseekreet",
    "change-me",
    "changeme",
    "secret",
    "default",
    "password",
}


def get_cookie_secure(settings):
    return asbool(settings.get("cookie.secure", False))


def get_cookie_samesite(settings):
    value = (settings.get("cookie.samesite") or "Lax").strip()
    if value not in {"Lax", "Strict", "None"}:
        return "Lax"
    return value


def get_int_setting(settings, key, default):
    try:
        return int(settings.get(key, default))
    except (TypeError, ValueError):
        return default


def get_validated_secret(settings, setting_key, env_key):
    secret = (os.environ.get(env_key) or settings.get(setting_key) or "").strip()
    if not secret:
        raise ValueError(
            f"Missing required secret '{setting_key}'. Set {env_key} or {setting_key}."
        )

    allow_weak = asbool(settings.get("security.allow_weak_secrets", False))
    if allow_weak:
        return secret

    if len(secret) < _MIN_SECRET_LENGTH or secret.lower() in _WEAK_SECRET_VALUES:
        raise ValueError(
            f"Secret '{setting_key}' is too weak. Set a random value via {env_key} "
            f"with at least {_MIN_SECRET_LENGTH} characters."
        )

    return secret