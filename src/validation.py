"""Validation helpers for reminder lists and reminders."""

from datetime import datetime, timezone

MAX_LIST_NAME_LENGTH = 50
MAX_REMINDER_TEXT_LENGTH = 200
MAX_REMINDER_DESCRIPTION_LENGTH = 500


def is_blank(s: str) -> bool:
    """Return True if the string is empty or contains only whitespace."""
    return s.strip() == ""


def validate_list_name(name: str) -> None:
    """Raise ValueError if name is empty, blank, or longer than 50 characters."""
    if is_blank(name) or len(name) > MAX_LIST_NAME_LENGTH:
        raise ValueError("List name must be between 1 and 50 characters")


def validate_reminder_text(text: str) -> None:
    """Raise ValueError if text is empty, blank, or exceeds 200 characters."""
    if is_blank(text) or len(text) > MAX_REMINDER_TEXT_LENGTH:
        raise ValueError("Reminder text must be between 1 and 200 characters")


def validate_reminder_description(description: str | None) -> str | None:
    """Validate description. Blank values become None. Raise if longer than 500."""
    if description is None or is_blank(description):
        return None
    if len(description) > MAX_REMINDER_DESCRIPTION_LENGTH:
        raise ValueError("Description must not exceed 500 characters")
    return description


def parse_iso8601(date_str: str) -> datetime:
    """Parse an ISO-8601 date-time string. Raise ValueError if invalid."""
    if not isinstance(date_str, str) or date_str.strip() == "":
        raise ValueError("dueAt must be a valid ISO-8601 date-time")
    normalized = date_str[:-1] + "+00:00" if date_str.endswith(("Z", "z")) else date_str
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError("dueAt must be a valid ISO-8601 date-time") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    else:
        parsed = parsed.astimezone(timezone.utc)
    return parsed


def validate_future_date(date_str: str) -> None:
    """Raise ValueError if the date-time is not strictly in the future (UTC)."""
    parsed = parse_iso8601(date_str)
    if parsed <= datetime.now(timezone.utc):
        raise ValueError("dueAt must be in the future")
