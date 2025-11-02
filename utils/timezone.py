"""
Timezone utilities for consistent datetime handling
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from config.settings import settings


def get_local_timezone() -> ZoneInfo:
    """Get configured timezone (default: America/Mexico_City)"""
    return ZoneInfo(settings.timezone)


def now_local() -> datetime:
    """Get current time in local timezone"""
    return datetime.now(get_local_timezone())


def utc_to_local(dt: datetime) -> datetime:
    """Convert UTC datetime to local timezone"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(get_local_timezone())


def local_to_utc(dt: datetime) -> datetime:
    """Convert local datetime to UTC"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=get_local_timezone())
    return dt.astimezone(timezone.utc)


def format_datetime(dt: datetime, include_time: bool = True) -> str:
    """Format datetime in human-readable format"""
    local_dt = utc_to_local(dt) if dt.tzinfo == timezone.utc else dt

    if include_time:
        return local_dt.strftime("%d/%m/%Y %I:%M %p")  # 09/10/2025 09:30 PM
    else:
        return local_dt.strftime("%d/%m/%Y")  # 09/10/2025
