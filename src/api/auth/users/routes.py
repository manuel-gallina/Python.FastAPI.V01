from fastapi import APIRouter, Depends, status

from api.auth.users.models import User
from api.auth.users.repositories import UsersRepository
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
async def get_all(
    all_users: list[User] = Depends(UsersRepository.get_all),
    all_users_count: int = Depends(UsersRepository.count_all),
):
    return ListResponseSchema(
        data=[
            GetAllUsersResponseSchema(
                id=user.id, full_name=user.full_name, email=user.email
            )
            for user in all_users
        ],
        meta=ListResponseSchema.MetaSchema(count=all_users_count),
    )
