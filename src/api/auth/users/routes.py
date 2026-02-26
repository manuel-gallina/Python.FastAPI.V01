"""API routes for user-related operations."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.auth.users.models import User
from api.auth.users.repositories import UsersRepository
from api.auth.users.schemas import GetAllUsersResponseSchema, UserResponseSchema
from api.shared.schemas.errors import NotFoundError, UnprocessableContentError
from api.shared.schemas.responses import ListResponseSchema, ObjectResponseSchema
from api.shared.system.request_tracing import get_request_id

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
async def get_list(
    all_users: Annotated[list[User], Depends(UsersRepository.get_all)],
    all_users_count: Annotated[int, Depends(UsersRepository.count_all)],
) -> ListResponseSchema[GetAllUsersResponseSchema]:
    """Get the list of all users.

    Args:
        all_users (list[User]): A list of User objects retrieved from the database.
        all_users_count (int): The total count of users in the database.

    Returns:
        ListResponseSchema[GetAllUsersResponseSchema]: A response schema containing
            the list of users and metadata.
    """
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
        status.HTTP_200_OK: {
            "model": ObjectResponseSchema[UserResponseSchema],
            "description": "User retrieved successfully.",
        },
        status.HTTP_404_NOT_FOUND: {"description": "User not found."},
    },
)
async def get_one(
    user_id: UUID,
    request_id: Annotated[str, Depends(get_request_id)],
    user: Annotated[User | None, Depends(UsersRepository.get_by_id)],
) -> ObjectResponseSchema[UserResponseSchema]:
    """Get a single user by ID.

    Args:
        user_id (UUID): The ID of the user to retrieve.
        request_id (str): The unique ID of the request for tracing purposes.
        user (User | None): The User object retrieved from the database,
            or None if not found.

    Returns:
        ObjectResponseSchema[UserResponseSchema]: A response schema
            containing the user data.

    Raises:
        HTTPException: If the user was not found (404).
    """
    if user is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            NotFoundError(
                message="User not found with the given ID.",
                detail=f"User not found with ID={user_id}.",
                request_id=request_id,
            ).model_dump(mode="json"),
        )
    return ObjectResponseSchema(
        data=UserResponseSchema(id=user.id, full_name=user.full_name, email=user.email)
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": ObjectResponseSchema[UserResponseSchema],
            "description": "User created successfully.",
        }
    },
)
async def create(
    created_user: Annotated[User, Depends(UsersRepository.create)],
) -> ObjectResponseSchema[UserResponseSchema]:
    """Create a new user.

    Args:
        created_user (User): The newly created User object.

    Returns:
        ObjectResponseSchema[UserResponseSchema]: A response schema
            containing the created user data.
    """
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
        status.HTTP_200_OK: {
            "model": ObjectResponseSchema[UserResponseSchema],
            "description": "User updated successfully.",
        },
        status.HTTP_404_NOT_FOUND: {"description": "User not found."},
    },
)
async def update(
    user_id: UUID,
    request_id: Annotated[str, Depends(get_request_id)],
    user: Annotated[User | None, Depends(UsersRepository.get_by_id)],
    updated_user: Annotated[User | None, Depends(UsersRepository.update)],
) -> ObjectResponseSchema[UserResponseSchema]:
    """Update an existing user.

    Args:
        user_id (UUID): The ID of the user to update.
        request_id (str): The unique ID of the request for tracing purposes.
        user (User | None): The User object retrieved from the database,
            or None if not found.
        updated_user (User | None): The updated User object after the update operation,

    Returns:
        ObjectResponseSchema[UserResponseSchema]: A response schema
            containing the updated user data.

    Raises:
        HTTPException: If the user is not found (404).
    """
    if not user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            NotFoundError(
                message="User not found with the given ID.",
                detail=f"User not found with ID={user_id}.",
                request_id=request_id,
            ).model_dump(mode="json"),
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
        status.HTTP_204_NO_CONTENT: {"description": "User deleted successfully."},
        status.HTTP_404_NOT_FOUND: {"description": "User not found."},
    },
)
async def delete(
    user_id: UUID,
    request_id: Annotated[str, Depends(get_request_id)],
    user: Annotated[User | None, Depends(UsersRepository.get_by_id)],
    deleted: Annotated[bool, Depends(UsersRepository.delete)],
) -> None:
    """Delete a user by ID.

    Args:
        user_id (UUID): The ID of the user to delete.
        request_id (str): The unique ID of the request for tracing purposes.
        user (User | None): The User object retrieved from the database,
            or None if not found.
        deleted (bool): True if the user was deleted, False if not found.

    Returns:
        None: A 204 No Content response if the user was deleted successfully.

    Raises:
        HTTPException: If the user was not found (404) or if the deletion failed (422).
    """
    if not user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            NotFoundError(
                message="User not found with the given ID.",
                detail=f"User not found with ID={user_id}.",
                request_id=request_id,
            ).model_dump(mode="json"),
        )
    if not deleted:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            UnprocessableContentError(
                message="Failed to delete the user.",
                detail=f"Failed to delete user with ID={user_id}.",
                request_id=request_id,
            ).model_dump(mode="json"),
        )
