"""Module for providing the current application datetime."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Annotated, override
from zoneinfo import ZoneInfo

from fastapi import Depends

from api.shared.system.settings import Settings, get_settings


class IDatetimeProvider(ABC):
    """Interface for a provider that retrieves the current datetime."""

    @abstractmethod
    def now(self) -> datetime:
        """Get the current datetime."""
        raise NotImplementedError


class DatetimeProvider(IDatetimeProvider):
    """Provider for retrieving the current datetime.

    The datetime is based on the application's timezone settings.
    This MUST be used instead of directly calling datetime.now()
    to ensure that the correct timezone is applied, and to ensure
    it can be overridden in tests.
    """

    settings: Settings

    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]) -> None:
        """Initialize the DatetimeProvider with the application settings.

        Args:
            settings (Settings): The application settings,
                which include the timezone information.
        """
        self.settings = settings

    @override
    def now(self) -> datetime:
        return datetime.now(tz=ZoneInfo(self.settings.timezone))
