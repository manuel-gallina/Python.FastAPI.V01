"""API routes for retrieving server information."""

import logging
from typing import Annotated

from fastapi import APIRouter, status
from fastapi.params import Depends
from fastapi.responses import ORJSONResponse

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
        status.HTTP_200_OK: {
            "model": ObjectResponseSchema[GetServerInfoResponseSchema],
            "description": "Server information retrieved successfully.",
        }
    },
)
async def get_server_info(
    settings: Annotated[Settings, Depends(get_settings)],
    main_db_info: Annotated[DatabaseInfoSchema, Depends(MainDbInfoRepository.get)],
    datetime_provider: Annotated[DatetimeProvider, Depends()],
) -> ORJSONResponse:
    """Get information about the server.

    Information includes the server version, current datetime, and the status
    of its subsystems.

    Args:
        settings (Settings): The application settings.
        main_db_info (DatabaseInfoSchema): Information about the main database.
        datetime_provider (DatetimeProvider): A provider for getting
            the current datetime.

    Returns:
        ORJSONResponse: A JSON response containing the server information.
    """
    return ORJSONResponse(
        ObjectResponseSchema(
            data=GetServerInfoResponseSchema(
                server_version=settings.project.version,
                current_datetime=datetime_provider.now(),
                subsystems=SubsystemsInfoSchema(main_db=main_db_info),
            )
        ).model_dump()
    )
