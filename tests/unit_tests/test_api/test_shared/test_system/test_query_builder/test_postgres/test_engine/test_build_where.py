"""Test the where clause building for the Postgres engine."""

import pytest
from api.shared.system.query_builder.postgres.engine import QueryBuilder


@pytest.mark.seed_uuid
def test_equal_operator(query_builder: QueryBuilder) -> None:
    """Test the equal operator."""
    filters = {
        "field": "email",
        "operator": "equal",
        "value": "123",
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.email = :email_00000000000000000000000000000001"
    assert sql_params == {"email_00000000000000000000000000000001": "123"}


@pytest.mark.seed_uuid
def test_notequal_operator(query_builder: QueryBuilder) -> None:
    """Test the notequal operator."""
    filters = {
        "field": "email",
        "operator": "notequal",
        "value": "123",
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert (
        where_clause
        == "au.email is distinct from :email_00000000000000000000000000000001"
    )
    assert sql_params == {"email_00000000000000000000000000000001": "123"}
