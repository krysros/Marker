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
