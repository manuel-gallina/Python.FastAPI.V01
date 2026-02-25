"""Tests for POST /api/auth/users endpoint."""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

_ENDPOINT = "/api/auth/users"


@pytest.mark.clean_main_db
async def test_success(
    http_client: AsyncClient, main_async_db_engine: AsyncEngine
) -> None:
    """Tests that POST /api/auth/users creates a new user and returns it.

    Args:
        http_client (AsyncClient): HTTP client for making requests to the API.
        main_async_db_engine (AsyncEngine): Async engine for interacting
            with the main database.
    """
    response = await http_client.post(
        _ENDPOINT,
        json={"fullName": "New User", "email": "new@tmp.com", "password": "secret"},
    )

    assert response.status_code == status.HTTP_201_CREATED, response.text
    body = response.json()
    assert body["data"]["fullName"] == "New User"
    assert body["data"]["email"] == "new@tmp.com"
    assert "id" in body["data"]

    user_id = body["data"]["id"]
    async with AsyncSession(main_async_db_engine) as session:
        result = await session.execute(
            text("select * from auth.user where id = :id"), {"id": user_id}
        )
        row = result.mappings().one_or_none()

    assert row is not None
    assert row["full_name"] == "New User"
    assert row["email"] == "new@tmp.com"
