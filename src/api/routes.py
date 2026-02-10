"""
This module defines the main API router.
It imports and includes all the necessary routers for the different endpoint modules.
"""

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from api.server_info.routes import router as server_info_router

router = APIRouter(prefix="/api", tags=["api"], default_response_class=ORJSONResponse)
router.include_router(server_info_router)
