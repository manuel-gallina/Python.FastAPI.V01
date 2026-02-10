"""
This module defines the main API router.
It imports and includes all the necessary routers for the different endpoint modules.
"""

from fastapi import APIRouter

from api.server_info.routes import router as server_info_router

router = APIRouter(prefix="/api", tags=["api"])
router.include_router(server_info_router)
