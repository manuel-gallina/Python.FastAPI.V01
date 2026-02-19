"""API routes for user-related operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import ORJSONResponse

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
    all_users: Annotated[list[User], Depends(UsersRepository.get_all)],
    all_users_count: Annotated[int, Depends(UsersRepository.count_all)],
) -> ORJSONResponse:
    """Get the list of all users.

    Args:
        all_users (list[User]): A list of User objects retrieved from the database.
        all_users_count (int): The total count of users in the database.

    Returns:
        ListResponseSchema[GetAllUsersResponseSchema]: A response schema containing
            the list of users and metadata.
    """
    return ORJSONResponse(
        ListResponseSchema(
            data=[
                GetAllUsersResponseSchema(
                    id=user.id, full_name=user.full_name, email=user.email
                )
                for user in all_users
            ],
            meta=ListResponseSchema.MetaSchema(count=all_users_count),
        ).model_dump()
    )
