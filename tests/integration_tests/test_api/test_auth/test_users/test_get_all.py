"""Integration tests for the GET /api/auth/users endpoint."""

import json
from unittest.mock import AsyncMock
from uuid import UUID

from api.auth.users.models import User
from api.auth.users.repositories import UsersRepository
from api.shared.system.databases import get_request_main_async_db_session
from fastapi import status
from httpx import AsyncClient
from main import app
from testing_utils.responses import assert_error_response

_ENDPOINT = "/api/auth/users"
_USER_ID = "94a9187d-197a-4160-8d9e-1634d2b42415"


def _mock_repo(users: list[User] | None = None, count: int = 1) -> None:
    if users is None:
        users = [
            User(
                id=UUID(_USER_ID),
                full_name="John Doe",
                email="john.doe@tmp.com",
                password_hash="xyz",  # noqa: S106
            )
        ]

    async def mock_get_all() -> list[User]:
        return users

    async def mock_count_all() -> int:
        return count

    app.dependency_overrides = {
        UsersRepository.get_all: mock_get_all,
        UsersRepository.count_all: mock_count_all,
    }


def _mock_db_session() -> None:
    async def mock_session() -> AsyncMock:
        return AsyncMock()

    app.dependency_overrides = {
        get_request_main_async_db_session: mock_session,
    }


async def test_success(http_test_client: AsyncClient) -> None:
    """Test the GET /api/auth/users endpoint for a successful response.

    Args:
        http_test_client (AsyncClient): An asynchronous HTTP client
            for making requests to the API.
    """
    _mock_repo()

    response = await http_test_client.get(_ENDPOINT)

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {
        "data": [{"id": _USER_ID, "fullName": "John Doe", "email": "john.doe@tmp.com"}],
        "meta": {"count": 1},
    }


async def test_success_with_filters(http_test_client: AsyncClient) -> None:
    """Test GET /api/auth/users accepts valid filters and returns 200.

    Args:
        http_test_client (AsyncClient): An asynchronous HTTP client
            for making requests to the API.
    """
    _mock_repo()
    filters = json.dumps(
        {"field": "email", "operator": "equal", "value": "john.doe@tmp.com"}
    )

    response = await http_test_client.get(_ENDPOINT, params={"filters": filters})

    assert response.status_code == status.HTTP_200_OK, response.text


async def test_success_with_sort(http_test_client: AsyncClient) -> None:
    """Test GET /api/auth/users accepts valid sort and returns 200.

    Args:
        http_test_client (AsyncClient): An asynchronous HTTP client
            for making requests to the API.
    """
    _mock_repo()
    sort = json.dumps([{"field": "email", "direction": "asc"}])

    response = await http_test_client.get(_ENDPOINT, params={"sort": sort})

    assert response.status_code == status.HTTP_200_OK, response.text


async def test_success_with_pagination(http_test_client: AsyncClient) -> None:
    """Test GET /api/auth/users accepts skip and limit and returns 200.

    Args:
        http_test_client (AsyncClient): An asynchronous HTTP client
            for making requests to the API.
    """
    _mock_repo()

    response = await http_test_client.get(_ENDPOINT, params={"skip": 0, "limit": 10})

    assert response.status_code == status.HTTP_200_OK, response.text


async def test_filters_invalid_json(http_test_client: AsyncClient) -> None:
    """Test GET /api/auth/users with invalid JSON in filters returns 422.

    Args:
        http_test_client (AsyncClient): An asynchronous HTTP client
            for making requests to the API.
    """
    _mock_db_session()

    response = await http_test_client.get(
        _ENDPOINT, params={"filters": "not-valid-json"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, response.text
    assert_error_response(
        response,
        code="UNPROCESSABLE_CONTENT_422",
        message="Query builder error.",
        detail="Invalid 'filters' query parameter. Must be a valid JSON string.",
    )


async def test_filters_unknown_field(http_test_client: AsyncClient) -> None:
    """Test GET /api/auth/users with an unknown field in filters returns 422.

    Args:
        http_test_client (AsyncClient): An asynchronous HTTP client
            for making requests to the API.
    """
    _mock_db_session()
    filters = json.dumps({"field": "unknown", "operator": "equal", "value": "test"})

    response = await http_test_client.get(_ENDPOINT, params={"filters": filters})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, response.text
    assert_error_response(
        response,
        code="UNPROCESSABLE_CONTENT_422",
        message="Query builder error.",
        detail="Unknown field: unknown.",
    )


async def test_sort_invalid_json(http_test_client: AsyncClient) -> None:
    """Test GET /api/auth/users with invalid JSON in sort returns 422.

    Args:
        http_test_client (AsyncClient): An asynchronous HTTP client
            for making requests to the API.
    """
    _mock_db_session()

    response = await http_test_client.get(_ENDPOINT, params={"sort": "not-valid-json"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, response.text
    assert_error_response(
        response,
        code="UNPROCESSABLE_CONTENT_422",
        message="Query builder error.",
        detail="Invalid 'sort' query parameter. Must be a valid JSON string.",
    )


async def test_sort_unknown_field(http_test_client: AsyncClient) -> None:
    """Test GET /api/auth/users with an unknown field in sort returns 422.

    Args:
        http_test_client (AsyncClient): An asynchronous HTTP client
            for making requests to the API.
    """
    _mock_db_session()
    sort = json.dumps([{"field": "unknown", "direction": "asc"}])

    response = await http_test_client.get(_ENDPOINT, params={"sort": sort})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, response.text
    assert_error_response(
        response,
        code="UNPROCESSABLE_CONTENT_422",
        message="Query builder error.",
        detail="Unknown field: unknown.",
    )


async def test_limit_exceeds_max(http_test_client: AsyncClient) -> None:
    """Test GET /api/auth/users with limit above maximum returns 422.

    Args:
        http_test_client (AsyncClient): An asynchronous HTTP client
            for making requests to the API.
    """
    _mock_db_session()

    response = await http_test_client.get(_ENDPOINT, params={"limit": 501})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, response.text
    assert_error_response(
        response,
        code="UNPROCESSABLE_CONTENT_422",
        message="Query builder error.",
        detail="Limit cannot exceed 500. Received: 501.",
    )
