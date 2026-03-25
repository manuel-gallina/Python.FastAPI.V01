"""Benchmark tests for API endpoints.

These tests use pytest-benchmark to measure endpoint response times
against a live API. Run via the test_acceptance Dagger function.
"""

from uuid import uuid4

import pytest
from fastapi import status
from httpx import Client, Response
from pytest_benchmark.fixture import BenchmarkFixture
from sqlalchemy.ext.asyncio import AsyncEngine

from testing_utils.databases import execute_queries

_ENDPOINT = "/api/auth/users"


def _insert_user(user_id: str, full_name: str, email: str) -> str:
    return (
        f"insert into auth.user (id, full_name, email, password_hash) "
        f"values ('{user_id}', '{full_name}', '{email}', 'placeholder:{email}');"
    )


@pytest.mark.clean_main_db
async def test_get_all_users_latency(
    benchmark: BenchmarkFixture,
    sync_http_client: Client,
    main_async_db_engine: AsyncEngine,
) -> None:
    """Benchmark the GET /api/auth/users endpoint response time.

    Args:
        benchmark (BenchmarkFixture): The pytest-benchmark fixture for timing
            measurements.
        sync_http_client (Client): A synchronous HTTP client.
        main_async_db_engine (AsyncEngine): Async engine for interacting
            with the main database.
    """
    user_id = str(uuid4())
    await execute_queries(
        main_async_db_engine,
        [_insert_user(user_id, "Test User", "john.doe@tmp.com")],
    )

    def call_endpoint() -> Response:
        return sync_http_client.get(_ENDPOINT)

    result = benchmark.pedantic(call_endpoint, rounds=20, warmup_rounds=3)
    assert result.status_code == status.HTTP_200_OK
