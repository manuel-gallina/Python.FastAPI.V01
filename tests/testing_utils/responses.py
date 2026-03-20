"""Utility functions for asserting API response shapes."""

from httpx import Response


def assert_error_response(
    response: Response, *, code: str, message: str, detail: str
) -> None:
    """Assert that an error response matches the expected API error format.

    Verifies the response body contains all required error fields with the
    correct values. The requestId field is checked for the expected prefix
    but not for an exact value, as it is generated per request.

    Args:
        response (Response): The HTTP response to assert against.
        code (str): The expected error code (e.g. "NOT_FOUND_404").
        message (str): The expected human-readable error message.
        detail (str): The expected detailed error description.
    """
    body = response.json()
    error = body["error"]
    assert error["requestId"].startswith("REQ_")
    assert error["code"] == code
    assert error["message"] == message
    assert error["detail"] == detail
