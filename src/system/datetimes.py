from datetime import datetime
from zoneinfo import ZoneInfo

from system.settings import get_settings


def current_datetime() -> datetime:
    """Get the current datetime."""
    settings = get_settings()
    return datetime.now(tz=ZoneInfo(settings.timezone))
