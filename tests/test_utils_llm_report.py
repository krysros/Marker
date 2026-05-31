"""Tests for marker/utils/llm_report.py"""

from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# generate_report_sql
# ---------------------------------------------------------------------------


@patch("marker.utils.llm_report.invoke_text")
def test_generate_report_sql_returns_sql(mock_invoke_text):
    mock_invoke_text.return_value = "SELECT name FROM companies LIMIT 10"

    from marker.utils.llm_report import generate_report_sql

    result = generate_report_sql("list all companies")

    assert result == "SELECT name FROM companies LIMIT 10"
    mock_invoke_text.assert_called_once()


@patch("marker.utils.llm_report.invoke_text")
def test_generate_report_sql_strips_sql_code_fence(mock_invoke_text):
    mock_invoke_text.return_value = "```sql\nSELECT name FROM companies LIMIT 10\n```"

    from marker.utils.llm_report import generate_report_sql

    result = generate_report_sql("list all companies")

    assert result == "SELECT name FROM companies LIMIT 10"


@patch("marker.utils.llm_report.invoke_text")
def test_generate_report_sql_strips_plain_code_fence(mock_invoke_text):
    mock_invoke_text.return_value = "```\nSELECT id FROM projects\n```"

    from marker.utils.llm_report import generate_report_sql

    result = generate_report_sql("list projects")

    assert result == "SELECT id FROM projects"


@patch("marker.utils.llm_report.invoke_text")
@patch("marker.utils.llm_report.get_configured_model")
def test_generate_report_sql_uses_configured_model(mock_get_model, mock_invoke_text):
    mock_invoke_text.return_value = "SELECT 1"
    mock_get_model.return_value = "gemini-ini-model"

    from marker.utils.llm_report import generate_report_sql

    generate_report_sql("test")

    assert mock_invoke_text.call_args.kwargs["model"] == "gemini-ini-model"


# ---------------------------------------------------------------------------
# validate_sql
# ---------------------------------------------------------------------------


def test_validate_sql_valid_select():
    from marker.utils.llm_report import validate_sql

    result = validate_sql("SELECT name FROM companies LIMIT 10")
    assert result == "SELECT name FROM companies LIMIT 10"


def test_validate_sql_strips_trailing_semicolon():
    from marker.utils.llm_report import validate_sql

    result = validate_sql("SELECT name FROM companies LIMIT 10;")
    assert result == "SELECT name FROM companies LIMIT 10"


def test_validate_sql_strips_leading_semicolon():
    from marker.utils.llm_report import validate_sql

    result = validate_sql(";SELECT name FROM companies LIMIT 10")
    assert result.upper().startswith("SELECT")


def _make_mock_request():
    from unittest.mock import MagicMock

    mock_req = MagicMock()
    mock_req.translate.side_effect = lambda msg: msg
    return mock_req


def test_validate_sql_raises_for_non_select():
    from unittest.mock import patch

    from marker.utils.llm_report import validate_sql

    with patch(
        "marker.forms.ts.get_current_request", return_value=_make_mock_request()
    ):
        with pytest.raises(ValueError, match="Only SELECT"):
            validate_sql("DELETE FROM companies")


def test_validate_sql_raises_for_update():
    from unittest.mock import patch

    from marker.utils.llm_report import validate_sql

    with patch(
        "marker.forms.ts.get_current_request", return_value=_make_mock_request()
    ):
        with pytest.raises(ValueError, match="Only SELECT"):
            validate_sql("UPDATE companies SET name='x'")


def test_validate_sql_raises_for_semicolon_in_body():
    from unittest.mock import patch

    from marker.utils.llm_report import validate_sql

    with patch(
        "marker.forms.ts.get_current_request", return_value=_make_mock_request()
    ):
        with pytest.raises(ValueError, match="Multiple SQL"):
            validate_sql("SELECT 1; DELETE FROM companies")


def test_validate_sql_raises_for_insert_keyword():
    from unittest.mock import patch

    from marker.utils.llm_report import validate_sql

    with patch(
        "marker.forms.ts.get_current_request", return_value=_make_mock_request()
    ):
        with pytest.raises(ValueError, match="INSERT"):
            validate_sql("SELECT * FROM (INSERT INTO companies VALUES (1))")


def test_validate_sql_raises_for_drop_keyword():
    from unittest.mock import patch

    from marker.utils.llm_report import validate_sql

    with patch(
        "marker.forms.ts.get_current_request", return_value=_make_mock_request()
    ):
        with pytest.raises(ValueError, match="DROP"):
            validate_sql("SELECT DROP FROM companies")


def test_validate_sql_raises_for_alter_keyword():
    from unittest.mock import patch

    from marker.utils.llm_report import validate_sql

    with patch(
        "marker.forms.ts.get_current_request", return_value=_make_mock_request()
    ):
        with pytest.raises(ValueError, match="ALTER"):
            validate_sql("SELECT ALTER FROM tables")


def test_validate_sql_raises_for_pragma_keyword():
    from unittest.mock import patch

    from marker.utils.llm_report import validate_sql

    with patch(
        "marker.forms.ts.get_current_request", return_value=_make_mock_request()
    ):
        with pytest.raises(ValueError, match="PRAGMA"):
            validate_sql("SELECT PRAGMA FROM info")


def test_get_configured_model_raises_value_error():
    from unittest.mock import patch
    from marker.utils.llm_report import get_configured_model

    with (
        patch("pyramid.threadlocal.get_current_request", return_value=None),
        patch("os.path.exists", return_value=False),
    ):
        with pytest.raises(ValueError, match="Gemini model is not configured"):
            get_configured_model()


def test_get_configured_model_from_request_settings():
    from unittest.mock import patch, MagicMock
    from marker.utils.llm_report import get_configured_model

    mock_req = MagicMock()
    mock_req.registry.settings = {"gemini.model": "request-model"}

    with patch("pyramid.threadlocal.get_current_request", return_value=mock_req):
        model = get_configured_model()
        assert model == "request-model"


def test_get_configured_model_from_ini():
    from unittest.mock import patch, MagicMock
    from marker.utils.llm_report import get_configured_model

    mock_req = MagicMock()
    del mock_req.registry  # trigger attribute missing or req is None

    with (
        patch("pyramid.threadlocal.get_current_request", return_value=None),
        patch("os.path.exists", return_value=True),
        patch(
            "pyramid.paster.get_appsettings", return_value={"gemini.model": "ini-model"}
        ),
    ):
        model = get_configured_model()
        assert model == "ini-model"


def test_get_locale_from_request_locale_name():
    from unittest.mock import patch, MagicMock
    from marker.utils.llm_report import _get_locale

    mock_req = MagicMock()
    mock_req.locale_name = "pl_PL"

    with patch("pyramid.threadlocal.get_current_request", return_value=mock_req):
        loc = _get_locale()
        assert loc == "pl_PL"


def test_get_locale_from_request_registry():
    from unittest.mock import patch, MagicMock
    from marker.utils.llm_report import _get_locale

    mock_req = MagicMock()
    del mock_req.locale_name  # trigger no locale_name attribute
    mock_req.registry.settings = {"pyramid.default_locale_name": "es"}

    with patch("pyramid.threadlocal.get_current_request", return_value=mock_req):
        loc = _get_locale()
        assert loc == "es"


def test_get_locale_from_ini():
    from unittest.mock import patch
    from marker.utils.llm_report import _get_locale

    with (
        patch("pyramid.threadlocal.get_current_request", return_value=None),
        patch("os.path.exists", return_value=True),
        patch(
            "pyramid.paster.get_appsettings",
            return_value={"pyramid.default_locale_name": "de"},
        ),
    ):
        loc = _get_locale()
        assert loc == "de"


@patch("marker.utils.llm_report.invoke_text")
@patch("marker.utils.llm_report.get_configured_model")
def test_generate_report_sql_polish_locale(mock_get_model, mock_invoke_text):
    mock_get_model.return_value = "gemini-model"
    mock_invoke_text.return_value = "SELECT 1"

    from marker.utils.llm_report import generate_report_sql

    generate_report_sql("pokaż firmy", locale="pl")

    # verify that the prompt passed to invoke_text includes Polish translation info
    called_prompt = mock_invoke_text.call_args[0][0]
    assert "User request language is Polish" in called_prompt
    assert "firmy" in called_prompt


def test_get_configured_model_request_exception():
    from unittest.mock import patch, MagicMock
    from marker.utils.llm_report import get_configured_model

    # Accessing hasattr or registry on req raises an exception
    mock_req = MagicMock()
    type(mock_req).registry = property(
        lambda self: exec("raise(Exception('Registry error'))")
    )

    with (
        patch("pyramid.threadlocal.get_current_request", return_value=mock_req),
        patch("os.path.exists", return_value=False),
    ):
        with pytest.raises(ValueError, match="Gemini model is not configured"):
            get_configured_model()


def test_get_configured_model_ini_exception():
    from unittest.mock import patch
    from marker.utils.llm_report import get_configured_model

    with (
        patch("pyramid.threadlocal.get_current_request", return_value=None),
        patch("os.path.exists", return_value=True),
        patch(
            "pyramid.paster.get_appsettings", side_effect=Exception("INI read error")
        ),
    ):
        with pytest.raises(ValueError, match="Gemini model is not configured"):
            get_configured_model()


def test_get_locale_request_exception():
    from unittest.mock import patch
    from marker.utils.llm_report import _get_locale

    with (
        patch(
            "pyramid.threadlocal.get_current_request",
            side_effect=Exception("Request error"),
        ),
        patch("os.path.exists", return_value=False),
    ):
        loc = _get_locale()
        assert loc == "en"


def test_get_locale_settings_exception():
    from unittest.mock import patch, MagicMock
    from marker.utils.llm_report import _get_locale

    mock_req = MagicMock()
    del mock_req.locale_name
    type(mock_req).registry = property(
        lambda self: exec("raise(Exception('Registry error'))")
    )

    with (
        patch("pyramid.threadlocal.get_current_request", return_value=mock_req),
        patch("os.path.exists", return_value=False),
    ):
        loc = _get_locale()
        assert loc == "en"


def test_get_locale_ini_exception():
    from unittest.mock import patch
    from marker.utils.llm_report import _get_locale

    with (
        patch("pyramid.threadlocal.get_current_request", return_value=None),
        patch("os.path.exists", return_value=True),
        patch(
            "pyramid.paster.get_appsettings", side_effect=Exception("INI read error")
        ),
    ):
        loc = _get_locale()
        assert loc == "en"


@patch("marker.utils.llm_report.invoke_text")
@patch("marker.utils.llm_report.get_configured_model")
def test_generate_report_sql_invalid_retries_env(mock_get_model, mock_invoke_text):
    mock_get_model.return_value = "gemini-model"
    mock_invoke_text.return_value = "SELECT 1"

    from marker.utils.llm_report import generate_report_sql

    with patch.dict("os.environ", {"GEMINI_RETRIES": "invalid-int"}):
        generate_report_sql("test prompt")
        # should fall back to 2 retries (none passed)
        assert mock_invoke_text.call_args.kwargs["retries"] == 2
