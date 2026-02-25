"""Integration tests for the POST /api/auth/users endpoint."""

from uuid import UUID

from api.auth.users.models import User
from api.auth.users.repositories import UsersRepository
from fastapi import status
from httpx import AsyncClient
from main import app

_ENDPOINT = "/api/auth/users"


async def test_success(http_test_client: AsyncClient) -> None:
    """Test the POST /api/auth/users endpoint for a successful response.

    Args:
        http_test_client (AsyncClient): An asynchronous HTTP client
            for making requests to the API.
    """
    user_id = "94a9187d-197a-4160-8d9e-1634d2b42415"

    async def mock_create() -> User:
        return User(
            id=UUID(user_id),
            full_name="John Doe",
            email="john.doe@tmp.com",
            password_hash="xyz",  # noqa: S106
        )

    app.dependency_overrides = {UsersRepository.create: mock_create}

    response = await http_test_client.post(
        _ENDPOINT,
        json={
            "fullName": "John Doe",
            "email": "john.doe@tmp.com",
            "password": "secret",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED, response.text
    assert response.json() == {
        "data": {"id": user_id, "fullName": "John Doe", "email": "john.doe@tmp.com"}
    }
