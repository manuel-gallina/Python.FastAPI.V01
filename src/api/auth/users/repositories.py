"""Repository for fetching user data from the database."""

from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.users.models import User
from api.auth.users.schemas import CreateUserRequestSchema, UpdateUserRequestSchema
from api.shared.system.databases import get_request_main_async_db_session


class UsersRepository:
    """Repository for fetching user data from the database."""

    @staticmethod
    async def get_all(
        main_async_db_session: Annotated[
            AsyncSession, Depends(get_request_main_async_db_session)
        ],
    ) -> list[User]:
        """Fetch all users from the database.

        Args:
            main_async_db_session (AsyncSession): The asynchronous database session
                to use for the query.

        Returns:
            list[User]: A list of User objects representing all users in the database.
        """
        result = await main_async_db_session.execute(text("select * from auth.user;"))
        rows = result.all()
        return [User.model_validate(row) for row in rows]

    @staticmethod
    async def count_all(
        main_async_db_session: Annotated[
            AsyncSession, Depends(get_request_main_async_db_session)
        ],
    ) -> int:
        """Fetch the count of all users from the database.

        Args:
            main_async_db_session (AsyncSession): The asynchronous database session
                to use for the query.

        Returns:
            int: The count of all users in the database.
        """
        result = await main_async_db_session.execute(
            text("select count(*) from auth.user;")
        )
        return result.scalar_one()

    @staticmethod
    async def get_by_id(
        user_id: UUID,
        main_async_db_session: Annotated[
            AsyncSession, Depends(get_request_main_async_db_session)
        ],
    ) -> User | None:
        """Fetch a single user by ID from the database.

        Args:
            user_id (UUID): The ID of the user to retrieve.
            main_async_db_session (AsyncSession): The asynchronous database session
                to use for the query.

        Returns:
            User | None: The User object if found, None otherwise.
        """
        result = await main_async_db_session.execute(
            text("select * from auth.user where id = :user_id"),
            {"user_id": str(user_id)},
        )
        row = result.one_or_none()
        return User.model_validate(row) if row is not None else None

    @staticmethod
    async def create(
        body: CreateUserRequestSchema,
        main_async_db_session: Annotated[
            AsyncSession, Depends(get_request_main_async_db_session)
        ],
    ) -> User:
        """Insert a new user into the database.

        Args:
            body (CreateUserRequestSchema): The request body containing the new
                user's data.
            main_async_db_session (AsyncSession): The asynchronous database session
                to use for the query.

        Returns:
            User: The newly created User object.
        """
        user_id = uuid4()
        # TODO(@manuel-gallina): replace with a proper password hashing implementation
        #   https://github.com/manuel-gallina/Python.FastAPI.V01/issues/17
        password_hash = f"placeholder:{body.email}"

        result = await main_async_db_session.execute(
            text(
                """
                insert into auth.user (id, full_name, email, password_hash)
                values (:id, :full_name, :email, :password_hash)
                returning *;
                """
            ),
            {
                "id": str(user_id),
                "full_name": body.full_name,
                "email": body.email,
                "password_hash": password_hash,
            },
        )
        row = result.one()
        return User.model_validate(row)

    @staticmethod
    async def update(
        user: Annotated[User | None, Depends(get_by_id)],
        body: UpdateUserRequestSchema,
        main_async_db_session: Annotated[
            AsyncSession, Depends(get_request_main_async_db_session)
        ],
    ) -> User | None:
        """Update an existing user in the database.

        Args:
            user (User | None): The existing User object to update,
                or None if the user was not found.
            body (UpdateUserRequestSchema): The request body containing the updated
                user's data.
            main_async_db_session (AsyncSession): The asynchronous database session
                to use for the query.

        Returns:
            User | None: The updated User object if found, None otherwise.
        """
        # TODO(@manuel-gallina): replace with a proper password hashing implementation
        #   https://github.com/manuel-gallina/Python.FastAPI.V01/issues/17
        if not user:
            return None

        password_hash = f"placeholder:{body.email}"
        result = await main_async_db_session.execute(
            text(
                """
                update auth.user
                set full_name = :full_name,
                    email = :email,
                    password_hash = :password_hash
                where id = :user_id
                returning *;
                """
            ),
            {
                "user_id": str(user.id),
                "full_name": body.full_name,
                "email": body.email,
                "password_hash": password_hash,
            },
        )
        row = result.one_or_none()
        return User.model_validate(row) if row is not None else None

    @staticmethod
    async def delete(
        user: Annotated[User | None, Depends(get_by_id)],
        main_async_db_session: Annotated[
            AsyncSession, Depends(get_request_main_async_db_session)
        ],
    ) -> bool:
        """Delete a user from the database.

        Args:
            user (User | None): The User object to delete, or None if the user
                was not found.
            main_async_db_session (AsyncSession): The asynchronous database session
                to use for the query.

        Returns:
            bool: True if the user was deleted, False if the user was not found.
        """
        if not user:
            return False

        result = await main_async_db_session.execute(
            text("delete from auth.user where id = :user_id returning id"),
            {"user_id": str(user.id)},
        )
        return result.one_or_none() is not None
