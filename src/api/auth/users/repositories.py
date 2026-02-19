"""Repository for fetching user data from the database."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from api.auth.users.models import User
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
