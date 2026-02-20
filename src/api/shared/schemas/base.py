"""Base schema for API request and response models."""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    """Base schema for all API request and response schemas.

    This MUST be extended to create specific request and response schemas,
    ensuring consistency across the API.

    It is configured to generate field aliases using camelCase convention.
    """

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, serialize_by_alias=True
    )
