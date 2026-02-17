from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from api.auth.users.models import User
from api.shared.system.databases import get_main_async_db_engine


class UsersRepository:
    @staticmethod
    async def get_all(
        main_async_db_engine: AsyncEngine = Depends(get_main_async_db_engine),
    ) -> list[User]:
        async with AsyncSession(main_async_db_engine) as session:
            result = await session.execute(text("select * from auth.user;"))
            rows = result.all()
        return [User.model_validate(row) for row in rows]

    @staticmethod
    async def count_all(
        main_async_db_engine: AsyncEngine = Depends(get_main_async_db_engine),
    ) -> int:
        async with AsyncSession(main_async_db_engine) as session:
            result = await session.execute(text("select count(*) from auth.user;"))
            count = result.scalar_one()
        return count
