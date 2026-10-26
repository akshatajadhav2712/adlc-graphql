"""GraphQL resolvers for health and the in-memory todo list."""

from graphql import GraphQLError, GraphQLResolveInfo

from src.health import health
from src.todos import add_todo, complete_todo, list_todos


def resolve_health(
    _parent: object | None,
    _info: GraphQLResolveInfo,
) -> dict[str, str]:
    """Return the existing health payload."""
    return health()


def resolve_todos(
    _parent: object | None,
    _info: GraphQLResolveInfo,
) -> list[dict[str, str]]:
    """Return every todo currently in memory."""
    return list_todos()


def resolve_add_todo(
    _parent: object | None,
    _info: GraphQLResolveInfo,
    title: str,
) -> dict[str, str]:
    """Create a todo when the title is non-empty."""
    if title == "":
        raise GraphQLError("Title cannot be empty")
    return add_todo(title)


def resolve_complete_todo(
    _parent: object | None,
    _info: GraphQLResolveInfo,
    id: str,
) -> dict[str, str]:
    """Mark an existing todo done."""
    try:
        return complete_todo(id)
    except ValueError as exc:
        raise GraphQLError(str(exc)) from exc
