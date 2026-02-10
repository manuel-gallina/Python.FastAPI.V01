from enum import StrEnum

from api.shared.schemas.base import BaseSchema
from api.shared.schemas.datetimes import ApiDatetime


class ServerStatus(StrEnum):
    OK = "ok"
    OFFLINE = "offline"


class DatabaseInfoSchema(BaseSchema):
    status: ServerStatus
    version: str | None


class SubsystemsInfoSchema(BaseSchema):
    main_db: DatabaseInfoSchema


class GetServerInfoResponseSchema(BaseSchema):
    server_version: str
    current_datetime: ApiDatetime
    subsystems: SubsystemsInfoSchema
