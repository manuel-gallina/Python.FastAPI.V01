from fastapi import status
from httpx import AsyncClient
from testing_utils.datetimes import MockDatetimeProvider

from api.server_info.repositories import MainDbInfoRepository
from api.server_info.schemas import DatabaseInfoSchema, ServerStatus
from api.shared.system.datetimes import DatetimeProvider
from api.shared.system.settings import Settings, get_settings
from main import app

_ENDPOINT = "/api/server-info"


async def test_success(http_test_client: AsyncClient):
    async def mock_main_db_info_repository_get() -> DatabaseInfoSchema:
        return DatabaseInfoSchema(status=ServerStatus.OK, version="PostgreSQL 18")

    def mock_get_settings() -> Settings:
        settings = get_settings()
        settings.project.version = "1.0.0"
        return settings

    app.dependency_overrides = {
        MainDbInfoRepository.get: mock_main_db_info_repository_get,
        DatetimeProvider: MockDatetimeProvider,
        get_settings: mock_get_settings,
    }

    response = await http_test_client.get(_ENDPOINT)

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {
        "data": {
            "currentDatetime": "2026-02-11T00:00:00+00:00",
            "serverVersion": "1.0.0",
            "subsystems": {"mainDb": {"status": "ok", "version": "PostgreSQL 18"}},
        }
    }
