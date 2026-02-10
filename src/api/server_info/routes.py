import logging

from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from api.server_info.schemas import (
    DatabaseInfoSchema,
    GetServerInfoResponseSchema,
    ServerStatus,
    SubsystemsInfoSchema,
)
from api.shared.schemas.responses import ObjectResponseSchema
from api.shared.system.databases import get_main_async_db_engine
from api.shared.system.datetimes import current_datetime
from api.shared.system.settings import Settings, get_settings

router = APIRouter(prefix="/server-info", tags=["server-info"])
logger = logging.getLogger(__name__)


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
    main_db_info = DatabaseInfoSchema(status=ServerStatus.OK, version=None)
    try:
        async with AsyncSession(main_async_db_engine) as session:
            result = await session.execute(text("select version();"))
            main_db_info.version = result.scalar_one_or_none()
    except ConnectionError as exc:
        logger.error(exc)
        main_db_info.status = ServerStatus.OFFLINE

    return ObjectResponseSchema(
        data=GetServerInfoResponseSchema(
            server_version=settings.project.version,
            current_datetime=current_datetime(),
            subsystems=SubsystemsInfoSchema(
                main_db=main_db_info
            ),
        )
    )
