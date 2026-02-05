from api.v1.shared.schemas.base import BaseSchema


class ErrorResponseSchema(BaseSchema):
    pass


class ObjectResponseSchema[DataT: BaseSchema](BaseSchema):
    data: DataT


class ListResponseSchema[DataT: BaseSchema](BaseSchema):
    class MetaSchema(BaseSchema):
        count: int

    data: list[DataT]
    meta: MetaSchema
