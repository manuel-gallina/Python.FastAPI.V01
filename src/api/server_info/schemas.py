"""Schemas for the server information endpoint."""

from enum import StrEnum

from pydantic import Field

from api.shared.schemas.base import BaseSchema
from api.shared.schemas.datetimes import ApiDatetime


class ServerStatus(StrEnum):
    """Status of a server subsystem."""

    OK = "ok"
    OFFLINE = "offline"


class DatabaseInfoSchema(BaseSchema):
    """Schema for information about a database subsystem."""

    status: ServerStatus = Field(description="The status of the database connection.")
    version: str | None = Field(
        default=None, description="The version of the database server, if available."
    )


class SubsystemsInfoSchema(BaseSchema):
    """Schema for information about the server subsystems."""

    main_db: DatabaseInfoSchema = Field(
        description="Information about the main database."
    )


class GetServerInfoResponseSchema(BaseSchema):
    """Schema for the response of the API endpoint that retrieves server information."""

    server_version: str = Field(description="The version of the server application.")
    current_datetime: ApiDatetime = Field(
        description="The current date and time on the server."
    )
    subsystems: SubsystemsInfoSchema = Field(
        description="Information about the server subsystems."
    )
