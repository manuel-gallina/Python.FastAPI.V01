from fastapi import APIRouter

from api.v1.server_info.schemas import GetServerInfoResponseSchema
from api.v1.shared.schemas.responses import ObjectResponseSchema

router = APIRouter(prefix="/server-info", tags=["server-info"])


@router.get("")
async def get_server_info() -> ObjectResponseSchema[GetServerInfoResponseSchema]:
    return ObjectResponseSchema(
        data=GetServerInfoResponseSchema(server_version="a.b.c")
    )
