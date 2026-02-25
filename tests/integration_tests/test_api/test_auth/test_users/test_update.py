"""Integration tests for the PUT /api/auth/users/{user_id} endpoint."""

from uuid import UUID

from api.auth.users.models import User
from api.auth.users.repositories import UsersRepository
from fastapi import status
from httpx import AsyncClient
from main import app

_ENDPOINT = "/api/auth/users"


async def test_success(http_test_client: AsyncClient) -> None:
    """Test the PUT /api/auth/users/{user_id} endpoint for a successful response.

    Args:
        http_test_client (AsyncClient): An asynchronous HTTP client
            for making requests to the API.
    """
    user_id = "94a9187d-197a-4160-8d9e-1634d2b42415"

    async def mock_update() -> User | None:
        return User(
            id=UUID(user_id),
            full_name="Jane Doe",
            email="jane.doe@tmp.com",
            password_hash="xyz",  # noqa: S106
        )

    app.dependency_overrides = {UsersRepository.update: mock_update}

    response = await http_test_client.put(
        f"{_ENDPOINT}/{user_id}",
        json={"fullName": "Jane Doe", "email": "jane.doe@tmp.com", "password": "secret"},
    )

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {
        "data": {"id": user_id, "fullName": "Jane Doe", "email": "jane.doe@tmp.com"}
    }


async def test_not_found(http_test_client: AsyncClient) -> None:
    """Test the PUT /api/auth/users/{user_id} endpoint when the user does not exist.

    Args:
        http_test_client (AsyncClient): An asynchronous HTTP client
            for making requests to the API.
    """
    user_id = "94a9187d-197a-4160-8d9e-1634d2b42415"

    async def mock_update() -> User | None:
        return None

    app.dependency_overrides = {UsersRepository.update: mock_update}

    response = await http_test_client.put(
        f"{_ENDPOINT}/{user_id}",
        json={"fullName": "Jane Doe", "email": "jane.doe@tmp.com", "password": "secret"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
