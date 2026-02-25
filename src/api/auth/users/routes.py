"""API routes for user-related operations."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse, Response

from api.auth.users.models import User
from api.auth.users.repositories import UsersRepository
from api.auth.users.schemas import GetAllUsersResponseSchema, UserResponseSchema
from api.shared.schemas.responses import ListResponseSchema, ObjectResponseSchema

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
        ORJSONResponse: A response schema containing the list of users and metadata.
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
        ).model_dump(mode="json")
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
    user_id: UUID,  # noqa: ARG001
    user: Annotated[User | None, Depends(UsersRepository.get_by_id)],
) -> ORJSONResponse:
    """Get a single user by ID.

    Args:
        user_id (UUID): The ID of the user to retrieve.
        user (User | None): The User object retrieved from the database,
            or None if not found.

    Returns:
        ORJSONResponse: A response schema containing the user data.

    Raises:
        HTTPException: 404 if the user does not exist.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return ORJSONResponse(
        ObjectResponseSchema(
            data=UserResponseSchema(
                id=user.id, full_name=user.full_name, email=user.email
            )
        ).model_dump(mode="json")
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
async def create_one(
    created_user: Annotated[User, Depends(UsersRepository.create)],
) -> ORJSONResponse:
    """Create a new user.

    Args:
        created_user (User): The newly created User object.

    Returns:
        ORJSONResponse: A response schema containing the created user data.
    """
    return ORJSONResponse(
        ObjectResponseSchema(
            data=UserResponseSchema(
                id=created_user.id,
                full_name=created_user.full_name,
                email=created_user.email,
            )
        ).model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED,
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
async def update_one(
    user_id: UUID,  # noqa: ARG001
    updated_user: Annotated[User | None, Depends(UsersRepository.update)],
) -> ORJSONResponse:
    """Update an existing user.

    Args:
        user_id (UUID): The ID of the user to update.
        updated_user (User | None): The updated User object, or None if not found.

    Returns:
        ORJSONResponse: A response schema containing the updated user data.

    Raises:
        HTTPException: 404 if the user does not exist.
    """
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return ORJSONResponse(
        ObjectResponseSchema(
            data=UserResponseSchema(
                id=updated_user.id,
                full_name=updated_user.full_name,
                email=updated_user.email,
            )
        ).model_dump(mode="json")
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "User deleted successfully."},
        status.HTTP_404_NOT_FOUND: {"description": "User not found."},
    },
)
async def delete_one(
    user_id: UUID,  # noqa: ARG001
    deleted: Annotated[bool, Depends(UsersRepository.delete)],
) -> Response:
    """Delete a user by ID.

    Args:
        user_id (UUID): The ID of the user to delete.
        deleted (bool): True if the user was deleted, False if not found.

    Returns:
        Response: 204 No Content on success.

    Raises:
        HTTPException: 404 if the user does not exist.
    """
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
