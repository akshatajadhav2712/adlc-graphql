"""Validation helpers for reminder list names."""

MAX_LIST_NAME_LENGTH = 50


def is_blank(s: str) -> bool:
    """Return True if the string is empty or contains only whitespace."""
    return s.strip() == ""


def validate_list_name(name: str) -> None:
    """Raise ValueError if name is empty, blank, or longer than 50 characters."""
    if is_blank(name) or len(name) > MAX_LIST_NAME_LENGTH:
        raise ValueError("List name must be between 1 and 50 characters")
