"""Fixtures for testing the query builder."""

import uuid
from collections.abc import Generator
from typing import Any
from unittest.mock import patch

import pytest


class DeterministicUUID:
    """A helper to generate 0001, 0002, etc."""

    def __init__(self) -> None:
        """Initializes the counter to 0."""
        self.counter = 0

    def __call__(self) -> uuid.UUID:
        """Increments the counter and returns a UUID based on the counter value."""
        self.counter += 1
        return uuid.UUID(int=self.counter)


@pytest.fixture(autouse=True)
def seed_uuid(request: pytest.FixtureRequest) -> Generator[None, Any]:
    """Automatically patches uuid.uuid4 for EVERY test.

    Resets the counter to 1 at the start of every test function.

    Args:
        request (pytest.FixtureRequest): The pytest fixture request object,
            used to check for markers on the test function.
    """
    marker = request.node.get_closest_marker("seed_uuid")
    if marker:
        mock_gen = DeterministicUUID()
        with patch(
            "api.shared.system.query_builder.shared.engine.uuid4", side_effect=mock_gen
        ):
            yield
    else:
        yield
