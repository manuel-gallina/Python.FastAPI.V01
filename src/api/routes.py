"""
This module defines the main API router for the application.
It includes all versioned API routes and serves as the central point for routing API requests.
"""

from fastapi import APIRouter

from api.v1.routes import router as v1_router

router = APIRouter(prefix="/api", tags=["api"])
router.include_router(v1_router)
