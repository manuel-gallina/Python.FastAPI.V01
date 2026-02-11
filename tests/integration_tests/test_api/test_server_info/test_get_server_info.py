from datetime import datetime

from httpx import AsyncClient
from time_machine import TimeMachineFixture


async def test_success(http_test_client: AsyncClient, freezer: TimeMachineFixture):
    freezer.move_to(datetime(year=2026, month=2, day=11))
    response = await http_test_client.get("/api/v1/server-info")
    assert response.status_code == 200
    assert response.json() == {
        "app_name": "Pollini API",
        "app_version": "1.0.0",
        "environment": "test",
    }
