import logging

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
from api.shared.system.datetimes import current_datetime
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
    settings: Settings = Depends(get_settings),
    main_db_info: DatabaseInfoSchema = Depends(MainDbInfoRepository.get),
):
    """
    Endpoint to retrieve server information, including version, current datetime and subsystems info.
    """
    return ORJSONResponse(
        ObjectResponseSchema(
            data=GetServerInfoResponseSchema(
                server_version=settings.project.version,
                current_datetime=current_datetime(),
                subsystems=SubsystemsInfoSchema(main_db=main_db_info),
            )
        ).model_dump()
    )
