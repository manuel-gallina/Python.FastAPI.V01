"""Schemas for API errors."""

from api.shared.schemas.base import BaseSchema


class ApiError(BaseSchema):
    """Schema for representing an error in API responses."""

    request_id: str
    code: str
    message: str
    detail: str


class NotFoundError(ApiError):
    """Schema for representing a 404 Not Found error in API responses."""

    code: str = "NOT_FOUND_404"


class UnprocessableContentError(ApiError):
    """Schema for representing a 422 Unprocessable Content error in API responses."""

    code: str = "UNPROCESSABLE_CONTENT_422"


class ConflictError(ApiError):
    """Schema for representing a 409 Conflict error in API responses."""

    code: str = "CONFLICT_409"
