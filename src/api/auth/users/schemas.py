"""Schemas for user-related API endpoints."""

from uuid import UUID

from api.shared.schemas.base import BaseSchema


class GetAllUsersResponseSchema(BaseSchema):
    """Schema for the response of the API endpoint that retrieves all users."""

    id: UUID
    full_name: str
    email: str
