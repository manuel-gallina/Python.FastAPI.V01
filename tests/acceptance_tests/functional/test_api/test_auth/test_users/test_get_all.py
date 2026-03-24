"""Tests for GET /api/auth/users endpoint."""

import json
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine

from testing_utils.databases import execute_queries

_ENDPOINT = "/api/auth/users"


def _insert_user(user_id: str, full_name: str, email: str) -> str:
    return (
        f"insert into auth.user (id, full_name, email, password_hash) "
        f"values ('{user_id}', '{full_name}', '{email}', 'placeholder:{email}');"
    )


@pytest.mark.clean_main_db
async def test_success(
    http_client: AsyncClient, main_async_db_engine: AsyncEngine
) -> None:
    """Tests that GET /api/auth/users endpoint returns all users.

    Args:
        http_client (AsyncClient): HTTP client for making requests to the API.
        main_async_db_engine (AsyncEngine): Async engine for interacting
            with the main database.
    """
    user_id = str(uuid4())
    await execute_queries(
        main_async_db_engine,
        [
            f"""insert into auth.user (id, full_name, email, password_hash)
            values ('{user_id}', 'Test User', 'john.doe@tmp.com', 'xyz');"""
        ],
    )

    response = await http_client.get(_ENDPOINT)

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {
        "data": [{"id": user_id, "fullName": "Test User", "email": "john.doe@tmp.com"}],
        "meta": {"count": 1},
    }


@pytest.mark.clean_main_db
async def test_success_filters_equal(
    http_client: AsyncClient, main_async_db_engine: AsyncEngine
) -> None:
    """Tests that filtering by exact email match returns only the matching user.

    Args:
        http_client (AsyncClient): HTTP client for making requests to the API.
        main_async_db_engine (AsyncEngine): Async engine for interacting
            with the main database.
    """
    alice_id = str(uuid4())
    bob_id = str(uuid4())
    await execute_queries(
        main_async_db_engine,
        [
            _insert_user(alice_id, "Alice Smith", "alice@tmp.com"),
            _insert_user(bob_id, "Bob Jones", "bob@tmp.com"),
        ],
    )
    filters = json.dumps(
        {"field": "email", "operator": "equal", "value": "alice@tmp.com"}
    )

    response = await http_client.get(_ENDPOINT, params={"filters": filters})

    assert response.status_code == status.HTTP_200_OK, response.text
    body = response.json()
    assert body["meta"]["count"] == 1
    assert body["data"] == [
        {"id": alice_id, "fullName": "Alice Smith", "email": "alice@tmp.com"}
    ]


@pytest.mark.clean_main_db
async def test_success_filters_contains(
    http_client: AsyncClient, main_async_db_engine: AsyncEngine
) -> None:
    """Tests that filtering by fullName contains returns only matching users.

    Args:
        http_client (AsyncClient): HTTP client for making requests to the API.
        main_async_db_engine (AsyncEngine): Async engine for interacting
            with the main database.
    """
    alice_id = str(uuid4())
    bob_id = str(uuid4())
    await execute_queries(
        main_async_db_engine,
        [
            _insert_user(alice_id, "Alice Smith", "alice@tmp.com"),
            _insert_user(bob_id, "Bob Jones", "bob@tmp.com"),
        ],
    )
    filters = json.dumps(
        {"field": "fullName", "operator": "contains", "value": "Smith"}
    )

    response = await http_client.get(_ENDPOINT, params={"filters": filters})

    assert response.status_code == status.HTTP_200_OK, response.text
    body = response.json()
    assert body["meta"]["count"] == 1
    assert body["data"] == [
        {"id": alice_id, "fullName": "Alice Smith", "email": "alice@tmp.com"}
    ]


@pytest.mark.clean_main_db
async def test_success_sort_asc(
    http_client: AsyncClient, main_async_db_engine: AsyncEngine
) -> None:
    """Tests that sorting by email ascending returns users in ascending order.

    Args:
        http_client (AsyncClient): HTTP client for making requests to the API.
        main_async_db_engine (AsyncEngine): Async engine for interacting
            with the main database.
    """
    alice_id = str(uuid4())
    bob_id = str(uuid4())
    await execute_queries(
        main_async_db_engine,
        [
            _insert_user(bob_id, "Bob Jones", "bob@tmp.com"),
            _insert_user(alice_id, "Alice Smith", "alice@tmp.com"),
        ],
    )
    sort = json.dumps([{"field": "email", "direction": "asc"}])

    response = await http_client.get(_ENDPOINT, params={"sort": sort})

    assert response.status_code == status.HTTP_200_OK, response.text
    body = response.json()
    assert [user["email"] for user in body["data"]] == ["alice@tmp.com", "bob@tmp.com"]


@pytest.mark.clean_main_db
async def test_success_sort_desc(
    http_client: AsyncClient, main_async_db_engine: AsyncEngine
) -> None:
    """Tests that sorting by email descending returns users in descending order.

    Args:
        http_client (AsyncClient): HTTP client for making requests to the API.
        main_async_db_engine (AsyncEngine): Async engine for interacting
            with the main database.
    """
    alice_id = str(uuid4())
    bob_id = str(uuid4())
    await execute_queries(
        main_async_db_engine,
        [
            _insert_user(alice_id, "Alice Smith", "alice@tmp.com"),
            _insert_user(bob_id, "Bob Jones", "bob@tmp.com"),
        ],
    )
    sort = json.dumps([{"field": "email", "direction": "desc"}])

    response = await http_client.get(_ENDPOINT, params={"sort": sort})

    assert response.status_code == status.HTTP_200_OK, response.text
    body = response.json()
    assert [user["email"] for user in body["data"]] == ["bob@tmp.com", "alice@tmp.com"]


@pytest.mark.clean_main_db
async def test_success_pagination_skip(
    http_client: AsyncClient, main_async_db_engine: AsyncEngine
) -> None:
    """Tests that skip pagination skips the specified number of users.

    The count in the response reflects the total number of matching users,
    not the number returned after applying skip.

    Args:
        http_client (AsyncClient): HTTP client for making requests to the API.
        main_async_db_engine (AsyncEngine): Async engine for interacting
            with the main database.
    """
    alice_id = str(uuid4())
    bob_id = str(uuid4())
    charlie_id = str(uuid4())
    expected_total = 3
    await execute_queries(
        main_async_db_engine,
        [
            _insert_user(alice_id, "Alice Smith", "alice@tmp.com"),
            _insert_user(bob_id, "Bob Jones", "bob@tmp.com"),
            _insert_user(charlie_id, "Charlie Brown", "charlie@tmp.com"),
        ],
    )
    sort = json.dumps([{"field": "email", "direction": "asc"}])

    response = await http_client.get(_ENDPOINT, params={"sort": sort, "skip": 1})

    assert response.status_code == status.HTTP_200_OK, response.text
    body = response.json()
    assert body["meta"]["count"] == expected_total
    assert [user["email"] for user in body["data"]] == [
        "bob@tmp.com",
        "charlie@tmp.com",
    ]


@pytest.mark.clean_main_db
async def test_success_pagination_limit(
    http_client: AsyncClient, main_async_db_engine: AsyncEngine
) -> None:
    """Tests that limit pagination returns at most the specified number of users.

    The count in the response reflects the total number of matching users,
    not the number returned after applying the limit.

    Args:
        http_client (AsyncClient): HTTP client for making requests to the API.
        main_async_db_engine (AsyncEngine): Async engine for interacting
            with the main database.
    """
    alice_id = str(uuid4())
    bob_id = str(uuid4())
    charlie_id = str(uuid4())
    expected_total = 3
    await execute_queries(
        main_async_db_engine,
        [
            _insert_user(alice_id, "Alice Smith", "alice@tmp.com"),
            _insert_user(bob_id, "Bob Jones", "bob@tmp.com"),
            _insert_user(charlie_id, "Charlie Brown", "charlie@tmp.com"),
        ],
    )
    sort = json.dumps([{"field": "email", "direction": "asc"}])

    response = await http_client.get(_ENDPOINT, params={"sort": sort, "limit": 2})

    assert response.status_code == status.HTTP_200_OK, response.text
    body = response.json()
    assert body["meta"]["count"] == expected_total
    assert [user["email"] for user in body["data"]] == ["alice@tmp.com", "bob@tmp.com"]
