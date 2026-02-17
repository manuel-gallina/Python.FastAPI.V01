from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine
from testing_utils.databases import execute_queries

_ENDPOINT = "/api/auth/users"


@pytest.mark.clean_main_db
async def test_success(http_client: AsyncClient, main_async_db_engine: AsyncEngine):
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
