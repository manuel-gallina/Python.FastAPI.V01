"""Benchmark tests for API endpoints.

These tests use pytest-benchmark to measure endpoint response times
against a live API. Run via the test_acceptance Dagger function.
"""

from pytest_benchmark.fixture import BenchmarkFixture

from fastapi import status
from httpx import Client, Response

_SERVER_INFO_ENDPOINT = "/api/server-info"


def test_get_server_info_latency(
    benchmark: BenchmarkFixture, sync_http_client: Client
) -> None:
    """Benchmark the GET /api/server-info endpoint response time.

    Args:
        benchmark (BenchmarkFixture): The pytest-benchmark fixture for timing
            measurements.
        sync_http_client (Client): A synchronous HTTP client.
    """

    def call_endpoint() -> Response:
        return sync_http_client.get(_SERVER_INFO_ENDPOINT)

    result = benchmark.pedantic(call_endpoint, rounds=20, warmup_rounds=3)
    assert result.status_code == status.HTTP_200_OK
