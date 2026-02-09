"""
Entry point for the FastAPI application.

This module defines the main entry point for the FastAPI application.
It sets up the application, including its lifespan and routes.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI

from api.routes import router as api_router
from api.v1.shared.databases import get_async_db_engine
from system.settings import get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, Any]:
    logger.debug("Starting up...")

    settings = get_settings()

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


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
