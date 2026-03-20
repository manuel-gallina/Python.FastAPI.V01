"""API routes for user-related operations."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from api.auth.users.models import User
from api.auth.users.repositories import UsersRepository
from api.auth.users.schemas import GetAllUsersResponseSchema, UserResponseSchema
from api.shared.schemas.errors import (
    ApiError,
    NotFoundErrorSchema,
    UnprocessableContentErrorSchema,
)
from api.shared.schemas.responses import (
    ErrorResponseSchema,
    ListResponseSchema,
    ObjectResponseSchema,
)
from api.shared.system.request_tracing import get_request_id

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    responses={
        status.HTTP_200_OK: {"model": ListResponseSchema[GetAllUsersResponseSchema]}
    },
)
async def get_list(
    all_users: Annotated[list[User], Depends(UsersRepository.get_all)],
    all_users_count: Annotated[int, Depends(UsersRepository.count_all)],
) -> ListResponseSchema[GetAllUsersResponseSchema]:
    """Get the list of all users."""
    return ListResponseSchema(
        data=[
            GetAllUsersResponseSchema(
                id=user.id, full_name=user.full_name, email=user.email
            )
            for user in all_users
        ],
        meta=ListResponseSchema.MetaSchema(count=all_users_count),
    )


@router.get(
    "/{user_id}",
    responses={
        status.HTTP_200_OK: {"model": ObjectResponseSchema[UserResponseSchema]},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
    },
)
async def get_one(
    user_id: UUID,
    request_id: Annotated[str, Depends(get_request_id)],
    user: Annotated[User | None, Depends(UsersRepository.get_by_id)],
) -> ObjectResponseSchema[UserResponseSchema]:
    """Get a single user by ID."""
    if user is None:
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            NotFoundErrorSchema(
                message="User not found with the given ID.",
                detail=f"User not found with ID={user_id}.",
                request_id=request_id,
            ),
        )
    return ObjectResponseSchema(
        data=UserResponseSchema(id=user.id, full_name=user.full_name, email=user.email)
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"model": ObjectResponseSchema[UserResponseSchema]}
    },
)
async def create(
    created_user: Annotated[User, Depends(UsersRepository.create)],
) -> ObjectResponseSchema[UserResponseSchema]:
    """Create a new user."""
    return ObjectResponseSchema(
        data=UserResponseSchema(
            id=created_user.id,
            full_name=created_user.full_name,
            email=created_user.email,
        )
    )


@router.put(
    "/{user_id}",
    responses={
        status.HTTP_200_OK: {"model": ObjectResponseSchema[UserResponseSchema]},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
    },
)
async def update(
    user_id: UUID,
    request_id: Annotated[str, Depends(get_request_id)],
    user: Annotated[User | None, Depends(UsersRepository.get_by_id)],
    updated_user: Annotated[User | None, Depends(UsersRepository.update)],
) -> ObjectResponseSchema[UserResponseSchema]:
    """Update an existing user."""
    if not user:
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            NotFoundErrorSchema(
                message="User not found with the given ID.",
                detail=f"User not found with ID={user_id}.",
                request_id=request_id,
            ),
        )

    return ObjectResponseSchema(
        data=UserResponseSchema(
            id=updated_user.id,
            full_name=updated_user.full_name,
            email=updated_user.email,
        )
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponseSchema},
    },
)
async def delete(
    user_id: UUID,
    request_id: Annotated[str, Depends(get_request_id)],
    user: Annotated[User | None, Depends(UsersRepository.get_by_id)],
    deleted: Annotated[bool, Depends(UsersRepository.delete)],
) -> None:
    """Delete a user by ID."""
    if not user:
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            NotFoundErrorSchema(
                message="User not found with the given ID.",
                detail=f"User not found with ID={user_id}.",
                request_id=request_id,
            ),
        )
    if not deleted:
        raise ApiError(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            UnprocessableContentErrorSchema(
                message="Failed to delete the user.",
                detail=f"Failed to delete user with ID={user_id}.",
                request_id=request_id,
            ),
        )
