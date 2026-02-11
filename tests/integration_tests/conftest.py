from typing import Any, AsyncGenerator

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture(scope="session")
async def http_test_client() -> AsyncGenerator[AsyncClient, Any]:
    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(manager.app), base_url="http://test"
        ) as test_client:
            yield test_client
