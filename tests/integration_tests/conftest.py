"""Fixtures for integration tests."""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.fixture
async def http_test_client() -> AsyncGenerator[AsyncClient, Any]:
    """Provides an asynchronous HTTP client for testing the FastAPI application.

    Returns:
        AsyncClient: An asynchronous HTTP client configured
            to interact with the FastAPI application.
    """
    async with (
        LifespanManager(app) as manager,
        AsyncClient(
            transport=ASGITransport(manager.app), base_url="http://test"
        ) as test_client,
    ):
        yield test_client
