"""Schemas for API errors."""

from fastapi import HTTPException

from api.shared.schemas.base import BaseSchema


class _BaseApiError(BaseSchema):
    """Schema for representing an error in API responses."""

    request_id: str
    code: str
    message: str
    detail: str


class NotFoundError(_BaseApiError):
    """Schema for representing a 404 Not Found error in API responses."""

    code: str = "NOT_FOUND_404"


class UnprocessableContentError(_BaseApiError):
    """Schema for representing a 422 Unprocessable Content error in API responses."""

    code: str = "UNPROCESSABLE_CONTENT_422"


class ConflictError(_BaseApiError):
    """Schema for representing a 409 Conflict error in API responses."""

    code: str = "CONFLICT_409"


class ApiError(Exception):
    """Custom exception class for API errors."""

    status_code: int
    error: _BaseApiError

    def __init__(self, status_code: int, error: _BaseApiError) -> None:
        """Initialize the ApiError with the given API error details.

        Args:
            status_code (int): The HTTP status code associated with the error.
            error (_BaseApiError): The API error details
                to be included in the exception.
        """
        self.status_code = status_code
        self.error = error
        super().__init__(error.detail)

    @staticmethod
    def from_http_exception(exc: HTTPException, request_id: str = "N/A") -> "ApiError":
        """Create an ApiError instance from an HTTPException.

        Args:
            exc (HTTPException): The HTTPException to convert into an ApiError.
            request_id (str, optional): The unique ID of the request
                for tracing purposes.

        Returns:
            ApiError: An instance of ApiError containing
                the details from the HTTPException.
        """
        return ApiError(
            status_code=exc.status_code,
            error=_BaseApiError(
                request_id=request_id,
                code=str(exc.status_code),
                message=exc.detail,
                detail=exc.detail,
            ),
        )
