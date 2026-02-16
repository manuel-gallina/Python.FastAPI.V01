from uuid import UUID

from api.shared.schemas.base import BaseSchema


class GetAllUsersResponseSchema(BaseSchema):
    id: UUID
    full_name: str
    email: str
