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
