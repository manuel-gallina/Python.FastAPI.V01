"""API routes for retrieving server information."""

import logging
from typing import Annotated

from fastapi import APIRouter, status
from fastapi.params import Depends

from api.server_info.repositories import MainDbInfoRepository
from api.server_info.schemas import (
    DatabaseInfoSchema,
    GetServerInfoResponseSchema,
    SubsystemsInfoSchema,
)
from api.shared.schemas.responses import ObjectResponseSchema
from api.shared.system.datetimes import DatetimeProvider
from api.shared.system.settings import Settings, get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/server-info")


@router.get(
    "",
    responses={
        status.HTTP_200_OK: {"model": ObjectResponseSchema[GetServerInfoResponseSchema]}
    },
)
async def get_server_info(
    settings: Annotated[Settings, Depends(get_settings)],
    main_db_info: Annotated[DatabaseInfoSchema, Depends(MainDbInfoRepository.get)],
    datetime_provider: Annotated[DatetimeProvider, Depends()],
) -> ObjectResponseSchema[GetServerInfoResponseSchema]:
    """Get information about the server.

    Information includes the server version, current datetime, and the status
    of its subsystems.
    """
    return ObjectResponseSchema(
        data=GetServerInfoResponseSchema(
            server_version=settings.project.version,
            current_datetime=datetime_provider.now(),
            subsystems=SubsystemsInfoSchema(main_db=main_db_info),
        )
    )
