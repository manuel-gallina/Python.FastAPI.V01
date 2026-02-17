from typing import Any, AsyncGenerator

import pytest
from httpx import AsyncClient
from pydantic_settings import BaseSettings
from pytest import FixtureRequest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine

from api.shared.system.databases import get_async_db_engine
from api.shared.system.settings import Settings, get_settings

_MAIN_DB_TABLE_CACHE: list[str] | None = None


class TestSettings(BaseSettings):
    test_api_base_url: str = "http://localhost:9101"


@pytest.fixture
def test_settings() -> TestSettings:
    return TestSettings()


@pytest.fixture
def settings() -> Settings:
    return get_settings()


@pytest.fixture
async def main_async_db_engine(settings: Settings) -> AsyncEngine:
    return get_async_db_engine(settings.database.main_connection)


@pytest.fixture(autouse=True)
async def clean_main_db(
    request: FixtureRequest, main_async_db_engine: AsyncEngine
) -> AsyncGenerator[None, Any]:
    target_schemas = ["auth"]
    marker = request.node.get_closest_marker("clean_main_db")
    if marker:
        global _MAIN_DB_TABLE_CACHE
        if not _MAIN_DB_TABLE_CACHE:
            async with main_async_db_engine.connect() as connection:

                def get_tables(sync_conn):
                    inspector = inspect(sync_conn)
                    tables = []
                    for schema in target_schemas:
                        if schema in inspector.get_schema_names():
                            for table in inspector.get_table_names(schema=schema):
                                tables.append(f"{schema}.{table}")
                    return tables

                _MAIN_DB_TABLE_CACHE = await connection.run_sync(get_tables)

        if _MAIN_DB_TABLE_CACHE:
            async with main_async_db_engine.connect() as connection:
                async with connection.begin() as transaction:
                    await connection.execute(
                        text(
                            f"truncate {', '.join(_MAIN_DB_TABLE_CACHE)} restart identity cascade;"
                        )
                    )
                    await transaction.commit()
    yield


@pytest.fixture
async def http_client(test_settings: TestSettings) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(base_url=test_settings.test_api_base_url) as client:
        yield client
