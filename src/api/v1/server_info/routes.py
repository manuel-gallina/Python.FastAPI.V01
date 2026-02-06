from fastapi import APIRouter, status

from api.v1.server_info.schemas import GetServerInfoResponseSchema
from api.v1.shared.schemas.responses import ObjectResponseSchema

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
async def get_server_info():
    return ObjectResponseSchema(
        data=GetServerInfoResponseSchema(server_version="a.b.c")
    )
