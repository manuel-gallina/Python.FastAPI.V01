from datetime import datetime
from typing import override
from zoneinfo import ZoneInfo

from api.shared.system.datetimes import IDatetimeProvider

DEFAULT_CURRENT_DATETIME_MOCK = datetime(
    year=2026, month=2, day=11, tzinfo=ZoneInfo("UTC")
)
_current_datetime_mock = DEFAULT_CURRENT_DATETIME_MOCK


class MockDatetimeProvider(IDatetimeProvider):
    """
    A mock datetime provider that returns a fixed predefined datetime.
    This is useful for testing purposes to ensure consistent results regardless of the actual current time.
    """

    @override
    def now(self) -> datetime:
        return _current_datetime_mock

    @staticmethod
    def set_current_datetime(new_datetime: datetime) -> None:
        """
        Set a new datetime to be returned by the now() method.
        This allows tests to simulate different current times as needed.
        """
        global _current_datetime_mock
        _current_datetime_mock = new_datetime
