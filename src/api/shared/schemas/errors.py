from api.shared.schemas.base import BaseSchema


class ApiError(BaseSchema):
    request_id: str
    code: str
    message: str
    detail: str
