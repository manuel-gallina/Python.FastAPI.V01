"""Module containing the User model for the authentication system."""

from uuid import UUID

from api.shared.models import BaseDbModel


class User(BaseDbModel):
    """Model representing a user in the authentication system."""

    id: UUID
    full_name: str
    email: str
    password_hash: str
