"""Test the where clause building for the Postgres engine."""

import pytest
from api.shared.schemas.errors import ApiError
from api.shared.system.query_builder.postgres.engine import QueryBuilder


def test_no_filter(query_builder: QueryBuilder) -> None:
    """Test that no filter returns the default 1=1 clause."""
    where_clause, sql_params = query_builder.build_where(None)
    assert where_clause == "1=1"
    assert sql_params == {}


# --- Scalar comparison operators ---


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


@pytest.mark.seed_uuid
def test_greaterthan_operator(query_builder: QueryBuilder) -> None:
    """Test the greaterThan operator."""
    filters = {
        "field": "id",
        "operator": "greaterThan",
        "value": 5,
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.id > :id_00000000000000000000000000000001"
    assert sql_params == {"id_00000000000000000000000000000001": 5}


@pytest.mark.seed_uuid
def test_greaterthanorequal_operator(query_builder: QueryBuilder) -> None:
    """Test the greaterThanOrEqual operator."""
    filters = {
        "field": "id",
        "operator": "greaterThanOrEqual",
        "value": 5,
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.id >= :id_00000000000000000000000000000001"
    assert sql_params == {"id_00000000000000000000000000000001": 5}


@pytest.mark.seed_uuid
def test_lessthan_operator(query_builder: QueryBuilder) -> None:
    """Test the lessThan operator."""
    filters = {
        "field": "id",
        "operator": "lessThan",
        "value": 10,
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.id < :id_00000000000000000000000000000001"
    assert sql_params == {"id_00000000000000000000000000000001": 10}


@pytest.mark.seed_uuid
def test_lessthanorequal_operator(query_builder: QueryBuilder) -> None:
    """Test the lessThanOrEqual operator."""
    filters = {
        "field": "id",
        "operator": "lessThanOrEqual",
        "value": 10,
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.id <= :id_00000000000000000000000000000001"
    assert sql_params == {"id_00000000000000000000000000000001": 10}


# --- Case-insensitive equality operators ---


@pytest.mark.seed_uuid
def test_iequal_operator(query_builder: QueryBuilder) -> None:
    """Test the case-insensitive iEqual operator."""
    filters = {
        "field": "email",
        "operator": "iEqual",
        "value": "TEST@EXAMPLE.COM",
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert (
        where_clause
        == "lower(au.email) = lower(:email_00000000000000000000000000000001)"
    )
    assert sql_params == {"email_00000000000000000000000000000001": "TEST@EXAMPLE.COM"}


@pytest.mark.seed_uuid
def test_inotequal_operator(query_builder: QueryBuilder) -> None:
    """Test the case-insensitive iNotEqual operator."""
    filters = {
        "field": "email",
        "operator": "iNotEqual",
        "value": "TEST@EXAMPLE.COM",
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert (
        where_clause == "lower(au.email) "
        "is distinct from "
        "lower(:email_00000000000000000000000000000001)"
    )
    assert sql_params == {"email_00000000000000000000000000000001": "TEST@EXAMPLE.COM"}


# --- LIKE operators ---


@pytest.mark.seed_uuid
def test_like_operator(query_builder: QueryBuilder) -> None:
    """Test the like operator."""
    filters = {
        "field": "email",
        "operator": "like",
        "value": "%test%",
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.email like :email_00000000000000000000000000000001"
    assert sql_params == {"email_00000000000000000000000000000001": "%test%"}


@pytest.mark.seed_uuid
def test_ilike_operator(query_builder: QueryBuilder) -> None:
    """Test the case-insensitive iLike operator."""
    filters = {
        "field": "email",
        "operator": "iLike",
        "value": "%TEST%",
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.email ilike :email_00000000000000000000000000000001"
    assert sql_params == {"email_00000000000000000000000000000001": "%TEST%"}


@pytest.mark.seed_uuid
def test_startswith_operator(query_builder: QueryBuilder) -> None:
    """Test the startsWith operator appends a trailing wildcard."""
    filters = {
        "field": "email",
        "operator": "startsWith",
        "value": "test",
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.email like :email_00000000000000000000000000000001"
    assert sql_params == {"email_00000000000000000000000000000001": "test%"}


@pytest.mark.seed_uuid
def test_istartswith_operator(query_builder: QueryBuilder) -> None:
    """Test the case-insensitive iStartsWith operator appends a trailing wildcard."""
    filters = {
        "field": "email",
        "operator": "iStartsWith",
        "value": "TEST",
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.email ilike :email_00000000000000000000000000000001"
    assert sql_params == {"email_00000000000000000000000000000001": "TEST%"}


@pytest.mark.seed_uuid
def test_endswith_operator(query_builder: QueryBuilder) -> None:
    """Test the endsWith operator prepends a leading wildcard."""
    filters = {
        "field": "email",
        "operator": "endsWith",
        "value": "test",
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.email like :email_00000000000000000000000000000001"
    assert sql_params == {"email_00000000000000000000000000000001": "%test"}


@pytest.mark.seed_uuid
def test_iendswith_operator(query_builder: QueryBuilder) -> None:
    """Test the case-insensitive iEndsWith operator prepends a leading wildcard."""
    filters = {
        "field": "email",
        "operator": "iEndsWith",
        "value": "TEST",
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.email ilike :email_00000000000000000000000000000001"
    assert sql_params == {"email_00000000000000000000000000000001": "%TEST"}


@pytest.mark.seed_uuid
def test_contains_operator(query_builder: QueryBuilder) -> None:
    """Test the contains operator wraps the value in wildcards."""
    filters = {
        "field": "email",
        "operator": "contains",
        "value": "test",
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.email like :email_00000000000000000000000000000001"
    assert sql_params == {"email_00000000000000000000000000000001": "%test%"}


@pytest.mark.seed_uuid
def test_icontains_operator(query_builder: QueryBuilder) -> None:
    """Test the case-insensitive iContains operator wraps the value in wildcards."""
    filters = {
        "field": "email",
        "operator": "iContains",
        "value": "TEST",
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.email ilike :email_00000000000000000000000000000001"
    assert sql_params == {"email_00000000000000000000000000000001": "%TEST%"}


# --- Null / empty operators ---


def test_isnull_operator(query_builder: QueryBuilder) -> None:
    """Test the isNull operator."""
    filters = {
        "field": "email",
        "operator": "isNull",
        "value": None,
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.email is null"
    assert sql_params == {}


def test_isnotnull_operator(query_builder: QueryBuilder) -> None:
    """Test the isNotNull operator."""
    filters = {
        "field": "email",
        "operator": "isNotNull",
        "value": None,
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.email is not null"
    assert sql_params == {}


@pytest.mark.seed_uuid
def test_isempty_operator(query_builder: QueryBuilder) -> None:
    """Test the isEmpty operator compares to an empty string."""
    filters = {
        "field": "email",
        "operator": "isEmpty",
        "value": None,
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == "au.email = :email_00000000000000000000000000000001"
    assert sql_params == {"email_00000000000000000000000000000001": ""}


@pytest.mark.seed_uuid
def test_isnotempty_operator(query_builder: QueryBuilder) -> None:
    """Test the isNotEmpty operator distinguishes from an empty string."""
    filters = {
        "field": "email",
        "operator": "isNotEmpty",
        "value": None,
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert (
        where_clause
        == "au.email is distinct from :email_00000000000000000000000000000001"
    )
    assert sql_params == {"email_00000000000000000000000000000001": ""}


# --- Collection operators ---


@pytest.mark.seed_uuid
def test_in_operator(query_builder: QueryBuilder) -> None:
    """Test the in operator with a list of values."""
    filters = {
        "field": "email",
        "operator": "in",
        "value": ["a@test.com", "b@test.com"],
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == (
        "au.email in ("
        ":email_00000000000000000000000000000001, "
        ":email_00000000000000000000000000000002"
        ")"
    )
    assert sql_params == {
        "email_00000000000000000000000000000001": "a@test.com",
        "email_00000000000000000000000000000002": "b@test.com",
    }


@pytest.mark.seed_uuid
def test_notin_operator(query_builder: QueryBuilder) -> None:
    """Test the notIn operator with a list of values."""
    filters = {
        "field": "email",
        "operator": "notIn",
        "value": ["a@test.com", "b@test.com"],
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == (
        "au.email not in ("
        ":email_00000000000000000000000000000001, "
        ":email_00000000000000000000000000000002"
        ")"
    )
    assert sql_params == {
        "email_00000000000000000000000000000001": "a@test.com",
        "email_00000000000000000000000000000002": "b@test.com",
    }


# --- Subquery operators ---


# noinspection SqlResolve
@pytest.mark.seed_uuid
def test_any_operator(query_builder: QueryBuilder) -> None:
    """Test the 'any' operator injects a compiled subquery into exists()."""
    filters = {
        "field": "sameNames",
        "operator": "any",
        "value": {
            "field": "sameNames.email",
            "operator": "equal",
            "value": "test@example.com",
        },
    }
    where_clause, sql_params = query_builder.build_where(filters)
    expected_subquery = (
        "select * from auth.user au_ "
        "where au_.full_name = au.full_name "
        "and au_.id != au.id "
        "and au_.email = :sameNames_email_00000000000000000000000000000001"
    )
    assert where_clause == f"exists ({expected_subquery})"
    assert sql_params == {
        "sameNames_email_00000000000000000000000000000001": "test@example.com"
    }


# noinspection SqlResolve
@pytest.mark.seed_uuid
def test_all_operator(query_builder: QueryBuilder) -> None:
    """Test the 'all' operator injects a negated subquery into not exists()."""
    filters = {
        "field": "sameNames",
        "operator": "all",
        "value": {
            "field": "sameNames.email",
            "operator": "equal",
            "value": "test@example.com",
        },
    }
    where_clause, sql_params = query_builder.build_where(filters)
    expected_subquery = (
        "select * from auth.user au_ "
        "where au_.full_name = au.full_name "
        "and au_.id != au.id "
        "and not (au_.email = :sameNames_email_00000000000000000000000000000001)"
    )
    assert where_clause == f"not exists ({expected_subquery})"
    assert sql_params == {
        "sameNames_email_00000000000000000000000000000001": "test@example.com"
    }


# --- Complex conditions ---


@pytest.mark.seed_uuid
def test_and_condition(query_builder: QueryBuilder) -> None:
    """Test AND combining two simple rules."""
    filters = {
        "condition": "and",
        "rules": [
            {"field": "email", "operator": "equal", "value": "test@example.com"},
            {"field": "fullName", "operator": "equal", "value": "John"},
        ],
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == (
        "(au.email = :email_00000000000000000000000000000001)"
        " and "
        "(au.full_name = :fullName_00000000000000000000000000000002)"
    )
    assert sql_params == {
        "email_00000000000000000000000000000001": "test@example.com",
        "fullName_00000000000000000000000000000002": "John",
    }


@pytest.mark.seed_uuid
def test_or_condition(query_builder: QueryBuilder) -> None:
    """Test OR combining two simple rules."""
    filters = {
        "condition": "or",
        "rules": [
            {"field": "email", "operator": "equal", "value": "test@example.com"},
            {"field": "fullName", "operator": "equal", "value": "John"},
        ],
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == (
        "(au.email = :email_00000000000000000000000000000001)"
        " or "
        "(au.full_name = :fullName_00000000000000000000000000000002)"
    )
    assert sql_params == {
        "email_00000000000000000000000000000001": "test@example.com",
        "fullName_00000000000000000000000000000002": "John",
    }


@pytest.mark.seed_uuid
def test_nested_conditions(query_builder: QueryBuilder) -> None:
    """Test AND at the top level with a nested OR group."""
    filters = {
        "condition": "and",
        "rules": [
            {"field": "email", "operator": "equal", "value": "test@example.com"},
            {
                "condition": "or",
                "rules": [
                    {"field": "fullName", "operator": "equal", "value": "John"},
                    {"field": "fullName", "operator": "equal", "value": "Jane"},
                ],
            },
        ],
    }
    where_clause, sql_params = query_builder.build_where(filters)
    assert where_clause == (
        "(au.email = :email_00000000000000000000000000000001)"
        " and "
        "((au.full_name = :fullName_00000000000000000000000000000002)"
        " or "
        "(au.full_name = :fullName_00000000000000000000000000000003))"
    )
    assert sql_params == {
        "email_00000000000000000000000000000001": "test@example.com",
        "fullName_00000000000000000000000000000002": "John",
        "fullName_00000000000000000000000000000003": "Jane",
    }


# --- Error cases ---


def test_unknown_field_raises_error(query_builder: QueryBuilder) -> None:
    """Test that an unknown field raises an ApiError."""
    filters = {"field": "unknown", "operator": "equal", "value": "test"}
    with pytest.raises(ApiError) as exc_info:
        query_builder.build_where(filters)
    assert "Unknown field: unknown" in str(exc_info.value)


def test_unsupported_operator_raises_error(query_builder: QueryBuilder) -> None:
    """Test that an unsupported operator raises an ApiError."""
    filters = {"field": "email", "operator": "unsupported", "value": "test"}
    with pytest.raises(ApiError) as exc_info:
        query_builder.build_where(filters)
    assert "Unsupported operator: unsupported" in str(exc_info.value)


def test_invalid_structure_raises_error(query_builder: QueryBuilder) -> None:
    """Test that a where dict without 'field' or 'condition' raises an ApiError."""
    filters = {"invalid": "structure"}
    with pytest.raises(ApiError):
        query_builder.build_where(filters)


def test_equal_with_list_value_raises_error(query_builder: QueryBuilder) -> None:
    """Test that equal rejects a list value."""
    filters = {"field": "email", "operator": "equal", "value": ["a", "b"]}
    with pytest.raises(ApiError):
        query_builder.build_where(filters)


def test_in_with_scalar_value_raises_error(query_builder: QueryBuilder) -> None:
    """Test that in rejects a scalar value."""
    filters = {"field": "email", "operator": "in", "value": "test"}
    with pytest.raises(ApiError):
        query_builder.build_where(filters)


def test_isnull_with_non_none_value_raises_error(query_builder: QueryBuilder) -> None:
    """Test that isNull rejects a non-None value."""
    filters = {"field": "email", "operator": "isNull", "value": "not-none"}
    with pytest.raises(ApiError):
        query_builder.build_where(filters)


def test_like_with_non_string_value_raises_error(query_builder: QueryBuilder) -> None:
    """Test that like rejects a non-string value."""
    filters = {"field": "email", "operator": "like", "value": 123}
    with pytest.raises(ApiError):
        query_builder.build_where(filters)
