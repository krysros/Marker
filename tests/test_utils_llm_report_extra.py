import pytest
from marker.utils.llm_report import validate_sql


def test_validate_sql_invalid():
    # Should raise on non-SELECT
    with pytest.raises(ValueError):
        validate_sql("DROP TABLE foo")
    with pytest.raises(ValueError):
        validate_sql("")
    with pytest.raises(ValueError):
        validate_sql(";")

    def test_validate_sql_invalid_gemini_retries(monkeypatch):
        # Coverage for ValueError with invalid GEMINI_RETRIES
        import os
        from marker.utils.llm_report import generate_sql
        monkeypatch.setenv("GEMINI_RETRIES", "notanint")
        # Should not raise, but will set retries_value to None
        result = generate_sql("SELECT 1")
        assert isinstance(result, str)
