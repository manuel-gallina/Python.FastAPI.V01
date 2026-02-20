"""Schemas for API responses."""

from api.shared.schemas.base import BaseSchema


class ErrorResponseSchema(BaseSchema):
    """Schema for the response of an API endpoint when an error occurs."""


class ObjectResponseSchema[DataT: BaseSchema](BaseSchema):
    """Schema for the response of an API endpoint that returns a single object."""

    data: DataT


class ListResponseSchema[DataT: BaseSchema](BaseSchema):
    """Schema for the response of an API endpoint that returns a list of objects."""

    class MetaSchema(BaseSchema):
        """Schema for the metadata of a list response."""

        count: int

    data: list[DataT]
    meta: MetaSchema
