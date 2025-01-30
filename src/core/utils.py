import hashlib
import datetime as dt
import pytz
from src.core.constants import DATETIME_FORMAT, DEFAULT_TIMEZONE


def generate_hash(s: str) -> str:
    """Generate a hash from a string."""
    return hashlib.md5(s.encode()).hexdigest()


def parse_datetime(
    d: str, format: str = DATETIME_FORMAT, tz: pytz.BaseTzInfo = DEFAULT_TIMEZONE
) -> dt.datetime:
    try:
        parsed_datetime = dt.datetime.strptime(d, format)
        if parsed_datetime.tzinfo is None or parsed_datetime.tzinfo != tz:
            raise ValueError(f"Timestamp '{d}' must be in UTC.")
        return parsed_datetime
    except ValueError as e:
        raise ValueError(
            f"Timestamp '{d}' is not in the correct format ({format}): {e}"
        )


def parse_datetime_to_str(
    d: dt.datetime,
    format: str = DATETIME_FORMAT,
    tz: pytz.BaseTzInfo = DEFAULT_TIMEZONE,
) -> str:
    """Send a datetime to str"""
    try:
        if d.tzinfo is None or d.tzinfo != tz:
            raise ValueError(f"Timestamp {d} must be in UTC.")
        d_str = d.strftime(format=format)
    except Exception as e:
        raise ValueError(f"Can't parse to str as you have error: {e}")
    return d_str
