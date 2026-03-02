"""Query parameters for the query builder."""

import json
from typing import Annotated, Any, Callable

from fastapi import Depends, status
from fastapi.params import Query
from pydantic import BaseModel

from api.shared.schemas.errors import ApiError, UnprocessableContentErrorSchema
from api.shared.system.request_tracing import get_request_id


def get_filters(
    request_id: Annotated[str, Depends(get_request_id)],
    filters: Annotated[str | None, Query()] = None,
) -> dict[str, Any] | None:
    """Extracts the 'filters' query parameter from the request.

    Args:
        request_id (str): The unique identifier for the request,
            used for tracing and logging.
        filters (str | None): The 'filters' query parameter.

    Returns:
        dict[str, Any] | None: The filters as a dictionary if provided, None otherwise.
    """
    if isinstance(filters, str):
        try:
            return json.loads(filters)
        except json.JSONDecodeError as e:
            error = "Invalid 'filters' query parameter. Must be a valid JSON string."
            raise ApiError(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                UnprocessableContentErrorSchema(
                    request_id=request_id, message=error, detail=error
                ),
            ) from e
    return None


def get_sort(
    request_id: Annotated[str, Depends(get_request_id)],
    sort: Annotated[str | None, Query()] = None,
) -> list[dict[str, Any]] | None:
    """Extracts the 'sort' query parameter from the request.

    Args:
        request_id (str): The unique identifier for the request,
            used for tracing and logging.
        sort (str | None): The 'sort' query parameter.

    Returns:
        list[dict[str, Any]] | None: The sort options if provided, None otherwise.
    """
    if isinstance(sort, str):
        try:
            return json.loads(sort)
        except json.JSONDecodeError as e:
            error = "Invalid 'sort' query parameter. Must be a valid JSON string."
            raise ApiError(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                UnprocessableContentErrorSchema(
                    request_id=request_id, message=error, detail=error
                ),
            ) from e
    return None


class PaginationParams(BaseModel):
    """Pagination parameters."""

    skip: int
    limit: int


def get_pagination(
    request_id: Annotated[str, Depends(get_request_id)],
    skip: Annotated[int | None, Query()],
    limit: Annotated[int | None, Query()],
) -> Callable[[...], PaginationParams]:
    pass
