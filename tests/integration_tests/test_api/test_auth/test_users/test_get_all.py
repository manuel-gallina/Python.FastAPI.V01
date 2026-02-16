from uuid import UUID

from fastapi import status
from httpx import AsyncClient

from api.auth.users.models import User
from api.auth.users.repositories import UsersRepository
from main import app

_ENDPOINT = "/api/auth/users"


async def test_success(http_test_client: AsyncClient):
    user_id = "94a9187d-197a-4160-8d9e-1634d2b42415"

    async def mock_users_repository_get_all() -> list[User]:
        return [
            User(
                id=UUID(user_id),
                full_name="John Doe",
                email="john.doe@tmp.com",
                password_hash="xyz",
            )
        ]

    async def mock_users_repository_count_all() -> int:
        return 1

    app.dependency_overrides = {
        UsersRepository.get_all: mock_users_repository_get_all,
        UsersRepository.count_all: mock_users_repository_count_all,
    }

    response = await http_test_client.get(_ENDPOINT)

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {
        "data": [{"id": user_id, "fullName": "John Doe", "email": "john.doe@tmp.com"}],
        "meta": {"count": 1},
    }
