from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from starlette.requests import Request

from api.shared.system.settings import DatabaseConnection


def get_async_db_engine(database_connection: DatabaseConnection) -> AsyncEngine:
    """
    Get an asynchronous database engine.

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
    """
    Get the main asynchronous database engine from the application state.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        AsyncEngine: The main asynchronous database engine.
    """
    return request.app.state.main_async_db_engine
