"""Repository for fetching user data from the database."""

from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from api.auth.users.models import User
from api.auth.users.schemas import CreateUserRequestSchema, UpdateUserRequestSchema
from api.shared.system.databases import get_main_async_db_engine


class UsersRepository:
    """Repository for fetching user data from the database."""

    @staticmethod
    async def get_all(
        main_async_db_engine: Annotated[AsyncEngine, Depends(get_main_async_db_engine)],
    ) -> list[User]:
        """Fetch all users from the database.

        Args:
            main_async_db_engine (AsyncEngine): The asynchronous database engine
                to use for the query.

        Returns:
            list[User]: A list of User objects representing all users in the database.
        """
        async with AsyncSession(main_async_db_engine) as session:
            result = await session.execute(text("select * from auth.user;"))
            rows = result.all()
        return [User.model_validate(row) for row in rows]

    @staticmethod
    async def count_all(
        main_async_db_engine: Annotated[AsyncEngine, Depends(get_main_async_db_engine)],
    ) -> int:
        """Fetch the count of all users from the database.

        Args:
            main_async_db_engine (AsyncEngine): The asynchronous database engine
                to use for the query.

        Returns:
            int: The count of all users in the database.
        """
        async with AsyncSession(main_async_db_engine) as session:
            result = await session.execute(text("select count(*) from auth.user;"))
            return result.scalar_one()

    @staticmethod
    async def get_by_id(
        user_id: UUID,
        main_async_db_engine: Annotated[AsyncEngine, Depends(get_main_async_db_engine)],
    ) -> User | None:
        """Fetch a single user by ID from the database.

        Args:
            user_id (UUID): The ID of the user to retrieve.
            main_async_db_engine (AsyncEngine): The asynchronous database engine
                to use for the query.

        Returns:
            User | None: The User object if found, None otherwise.
        """
        async with AsyncSession(main_async_db_engine) as session:
            result = await session.execute(
                text("select * from auth.user where id = :user_id"),
                {"user_id": str(user_id)},
            )
            row = result.one_or_none()
        return User.model_validate(row) if row is not None else None

    @staticmethod
    async def create(
        body: CreateUserRequestSchema,
        main_async_db_engine: Annotated[AsyncEngine, Depends(get_main_async_db_engine)],
    ) -> User:
        """Insert a new user into the database.

        Args:
            body (CreateUserRequestSchema): The request body containing the new
                user's data.
            main_async_db_engine (AsyncEngine): The asynchronous database engine
                to use for the query.

        Returns:
            User: The newly created User object.
        """
        user_id = uuid4()
        # TODO: replace with a proper password hashing implementation
        password_hash = f"placeholder:{body.email}"
        async with AsyncSession(main_async_db_engine) as session:
            result = await session.execute(
                text(
                    "insert into auth.user (id, full_name, email, password_hash)"
                    " values (:id, :full_name, :email, :password_hash)"
                    " returning *"
                ),
                {
                    "id": str(user_id),
                    "full_name": body.full_name,
                    "email": body.email,
                    "password_hash": password_hash,
                },
            )
            row = result.one()
            await session.commit()
        return User.model_validate(row)

    @staticmethod
    async def update(
        user_id: UUID,
        body: UpdateUserRequestSchema,
        main_async_db_engine: Annotated[AsyncEngine, Depends(get_main_async_db_engine)],
    ) -> User | None:
        """Update an existing user in the database.

        Args:
            user_id (UUID): The ID of the user to update.
            body (UpdateUserRequestSchema): The request body containing the updated
                user's data.
            main_async_db_engine (AsyncEngine): The asynchronous database engine
                to use for the query.

        Returns:
            User | None: The updated User object if found, None otherwise.
        """
        # TODO: replace with a proper password hashing implementation
        password_hash = f"placeholder:{body.email}"
        async with AsyncSession(main_async_db_engine) as session:
            result = await session.execute(
                text(
                    "update auth.user"
                    " set full_name = :full_name, email = :email,"
                    "     password_hash = :password_hash"
                    " where id = :user_id"
                    " returning *"
                ),
                {
                    "user_id": str(user_id),
                    "full_name": body.full_name,
                    "email": body.email,
                    "password_hash": password_hash,
                },
            )
            row = result.one_or_none()
            await session.commit()
        return User.model_validate(row) if row is not None else None

    @staticmethod
    async def delete(
        user_id: UUID,
        main_async_db_engine: Annotated[AsyncEngine, Depends(get_main_async_db_engine)],
    ) -> bool:
        """Delete a user from the database.

        Args:
            user_id (UUID): The ID of the user to delete.
            main_async_db_engine (AsyncEngine): The asynchronous database engine
                to use for the query.

        Returns:
            bool: True if the user was deleted, False if the user was not found.
        """
        async with AsyncSession(main_async_db_engine) as session:
            result = await session.execute(
                text("delete from auth.user where id = :user_id returning id"),
                {"user_id": str(user_id)},
            )
            deleted = result.one_or_none() is not None
            await session.commit()
        return deleted
