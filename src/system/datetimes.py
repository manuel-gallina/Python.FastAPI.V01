from datetime import UTC, datetime, tzinfo


def current_datetime() -> datetime:
    """Get the current datetime."""
    return datetime.now(tz=UTC)
