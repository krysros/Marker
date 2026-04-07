import os
from unittest.mock import patch

import pytest

from marker.security_settings import (
    get_cookie_samesite,
    get_cookie_secure,
    get_int_setting,
    get_validated_secret,
)


def test_get_cookie_secure_true():
    assert get_cookie_secure({"cookie.secure": "true"}) is True


def test_get_cookie_secure_false():
    assert get_cookie_secure({"cookie.secure": "false"}) is False


def test_get_cookie_secure_default():
    assert get_cookie_secure({}) is False


def test_get_cookie_samesite_lax():
    assert get_cookie_samesite({"cookie.samesite": "Lax"}) == "Lax"


def test_get_cookie_samesite_strict():
    assert get_cookie_samesite({"cookie.samesite": "Strict"}) == "Strict"


def test_get_cookie_samesite_none():
    assert get_cookie_samesite({"cookie.samesite": "None"}) == "None"


def test_get_cookie_samesite_invalid_falls_back_to_lax():
    assert get_cookie_samesite({"cookie.samesite": "BadValue"}) == "Lax"


def test_get_cookie_samesite_missing_falls_back_to_lax():
    assert get_cookie_samesite({}) == "Lax"


def test_get_cookie_samesite_whitespace_stripped():
    assert get_cookie_samesite({"cookie.samesite": "  Strict  "}) == "Strict"


def test_get_int_setting_valid():
    assert get_int_setting({"timeout": "300"}, "timeout", 100) == 300


def test_get_int_setting_missing_returns_default():
    assert get_int_setting({}, "timeout", 100) == 100


def test_get_int_setting_type_error():
    assert get_int_setting({"timeout": None}, "timeout", 42) == 42


def test_get_int_setting_value_error():
    assert get_int_setting({"timeout": "abc"}, "timeout", 42) == 42


def test_get_validated_secret_valid_strong():
    secret = "a" * 40
    result = get_validated_secret(
        {"my.secret": secret}, setting_key="my.secret", env_key="MY_SECRET"
    )
    assert result == secret


def test_get_validated_secret_empty_raises():
    with pytest.raises(ValueError, match="Missing required secret"):
        get_validated_secret({}, setting_key="my.secret", env_key="MY_SECRET")


def test_get_validated_secret_weak_raises():
    with pytest.raises(ValueError, match="too weak"):
        get_validated_secret(
            {"my.secret": "seekrit"}, setting_key="my.secret", env_key="MY_SECRET"
        )


def test_get_validated_secret_short_raises():
    with pytest.raises(ValueError, match="too weak"):
        get_validated_secret(
            {"my.secret": "short"}, setting_key="my.secret", env_key="MY_SECRET"
        )


def test_get_validated_secret_allow_weak():
    result = get_validated_secret(
        {"my.secret": "seekrit", "security.allow_weak_secrets": "true"},
        setting_key="my.secret",
        env_key="MY_SECRET",
    )
    assert result == "seekrit"


@patch.dict(os.environ, {"MY_SECRET": "env-secret-that-is-long-enough-for-test"})
def test_get_validated_secret_from_env():
    result = get_validated_secret({}, setting_key="my.secret", env_key="MY_SECRET")
    assert result == "env-secret-that-is-long-enough-for-test"


@patch.dict(os.environ, {"MY_SECRET": "env-secret-that-is-long-enough-for-test"})
def test_get_validated_secret_env_overrides_setting():
    result = get_validated_secret(
        {"my.secret": "x" * 40}, setting_key="my.secret", env_key="MY_SECRET"
    )
    assert result == "env-secret-that-is-long-enough-for-test"
