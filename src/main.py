"""Entry point for the FastAPI application.

This module defines the main entry point for the FastAPI application.
It sets up the application, including its lifespan, middlewares and routes.
"""

import logging
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.routes import router as api_router
from api.shared.system.databases import get_async_db_engine
from api.shared.system.request_tracing import get_request_id, init_request_id
from api.shared.system.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, Any]:
    """Lifespan function for the FastAPI application.

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


app = FastAPI(
    version=settings.project.version,
    title=settings.project.title,
    redoc_url=None,
    docs_url=None,
    openapi_url=None,
    description=settings.project.description,
    lifespan=lifespan,
)
app.include_router(api_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, exc: HTTPException
) -> ORJSONResponse:
    """Custom exception handler for HTTP exceptions.

    Args:
        request (Request): The incoming HTTP request that caused the exception.
        exc (HTTPException): The HTTP exception that was raised.

    Returns:
        ORJSONResponse: A JSON response containing the error details
            and the appropriate status code.
    """
    return ORJSONResponse(content=exc.detail, status_code=exc.status_code)


@app.middleware("http")
async def handle_main_async_db_session(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware to handle the async main database session.

    This middleware ensures that the main database session is properly
    initialized and disposed of for each incoming request.

    Args:
        request (Request): The incoming HTTP request.
        call_next(Callable[[Request], Awaitable[Response]]): The next middleware
            or route handler in the chain.

    Returns:
        Response: The HTTP response returned by the next middleware or route handler.
    """
    request.state.main_async_db_session = None
    try:
        response = await call_next(request)
        session: AsyncSession | None = request.state.main_async_db_session
        if session is not None:
            if status.HTTP_200_OK <= response.status_code < status.HTTP_400_BAD_REQUEST:
                await session.commit()
            else:
                await session.rollback()
            await session.close()
        return response
    except Exception as e:
        if request.state.main_async_db_session is not None:
            await request.state.main_async_db_session.rollback()
            await request.state.main_async_db_session.close()
        raise e


@app.middleware("http")
async def add_request_tracing(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware to add request tracing.

    This middleware assigns a unique ID to each incoming request.

    Args:
        request (Request): The incoming HTTP request.
        call_next(Callable[[Request], Awaitable[Response]]): The next middleware
            or route handler in the chain.

    Returns:
        Response: The HTTP response returned by the next middleware or route handler.
    """
    init_request_id(request)
    logger.info(
        "Received request: %s %s (ID: %s)",
        request.method,
        request.url,
        get_request_id(request),
    )
    response = await call_next(request)
    logger.info(
        "Completed request: %s %s (ID: %s) with status code %s",
        request.method,
        request.url,
        get_request_id(request),
        response.status_code,
    )
    return response
