"""Query and mutation resolvers for reminder lists."""

from graphql import GraphQLError, GraphQLResolveInfo

from src.health import health
from src.store import add_list, delete_list, get_all_lists, get_list_by_id, rename_list


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
