from api.shared.schemas.base import BaseSchema


class GetAllUsersResponseSchema(BaseSchema):
    id: int
    full_name: str
    email: str
