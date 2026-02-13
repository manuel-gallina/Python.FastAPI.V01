from unittest.mock import ANY

from fastapi import status
from httpx import AsyncClient

_ENDPOINT = "/api/server-info"


async def test_success(http_client: AsyncClient):
    response = await http_client.get(_ENDPOINT)

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {
        "data": {
            "currentDatetime": ANY,
            "serverVersion": ANY,
            "subsystems": {"mainDb": {"status": "ok", "version": ANY}},
        }
    }
