"""Routers for authentication-related operations.

This module defines the API routes for authentication-related operations,
such as user management. It includes the necessary imports
and sets up the router for the authentication endpoints.
"""

from fastapi import APIRouter

from api.auth.users.routes import router as users_router

router = APIRouter(prefix="/auth")
router.include_router(users_router)
