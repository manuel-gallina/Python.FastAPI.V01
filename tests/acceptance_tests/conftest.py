from typing import Any, AsyncGenerator

import pytest
from httpx import AsyncClient
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    test_api_base_url: str = "http://localhost:9101"


@pytest.fixture
def test_settings() -> TestSettings:
    return TestSettings()


@pytest.fixture
async def http_client(test_settings: TestSettings) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(base_url=test_settings.test_api_base_url) as client:
        yield client
