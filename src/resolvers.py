"""Query and mutation resolvers for reminder lists and reminders."""

from graphql import GraphQLError, GraphQLResolveInfo

from src.health import health
from src.store import (
    add_list,
    add_reminder,
    complete_reminder,
    delete_list,
    get_all_lists,
    get_list_by_id,
    get_reminders_for_list,
    rename_list,
)


def resolve_lists(
    _parent: object | None,
    _info: GraphQLResolveInfo,
) -> list[dict]:
    """Return all reminder lists sorted by name (case-insensitive)."""
    return get_all_lists()


def resolve_list(
    _parent: object | None,
    _info: GraphQLResolveInfo,
    id: str,
) -> dict | None:
    """Return one list by id, or None if not found."""
    return get_list_by_id(id)


def resolve_health(
    _parent: object | None,
    _info: GraphQLResolveInfo,
) -> dict:
    """Return {"status": "ok"}."""
    return health()


def resolve_add_list(
    _parent: object | None,
    _info: GraphQLResolveInfo,
    name: str,
) -> dict:
    """Create a new list. Raise GraphQLError on validation failure."""
    try:
        return add_list(name)
    except ValueError as exc:
        raise GraphQLError(str(exc)) from exc


def resolve_rename_list(
    _parent: object | None,
    _info: GraphQLResolveInfo,
    id: str,
    name: str,
) -> dict:
    """Rename a list. Raise GraphQLError if the id is unknown or the name is taken."""
    try:
        return rename_list(id, name)
    except ValueError as exc:
        raise GraphQLError(str(exc)) from exc


def resolve_delete_list(
    _parent: object | None,
    _info: GraphQLResolveInfo,
    id: str,
) -> bool:
    """Delete a list and its reminders. Raise GraphQLError if the id is unknown."""
    try:
        return delete_list(id)
    except ValueError as exc:
        raise GraphQLError(str(exc)) from exc


def resolve_reminders(
    _parent: object | None,
    _info: GraphQLResolveInfo,
    listId: str,
    includeDone: bool = False,
) -> list[dict]:
    """Return reminders of one list sorted by dueAt, oldest first.

    Done reminders are omitted unless includeDone is True.
    """
    return get_reminders_for_list(listId, include_done=includeDone)


def resolve_list_reminders(
    parent: dict,
    _info: GraphQLResolveInfo,
) -> list[dict]:
    """Return every reminder on a list, done and open, sorted by dueAt."""
    return get_reminders_for_list(parent["id"], include_done=True)


def resolve_add_reminder(
    _parent: object | None,
    _info: GraphQLResolveInfo,
    listId: str,
    text: str,
    dueAt: str,
    description: str | None = None,
) -> dict:
    """Create a reminder. Raise GraphQLError on validation failure."""
    try:
        return add_reminder(listId, text, dueAt, description)
    except ValueError as exc:
        raise GraphQLError(str(exc)) from exc


def resolve_complete_reminder(
    _parent: object | None,
    _info: GraphQLResolveInfo,
    id: str,
) -> dict:
    """Set done to True. Raise GraphQLError if the id is unknown."""
    try:
        return complete_reminder(id)
    except ValueError as exc:
        raise GraphQLError(str(exc)) from exc
