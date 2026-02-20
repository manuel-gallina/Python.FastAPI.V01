"""Utility functions and types for handling datetime fields in API response models."""

from datetime import datetime
from typing import Annotated

from pydantic import PlainSerializer


def serialize_datetime(dt: datetime) -> str:
    """Serialize a datetime object to an ISO 8601 string.

    Args:
        dt (datetime): The datetime object to serialize.

    Returns:
        str: The ISO 8601 string representation of the datetime.
    """
    return dt.isoformat()


ApiDatetime = Annotated[
    datetime, PlainSerializer(serialize_datetime, return_type=str, when_used="json")
]
"""
    A datetime field that is serialized to an ISO 8601 string in JSON responses.

    This type MUST be used for all datetime fields in API response models to ensure
    consistent serialization across the API.
"""
