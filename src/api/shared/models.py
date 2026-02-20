"""Shared models for the API."""

from pydantic import BaseModel, ConfigDict


class BaseDbModel(BaseModel):
    """Base model for database entities."""

    model_config = ConfigDict(from_attributes=True)
