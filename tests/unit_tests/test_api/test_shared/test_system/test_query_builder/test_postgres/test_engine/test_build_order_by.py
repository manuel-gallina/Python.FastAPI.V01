"""Test the order by clause building for the Postgres engine."""

import pytest
from api.shared.schemas.errors import ApiError
from api.shared.system.query_builder.postgres.engine import QueryBuilder


def test_no_order_by(query_builder: QueryBuilder) -> None:
    """Test that no order by returns the default 1=1 clause."""
    order_by_clause = query_builder.build_order_by(None)
    assert order_by_clause == "1=1"


def test_empty_order_by(query_builder: QueryBuilder) -> None:
    """Test that an empty list returns the default 1=1 clause."""
    order_by_clause = query_builder.build_order_by([])
    assert order_by_clause == "1=1"


# --- Single field ordering ---


def test_single_field_asc(query_builder: QueryBuilder) -> None:
    """Test ordering by a single field ascending."""
    order_by_clause = query_builder.build_order_by([{"field": "email", "direction": "asc"}])
    assert order_by_clause == "au.email asc"


def test_single_field_desc(query_builder: QueryBuilder) -> None:
    """Test ordering by a single field descending."""
    order_by_clause = query_builder.build_order_by([{"field": "email", "direction": "desc"}])
    assert order_by_clause == "au.email desc"


def test_single_field_default_direction(query_builder: QueryBuilder) -> None:
    """Test that the default direction is asc when not specified."""
    order_by_clause = query_builder.build_order_by([{"field": "email", "direction": "asc"}])
    assert order_by_clause == "au.email asc"


def test_field_name_case_insensitive(query_builder: QueryBuilder) -> None:
    """Test that field lookup is case-insensitive."""
    order_by_clause = query_builder.build_order_by([{"field": "Email", "direction": "asc"}])
    assert order_by_clause == "au.email asc"


def test_direction_case_insensitive(query_builder: QueryBuilder) -> None:
    """Test that direction is case-insensitive."""
    order_by_clause = query_builder.build_order_by([{"field": "email", "direction": "DESC"}])
    assert order_by_clause == "au.email desc"


# --- Multiple field ordering ---


def test_multiple_fields(query_builder: QueryBuilder) -> None:
    """Test ordering by multiple fields."""
    order_by_clause = query_builder.build_order_by(
        [
            {"field": "fullName", "direction": "asc"},
            {"field": "email", "direction": "desc"},
        ]
    )
    assert order_by_clause == "au.full_name asc, au.email desc"


def test_multiple_fields_same_direction(query_builder: QueryBuilder) -> None:
    """Test ordering by multiple fields with the same direction."""
    order_by_clause = query_builder.build_order_by(
        [
            {"field": "fullName", "direction": "asc"},
            {"field": "email", "direction": "asc"},
        ]
    )
    assert order_by_clause == "au.full_name asc, au.email asc"


# --- Error cases ---


def test_unknown_field_raises_error(query_builder: QueryBuilder) -> None:
    """Test that an unknown field raises an ApiError."""
    with pytest.raises(ApiError) as exc_info:
        query_builder.build_order_by([{"field": "unknown", "direction": "asc"}])
    assert "Unknown field: unknown" in str(exc_info.value)


def test_unsupported_direction_raises_error(query_builder: QueryBuilder) -> None:
    """Test that an unsupported direction raises an ApiError."""
    with pytest.raises(ApiError) as exc_info:
        query_builder.build_order_by([{"field": "email", "direction": "sideways"}])
    assert "Unsupported order by direction: sideways" in str(exc_info.value)
