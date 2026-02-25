"""Functions for managing database connections and engines."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from starlette.requests import Request

from api.shared.system.settings import DatabaseConnection


def get_async_db_engine(database_connection: DatabaseConnection) -> AsyncEngine:
    """Get an asynchronous database engine.

    Args:
        database_connection (DatabaseConnection): The database connection settings.

    Returns:
        AsyncEngine: An instance of the asynchronous database engine.
    """
    return create_async_engine(
        database_connection.url,
        pool_pre_ping=database_connection.pool_pre_ping,
        pool_size=database_connection.pool_size,
        max_overflow=database_connection.max_overflow,
    )


def get_main_async_db_engine(request: Request) -> AsyncEngine:
    """Get the main asynchronous database engine from the application state.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        AsyncEngine: The main asynchronous database engine.
    """
    return request.app.state.main_async_db_engine


async def get_request_main_async_db_session(
    request: Request,
    main_async_db_engine: Annotated[AsyncEngine, Depends(get_main_async_db_engine)],
) -> AsyncSession:
    """Get the main async database session linked to the current request.

    Args:
        request (Request): The FastAPI request object.
        main_async_db_engine (AsyncEngine): The main asynchronous database engine.

    Returns:
        AsyncGenerator[AsyncSession, Any]: An asynchronous database session linked
            to the current request.
    """
    if request.state.main_async_db_session is None:
        session = AsyncSession(main_async_db_engine)
        await session.begin()
        request.state.main_async_db_session = session

    return request.state.main_async_db_session
