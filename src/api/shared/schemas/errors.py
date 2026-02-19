"""Schemas for API errors."""

from api.shared.schemas.base import BaseSchema


class ApiError(BaseSchema):
    """Schema for representing an error in API responses."""

    request_id: str
    code: str
    message: str
    detail: str
