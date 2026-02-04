from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, Any]:
    print("Starting up...")
    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)
