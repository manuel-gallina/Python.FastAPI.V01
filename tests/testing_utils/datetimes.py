from datetime import datetime
from zoneinfo import ZoneInfo


class MockDatetimeProvider:
    """
    A mock datetime provider that returns a fixed predefined datetime.
    This is useful for testing purposes to ensure consistent results regardless of the actual current time.
    """

    @staticmethod
    def now() -> datetime:
        """Get the current datetime."""
        return datetime(year=2026, month=2, day=11, tzinfo=ZoneInfo("UTC"))
