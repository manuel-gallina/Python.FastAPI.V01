"""Integration tests for the GET /api/auth/users/{user_id} endpoint."""

from uuid import UUID

from api.auth.users.models import User
from api.auth.users.repositories import UsersRepository
from fastapi import status
from httpx import AsyncClient
from main import app
from testing_utils.responses import assert_error_response

_ENDPOINT = "/api/auth/users"


async def test_success(http_test_client: AsyncClient) -> None:
    """Test the GET /api/auth/users/{user_id} endpoint for a successful response.

    Args:
        http_test_client (AsyncClient): An asynchronous HTTP client
            for making requests to the API.
    """
    user_id = "94a9187d-197a-4160-8d9e-1634d2b42415"

    async def mock_get_by_id() -> User | None:
        return User(
            id=UUID(user_id),
            full_name="John Doe",
            email="john.doe@tmp.com",
            password_hash="xyz",  # noqa: S106
        )

    app.dependency_overrides = {UsersRepository.get_by_id: mock_get_by_id}

    response = await http_test_client.get(f"{_ENDPOINT}/{user_id}")

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {
        "data": {"id": user_id, "fullName": "John Doe", "email": "john.doe@tmp.com"}
    }


async def test_not_found(http_test_client: AsyncClient) -> None:
    """Test the GET /api/auth/users/{user_id} endpoint when the user does not exist.

    Args:
        http_test_client (AsyncClient): An asynchronous HTTP client
            for making requests to the API.
    """
    user_id = "94a9187d-197a-4160-8d9e-1634d2b42415"

    async def mock_get_by_id() -> User | None:
        return None

    app.dependency_overrides = {UsersRepository.get_by_id: mock_get_by_id}

    response = await http_test_client.get(f"{_ENDPOINT}/{user_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    assert_error_response(
        response,
        code="NOT_FOUND_404",
        message="User not found with the given ID.",
        detail=f"User not found with ID={user_id}.",
    )
