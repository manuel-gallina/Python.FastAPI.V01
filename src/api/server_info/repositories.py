"""Repository for retrieving information about the main database and server status."""

import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from api.server_info.schemas import DatabaseInfoSchema, ServerStatus
from api.shared.system.databases import get_main_async_db_engine

logger = logging.getLogger(__name__)


class MainDbInfoRepository:
    """Repository for retrieving information about the main database."""

    @staticmethod
    async def get(
        main_async_db_engine: Annotated[AsyncEngine, Depends(get_main_async_db_engine)],
    ) -> DatabaseInfoSchema:
        """Fetch information about the main database, including its status and version.

        Args:
            main_async_db_engine (AsyncEngine): The asynchronous database engine
                for the main database.

        Returns:
            DatabaseInfoSchema: An object containing the status and version
                of the main database.

        """
        main_db_info = DatabaseInfoSchema(status=ServerStatus.OK, version=None)
        try:
            async with AsyncSession(main_async_db_engine) as session:
                result = await session.execute(text("select version();"))
                main_db_info.version = result.scalar_one_or_none()
        except ConnectionError as exc:
            logger.error(exc)
            main_db_info.status = ServerStatus.OFFLINE
        return main_db_info
