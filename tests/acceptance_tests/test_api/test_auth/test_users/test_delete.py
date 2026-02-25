"""Tests for DELETE /api/auth/users/{user_id} endpoint."""

from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from testing_utils.databases import execute_queries

_ENDPOINT = "/api/auth/users"


@pytest.mark.clean_main_db
async def test_success(
    http_client: AsyncClient, main_async_db_engine: AsyncEngine
) -> None:
    """Tests that DELETE /api/auth/users/{user_id} deletes the user.

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
            values ('{user_id}', 'Test User', 'test@tmp.com', 'xyz');"""
        ],
    )

    response = await http_client.delete(f"{_ENDPOINT}/{user_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT, response.text

    async with AsyncSession(main_async_db_engine) as session:
        result = await session.execute(
            text("select * from auth.user where id = :id"), {"id": user_id}
        )
        row = result.mappings().one_or_none()

    assert row is None


@pytest.mark.clean_main_db
async def test_not_found(http_client: AsyncClient) -> None:
    """Tests that DELETE /api/auth/users/{user_id} returns 404 for a missing user.

    Args:
        http_client (AsyncClient): HTTP client for making requests to the API.
    """
    user_id = str(uuid4())

    response = await http_client.delete(f"{_ENDPOINT}/{user_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
