from fastapi import APIRouter, status

from api.auth.users.schemas import GetAllUsersResponseSchema
from api.shared.schemas.responses import ListResponseSchema

router = APIRouter(prefix="/users")


@router.get(
    "",
    responses={
        status.HTTP_200_OK: {
            "model": ListResponseSchema[GetAllUsersResponseSchema],
            "description": "List of users retrieved successfully.",
        }
    },
)
async def get_all():
    pass
