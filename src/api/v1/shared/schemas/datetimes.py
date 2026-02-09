from datetime import datetime
from typing import Annotated

from pydantic import PlainSerializer


def serialize_datetime(dt: datetime) -> str:
    """Serialize a datetime object to an ISO 8601 string."""
    return dt.isoformat()

ApiDatetime = Annotated[
    datetime,
    PlainSerializer(
        serialize_datetime,
        return_type=str,
        when_used="json",
    ),
]
