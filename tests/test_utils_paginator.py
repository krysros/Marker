import pytest
from sqlalchemy import column, select, table

from marker.utils.paginator import get_paginator


def test_get_paginator_limits_and_offsets():
    # Fake table for demonstration
    fake_table = table("fake", column("id"))
    stmt = select(fake_table)
    paginated = get_paginator(stmt, page=2, per_page=10)
    # SQLAlchemy compiles the statement to SQL string
    sql = str(paginated.compile(compile_kwargs={"literal_binds": True}))
    assert "LIMIT 10" in sql
    assert "OFFSET 10" in sql
