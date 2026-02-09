from api.v1.shared.schemas.base import BaseSchema
from api.v1.shared.schemas.datetimes import ApiDatetime


class GetServerInfoResponseSchema(BaseSchema):
    server_version: str
    main_db_version: str
    current_datetime: ApiDatetime
