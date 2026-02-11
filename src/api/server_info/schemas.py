from enum import StrEnum

from pydantic import Field

from api.shared.schemas.base import BaseSchema
from api.shared.schemas.datetimes import ApiDatetime


class ServerStatus(StrEnum):
    OK = "ok"
    OFFLINE = "offline"


class DatabaseInfoSchema(BaseSchema):
    status: ServerStatus = Field(description="The status of the database connection.")
    version: str | None = Field(
        default=None, description="The version of the database server, if available."
    )


class SubsystemsInfoSchema(BaseSchema):
    main_db: DatabaseInfoSchema = Field(
        description="Information about the main database."
    )


class GetServerInfoResponseSchema(BaseSchema):
    server_version: str = Field(description="The version of the server application.")
    current_datetime: ApiDatetime = Field(
        description="The current date and time on the server."
    )
    subsystems: SubsystemsInfoSchema = Field(
        description="Information about the server subsystems."
    )
