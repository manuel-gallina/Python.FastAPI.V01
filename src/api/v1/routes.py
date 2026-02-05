"""
This module defines the API routes for version 1 of the application.
It imports and includes all the necessary routers for the different endpoint modules.
"""

from fastapi import APIRouter

from api.v1.server_info.routes import router as server_info_router

router = APIRouter(prefix="/v1", tags=["v1"])
router.include_router(server_info_router)
