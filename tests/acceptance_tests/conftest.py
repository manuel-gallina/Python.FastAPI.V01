"""Fixtures for acceptance tests."""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from api.shared.system.databases import get_async_db_engine
from api.shared.system.settings import Settings, get_settings
from httpx import AsyncClient
from pydantic_settings import BaseSettings
from sqlalchemy import Connection, inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine

_MAIN_DB_TABLE_CACHE: list[str] | None = None


class TestSettings(BaseSettings):
    """Settings for acceptance tests."""

    test_api_base_url: str = "http://localhost:9101"


@pytest.fixture
def test_settings() -> TestSettings:
    """Returns the settings for acceptance tests.

    Returns:
        TestSettings: The settings for acceptance tests.
    """
    return TestSettings()


@pytest.fixture
def settings() -> Settings:
    """Returns the application settings.

    Returns:
        Settings: The application settings.
    """
    return get_settings()


@pytest.fixture
async def main_async_db_engine(settings: Settings) -> AsyncEngine:
    """Returns the asynchronous database engine for the main database.

    Args:
        settings (Settings): The application settings containing
            the database connection information.

    Returns:
        AsyncEngine: An asynchronous database engine for the main database.
    """
    return get_async_db_engine(settings.database.main_connection)


@pytest.fixture(autouse=True)
async def clean_main_db(
    request: pytest.FixtureRequest, main_async_db_engine: AsyncEngine
) -> None:
    """A fixture that automatically cleans the main database before each test.

    Args:
        request (pytest.FixtureRequest): The pytest fixture request object,
            used to check for markers on the test function.
        main_async_db_engine (AsyncEngine): The asynchronous database engine
            for the main database, used to execute the SQL queries
            to clean the database.
    """
    target_schemas = ["auth"]
    marker = request.node.get_closest_marker("clean_main_db")
    if marker:
        global _MAIN_DB_TABLE_CACHE  # noqa: PLW0603
        if not _MAIN_DB_TABLE_CACHE:
            async with main_async_db_engine.connect() as connection:

                def get_tables(sync_conn: Connection) -> list[str]:
                    inspector = inspect(sync_conn)
                    tables = []
                    for schema in target_schemas:
                        if schema in inspector.get_schema_names():
                            for table in inspector.get_table_names(schema=schema):
                                tables.append(f"{schema}.{table}")
                    return tables

                _MAIN_DB_TABLE_CACHE = await connection.run_sync(get_tables)

        if _MAIN_DB_TABLE_CACHE:
            async with (
                main_async_db_engine.connect() as connection,
                connection.begin() as transaction,
            ):
                await connection.execute(
                    text(
                        f"truncate {', '.join(_MAIN_DB_TABLE_CACHE)} "
                        f"restart identity cascade;"
                    )
                )
                await transaction.commit()


@pytest.fixture
async def http_client(test_settings: TestSettings) -> AsyncGenerator[AsyncClient, Any]:
    """Provides an asynchronous HTTP client for testing the API.

    Args:
        test_settings (TestSettings): The settings for acceptance tests, used to
            configure the base URL of the HTTP client.

    Returns:
        AsyncClient: An asynchronous HTTP client configured to interact with the API.

    """
    async with AsyncClient(base_url=test_settings.test_api_base_url) as client:
        yield client
