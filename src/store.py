"""In-memory storage for reminder lists and reminders."""

from uuid import uuid4

from src.validation import (
    parse_iso8601,
    validate_future_date,
    validate_list_name,
    validate_reminder_description,
    validate_reminder_text,
)

# Module-level storage (cleared on process restart).
_lists: dict[str, dict] = {}  # keyed by list id
_name_index: dict[str, str] = {}  # lowercase name -> list id
_reminders: dict[str, dict] = {}  # keyed by reminder id
_list_reminders: dict[str, list[str]] = {}  # list id -> reminder ids


def clear() -> None:
    """Remove every list and reminder. Tests use this to isolate cases."""
    _lists.clear()
    _name_index.clear()
    _reminders.clear()
    _list_reminders.clear()


def get_all_lists() -> list[dict]:
    """Return all lists sorted by name (case-insensitive)."""
    return sorted(_lists.values(), key=lambda item: item["name"].lower())


def get_list_by_id(list_id: str) -> dict | None:
    """Return a list by id, or None if not found."""
    return _lists.get(list_id)


def add_list(name: str) -> dict:
    """Create a list with a unique id and empty reminders.

    Raises ValueError when the name is blank, too long, or already used.
    """
    validate_list_name(name)
    normalized = _normalize_name(name)
    if normalized in _name_index:
        raise ValueError("List name already exists")
    list_id = str(uuid4())
    list_dict = {"id": list_id, "name": name, "reminders": []}
    _lists[list_id] = list_dict
    _name_index[normalized] = list_id
    return list_dict


def rename_list(list_id: str, new_name: str) -> dict:
    """Update a list name.

    Raises ValueError if the id is unknown, the name is invalid, or the name
    duplicates another list.
    """
    validate_list_name(new_name)
    list_dict = get_list_by_id(list_id)
    if list_dict is None:
        raise ValueError("List not found")
    normalized = _normalize_name(new_name)
    existing_id = _name_index.get(normalized)
    if existing_id is not None and existing_id != list_id:
        raise ValueError("List name already exists")
    old_normalized = _normalize_name(list_dict["name"])
    del _name_index[old_normalized]
    list_dict["name"] = new_name
    _name_index[normalized] = list_id
    return list_dict


def get_reminders_for_list(list_id: str, include_done: bool = False) -> list[dict]:
    """Return reminders for a list sorted by dueAt, oldest first.

    Done reminders are omitted unless include_done is True.
    """
    reminder_ids = _list_reminders.get(list_id, [])
    reminders_list = [_reminders[reminder_id] for reminder_id in reminder_ids]
    if not include_done:
        reminders_list = [item for item in reminders_list if not item["done"]]
    return sorted(reminders_list, key=lambda item: parse_iso8601(item["dueAt"]))


def get_reminder_by_id(reminder_id: str) -> dict | None:
    """Return a reminder by id, or None if not found."""
    return _reminders.get(reminder_id)


def add_reminder(
    list_id: str,
    text: str,
    due_at: str,
    description: str | None = None,
) -> dict:
    """Create a reminder with a unique id and done False.

    Raises ValueError when the list is unknown or text, description, or dueAt
    fail validation.
    """
    if get_list_by_id(list_id) is None:
        raise ValueError("List not found")
    validate_reminder_text(text)
    normalized_description = validate_reminder_description(description)
    parse_iso8601(due_at)
    validate_future_date(due_at)
    reminder_id = str(uuid4())
    reminder_dict = {
        "id": reminder_id,
        "listId": list_id,
        "text": text,
        "description": normalized_description,
        "dueAt": due_at,
        "done": False,
    }
    _reminders[reminder_id] = reminder_dict
    _list_reminders.setdefault(list_id, []).append(reminder_id)
    return reminder_dict


def complete_reminder(reminder_id: str) -> dict:
    """Set done to True. Raise ValueError if the id is unknown."""
    reminder_dict = get_reminder_by_id(reminder_id)
    if reminder_dict is None:
        raise ValueError("Reminder not found")
    reminder_dict["done"] = True
    return reminder_dict


def delete_list(list_id: str) -> bool:
    """Delete a list and its reminders.

    Raises ValueError if the id is unknown. Returns True on success.
    """
    list_dict = get_list_by_id(list_id)
    if list_dict is None:
        raise ValueError("List not found")
    for reminder_id in _list_reminders.get(list_id, []):
        del _reminders[reminder_id]
    if list_id in _list_reminders:
        del _list_reminders[list_id]
    normalized = _normalize_name(list_dict["name"])
    del _name_index[normalized]
    del _lists[list_id]
    return True


def _normalize_name(name: str) -> str:
    """Lowercase and strip whitespace for case-insensitive comparison."""
    return name.strip().lower()
