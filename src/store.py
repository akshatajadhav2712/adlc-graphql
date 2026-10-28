"""In-memory storage for reminder lists."""

from uuid import uuid4

from src.validation import validate_list_name

# Module-level storage (cleared on process restart).
_lists: dict[str, dict] = {}  # keyed by list id
_name_index: dict[str, str] = {}  # lowercase name -> list id


def clear() -> None:
    """Remove every list. Tests use this to isolate cases."""
    _lists.clear()
    _name_index.clear()


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


def delete_list(list_id: str) -> bool:
    """Delete a list and its reminders.

    Raises ValueError if the id is unknown. Returns True on success.
    """
    list_dict = get_list_by_id(list_id)
    if list_dict is None:
        raise ValueError("List not found")
    normalized = _normalize_name(list_dict["name"])
    del _name_index[normalized]
    del _lists[list_id]
    return True


def _normalize_name(name: str) -> str:
    """Lowercase and strip whitespace for case-insensitive comparison."""
    return name.strip().lower()
