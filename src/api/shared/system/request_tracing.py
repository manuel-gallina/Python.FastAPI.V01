"""Request tracing utilities."""

from uuid import uuid4

from fastapi import Request


def init_request_id(request: Request) -> None:
    """Assign an ID to the current request.

    Args:
        request (Request): The FastAPI request object.
    """
    request.state.request_id = f"REQ_{uuid4().hex}"


def get_request_id(request: Request) -> str:
    """Extract the request ID from the request headers.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        str: The ID assigned to the current request.
    """
    return request.state.request_id
