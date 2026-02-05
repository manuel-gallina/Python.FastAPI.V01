"""
Entry point for the FastAPI application.

This module defines the main entry point for the FastAPI application.
It sets up the application, including its lifespan and routes.
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI

from api.routes import router as api_router


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, Any]:
    print("Starting up...")
    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
