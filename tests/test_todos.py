"""Tests for the in-memory GraphQL todo list."""

import unittest

from src.schema import execute
from src.todos import todos_store


class TestTodos(unittest.TestCase):
    """Acceptance tests for todos, addTodo, completeTodo, and health."""

    def setUp(self) -> None:
        todos_store.clear()

    def test_add_todo_with_valid_title(self) -> None:
        """AC1: addTodo creates a not-done todo with a non-empty id."""
        result = execute('mutation { addTodo(title: "Buy milk") { id title done } }')

        self.assertFalse(result.errors)
        assert result.data is not None
        todo = result.data["addTodo"]
        self.assertEqual(todo["title"], "Buy milk")
        self.assertEqual(todo["done"], "not_done")
        self.assertTrue(todo["id"])

    def test_todos_query_returns_all_todos(self) -> None:
        """AC2: todos returns every todo that was added."""
        created = execute('mutation { addTodo(title: "Buy milk") { id } }')
        assert created.data is not None
        created_id = created.data["addTodo"]["id"]

        result = execute("{ todos { id title done } }")

        self.assertFalse(result.errors)
        assert result.data is not None
        self.assertEqual(
            result.data["todos"],
            [{"id": created_id, "title": "Buy milk", "done": "not_done"}],
        )

    def test_complete_todo_marks_as_done(self) -> None:
        """AC3: completeTodo sets done to done for the matching id."""
        created = execute('mutation { addTodo(title: "Buy milk") { id } }')
        assert created.data is not None
        created_id = created.data["addTodo"]["id"]

        result = execute(
            "mutation {"
            f'  completeTodo(id: "{created_id}") {{ id title done }}'
            "}"
        )

        self.assertFalse(result.errors)
        assert result.data is not None
        self.assertEqual(
            result.data["completeTodo"],
            {"id": created_id, "title": "Buy milk", "done": "done"},
        )

    def test_add_todo_with_empty_title_rejected(self) -> None:
        """AC4: an empty title is a GraphQL error and stores nothing."""
        result = execute('mutation { addTodo(title: "") { id title done } }')

        self.assertTrue(result.errors)
        assert result.errors is not None
        self.assertEqual(result.errors[0].message, "Title cannot be empty")
        self.assertEqual(todos_store, [])

        listed = execute("{ todos { id } }")
        assert listed.data is not None
        self.assertEqual(listed.data["todos"], [])

    def test_complete_todo_with_unknown_id_rejected(self) -> None:
        """AC5: an unknown id is a GraphQL error."""
        result = execute(
            'mutation { completeTodo(id: "nonexistent") { id title done } }'
        )

        self.assertTrue(result.errors)
        assert result.errors is not None
        self.assertEqual(result.errors[0].message, "Todo not found")

    def test_health_unchanged(self) -> None:
        """AC6: health still returns status ok alongside the todo operations."""
        result = execute("{ health { status } }")

        self.assertFalse(result.errors)
        assert result.data is not None
        self.assertEqual(result.data["health"], {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
