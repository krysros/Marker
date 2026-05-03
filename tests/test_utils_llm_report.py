"""Tests for marker/utils/llm_report.py"""

from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# generate_report_sql
# ---------------------------------------------------------------------------


@patch("marker.utils.llm_report.ChatGoogleGenerativeAI")
def test_generate_report_sql_returns_sql(mock_llm_class):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content="SELECT name FROM companies LIMIT 10"
    )
    mock_llm_class.return_value = mock_llm

    from marker.utils.llm_report import generate_report_sql

    result = generate_report_sql("list all companies")

    assert result == "SELECT name FROM companies LIMIT 10"
    mock_llm_class.assert_called_once_with(model="gemini-2.5-flash-lite")


@patch("marker.utils.llm_report.ChatGoogleGenerativeAI")
def test_generate_report_sql_strips_sql_code_fence(mock_llm_class):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content="```sql\nSELECT name FROM companies LIMIT 10\n```"
    )
    mock_llm_class.return_value = mock_llm

    from marker.utils.llm_report import generate_report_sql

    result = generate_report_sql("list all companies")

    assert result == "SELECT name FROM companies LIMIT 10"


@patch("marker.utils.llm_report.ChatGoogleGenerativeAI")
def test_generate_report_sql_strips_plain_code_fence(mock_llm_class):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content="```\nSELECT id FROM projects\n```"
    )
    mock_llm_class.return_value = mock_llm

    from marker.utils.llm_report import generate_report_sql

    result = generate_report_sql("list projects")

    assert result == "SELECT id FROM projects"


@patch("marker.utils.llm_report.ChatGoogleGenerativeAI")
def test_generate_report_sql_passes_model_param(mock_llm_class):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content="SELECT 1")
    mock_llm_class.return_value = mock_llm

    from marker.utils.llm_report import generate_report_sql

    generate_report_sql("test", model="gemini-custom-model")

    mock_llm_class.assert_called_once_with(model="gemini-custom-model")


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

    with patch("marker.forms.ts.get_current_request", return_value=_make_mock_request()):
        with pytest.raises(ValueError, match="Only SELECT"):
            validate_sql("DELETE FROM companies")


def test_validate_sql_raises_for_update():
    from unittest.mock import patch

    from marker.utils.llm_report import validate_sql

    with patch("marker.forms.ts.get_current_request", return_value=_make_mock_request()):
        with pytest.raises(ValueError, match="Only SELECT"):
            validate_sql("UPDATE companies SET name='x'")


def test_validate_sql_raises_for_semicolon_in_body():
    from unittest.mock import patch

    from marker.utils.llm_report import validate_sql

    with patch("marker.forms.ts.get_current_request", return_value=_make_mock_request()):
        with pytest.raises(ValueError, match="Multiple SQL"):
            validate_sql("SELECT 1; DELETE FROM companies")


def test_validate_sql_raises_for_insert_keyword():
    from unittest.mock import patch

    from marker.utils.llm_report import validate_sql

    with patch("marker.forms.ts.get_current_request", return_value=_make_mock_request()):
        with pytest.raises(ValueError, match="INSERT"):
            validate_sql("SELECT * FROM (INSERT INTO companies VALUES (1))")


def test_validate_sql_raises_for_drop_keyword():
    from unittest.mock import patch

    from marker.utils.llm_report import validate_sql

    with patch("marker.forms.ts.get_current_request", return_value=_make_mock_request()):
        with pytest.raises(ValueError, match="DROP"):
            validate_sql("SELECT DROP FROM companies")


def test_validate_sql_raises_for_alter_keyword():
    from unittest.mock import patch

    from marker.utils.llm_report import validate_sql

    with patch("marker.forms.ts.get_current_request", return_value=_make_mock_request()):
        with pytest.raises(ValueError, match="ALTER"):
            validate_sql("SELECT ALTER FROM tables")


def test_validate_sql_raises_for_pragma_keyword():
    from unittest.mock import patch

    from marker.utils.llm_report import validate_sql

    with patch("marker.forms.ts.get_current_request", return_value=_make_mock_request()):
        with pytest.raises(ValueError, match="PRAGMA"):
            validate_sql("SELECT PRAGMA FROM info")
