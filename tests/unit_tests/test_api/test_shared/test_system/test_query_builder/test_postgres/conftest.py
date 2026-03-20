"""Fixtures for testing the Postgres engine of the query builder."""

import pytest
from api.shared.system.query_builder.postgres.engine import QueryBuilder
from api.shared.system.query_builder.shared.engine import SUBQUERY_WHERE, Field


@pytest.fixture
def query_builder() -> QueryBuilder:
    """Fixture for the QueryBuilder instance."""
    return QueryBuilder(
        [
            Field("id", "au.id"),
            Field("fullName", "au.full_name"),
            Field("email", "au.email"),
            Field(
                "sameNames",
                f"select * "
                f"from auth.user au_ "
                f"where au_.full_name = au.full_name "
                f"and au_.id != au.id "
                f"and {SUBQUERY_WHERE}",
            ),
            Field("sameNames.email", "au_.email"),
        ]
    )
