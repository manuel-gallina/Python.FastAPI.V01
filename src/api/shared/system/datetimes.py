from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import Depends

from api.shared.system.settings import Settings, get_settings


class DatetimeProvider:
    """
    Provider for retrieving the current datetime based on the application's timezone settings.
    This MUST be used instead of directly calling datetime.now() to ensure that the correct timezone is applied,
    and to ensure it can be overridden in tests.
    """

    settings: Settings

    def __init__(self, settings: Settings = Depends(get_settings)):
        self.settings = settings

    def now(self) -> datetime:
        """Get the current datetime."""
        return datetime.now(tz=ZoneInfo(self.settings.timezone))
