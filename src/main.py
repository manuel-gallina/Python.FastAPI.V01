"""
Entry point for the FastAPI application.

This module defines the main entry point for the FastAPI application.
It sets up the application, including its lifespan, middlewares and routes.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI

from api.routes import router as api_router
from api.shared.system.databases import get_async_db_engine
from api.shared.system.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, Any]:
    """
    Lifespan function for the FastAPI application.

    This function is responsible for setting up resources when
    the application starts and cleaning them up when the application shuts down.

    Args:
        app_ (FastAPI): The FastAPI application instance.

    Returns:
        AsyncGenerator[None, Any]: This function does not yield any value, but it allows
            for setup and teardown logic to be executed.
    """
    logger.debug("Starting up...")

    logger.debug("Starting main database engine...")
    main_async_db_engine = get_async_db_engine(settings.database.main_connection)
    app_.state.main_async_db_engine = main_async_db_engine
    logger.info("Started main database engine")

    logger.info("Application started successfully.")

    yield

    logger.debug("Shutting down...")

    logger.debug("Disposing main database engine...")
    app_.state.main_async_db_engine = None
    await main_async_db_engine.dispose()
    logger.info("Disposed main database engine")

    logger.info("Application shut down successfully.")


app = FastAPI(title=settings.project.name, lifespan=lifespan)
app.include_router(api_router)
