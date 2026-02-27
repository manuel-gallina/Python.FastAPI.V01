"""Schemas for user-related API endpoints."""

from uuid import UUID

from api.shared.schemas.base import BaseSchema


class GetAllUsersResponseSchema(BaseSchema):
    """Schema for the response of the API endpoint that retrieves all users."""

    id: UUID
    full_name: str
    email: str


class UserResponseSchema(BaseSchema):
    """Schema for the response of API endpoints that return a single user."""

    id: UUID
    full_name: str
    email: str


class CreateUserRequestSchema(BaseSchema):
    """Schema for the request body of the create user endpoint."""

    full_name: str
    email: str
    password: str


class UpdateUserRequestSchema(BaseSchema):
    """Schema for the request body of the update user endpoint."""

    full_name: str
    email: str
    password: str
