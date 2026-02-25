"""Tests for POST /api/auth/users endpoint."""

import pytest
from fastapi import status
from httpx import AsyncClient

_ENDPOINT = "/api/auth/users"


@pytest.mark.clean_main_db
async def test_success(http_client: AsyncClient) -> None:
    """Tests that POST /api/auth/users creates a new user and returns it.

    Args:
        http_client (AsyncClient): HTTP client for making requests to the API.
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
