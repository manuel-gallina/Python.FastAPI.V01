from api.v1.shared.schemas.base import BaseSchema


class GetServerInfoResponseSchema(BaseSchema):
    server_version: str
