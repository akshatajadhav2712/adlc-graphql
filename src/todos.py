"""In-memory todo list. Cleared when the process starts."""

import uuid
from typing import TypedDict


class Todo(TypedDict):
    id: str
    title: str
    done: str


todos_store: list[Todo] = []


def list_todos() -> list[Todo]:
    """Return the todos currently held in memory."""
    return list(todos_store)


def add_todo(title: str) -> Todo:
    """Append a new not-done todo and return it.

    The caller rejects an empty title before this creates the object.
    """
    todo: Todo = {
        "id": str(uuid.uuid4()),
        "title": title,
        "done": "not_done",
    }
    todos_store.append(todo)
    return todo


def complete_todo(todo_id: str) -> Todo:
    """Mark the todo with ``todo_id`` as done.

    Raises:
        ValueError: if no stored todo has that id.
    """
    for todo in todos_store:
        if todo["id"] == todo_id:
            todo["done"] = "done"
            return todo
    raise ValueError("Todo not found")
