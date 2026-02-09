from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from api.v1.server_info.schemas import GetServerInfoResponseSchema
from api.v1.shared.databases import get_main_async_db_engine
from api.v1.shared.schemas.responses import ObjectResponseSchema
from system.datetimes import current_datetime
from system.settings import Settings, get_settings

router = APIRouter(prefix="/server-info", tags=["server-info"])


@router.get(
    "",
    responses={
        status.HTTP_200_OK: {
            "model": ObjectResponseSchema[GetServerInfoResponseSchema],
            "description": "Server information retrieved successfully.",
        }
    },
)
async def get_server_info(
    settings: Settings = Depends(get_settings),
    main_async_db_engine: AsyncEngine = Depends(get_main_async_db_engine),
):
    async with AsyncSession(main_async_db_engine) as session:
        result = await session.execute(text("select version();"))
        main_db_version = result.scalar_one_or_none()

    return ObjectResponseSchema(
        data=GetServerInfoResponseSchema(
            server_version=settings.project.version,
            main_db_version=main_db_version,
            current_datetime=current_datetime(),
        )
    )
