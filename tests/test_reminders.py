"""Tests for reminder queries and mutations."""

import unittest
from datetime import datetime, timedelta, timezone

from src.health import health
from src.schema import execute_graphql
from src.store import clear


def _future_iso(days: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def _reminder_count(list_id: str) -> int:
    result = execute_graphql(
        "query {"
        f'  reminders(listId: "{list_id}") {{ id }}'
        "}"
    )
    assert result["data"] is not None
    return len(result["data"]["reminders"])


class TestReminders(unittest.TestCase):
    """Acceptance tests for addReminder, reminders, completeReminder, and cascade delete."""

    def setUp(self) -> None:
        clear()

    def _add_list(self, name: str = "Home") -> str:
        result = execute_graphql(f'mutation {{ addList(name: "{name}") {{ id }} }}')
        self.assertNotIn("errors", result)
        return result["data"]["addList"]["id"]

    def test_add_reminder_success(self) -> None:
        """REQ-9 / AC5: addReminder creates an open reminder and list.reminders includes it."""
        list_id = self._add_list()
        due_at = _future_iso(1)

        result = execute_graphql(
            "mutation {"
            f'  addReminder(listId: "{list_id}", text: "Pay rent", dueAt: "{due_at}") {{'
            "    id listId text description dueAt done"
            "  }"
            "}"
        )

        self.assertNotIn("errors", result)
        reminder = result["data"]["addReminder"]
        self.assertTrue(reminder["id"])
        self.assertEqual(reminder["text"], "Pay rent")
        self.assertIsNone(reminder["description"])
        self.assertEqual(reminder["dueAt"], due_at)
        self.assertEqual(reminder["listId"], list_id)
        self.assertIs(reminder["done"], False)

        listed = execute_graphql(
            "query {"
            f'  list(id: "{list_id}") {{ reminders {{ id text }} }}'
            "}"
        )
        self.assertEqual(
            listed["data"]["list"]["reminders"],
            [{"id": reminder["id"], "text": "Pay rent"}],
        )

    def test_add_reminder_unknown_list(self) -> None:
        """REQ-10 / AC6: an unknown listId is rejected and adds nothing."""
        due_at = _future_iso(1)
        result = execute_graphql(
            "mutation {"
            f'  addReminder(listId: "unknown", text: "Pay rent", dueAt: "{due_at}") {{ id }}'
            "}"
        )

        self.assertIn("errors", result)
        self.assertIn("not found", result["errors"][0]["message"].lower())
        self.assertEqual(_reminder_count("unknown"), 0)

    def test_add_reminder_empty_text(self) -> None:
        """REQ-10 / AC6: empty text is rejected and adds nothing."""
        list_id = self._add_list()
        due_at = _future_iso(1)
        result = execute_graphql(
            "mutation {"
            f'  addReminder(listId: "{list_id}", text: "", dueAt: "{due_at}") {{ id }}'
            "}"
        )

        self.assertIn("errors", result)
        self.assertIn("1 and 200", result["errors"][0]["message"])
        self.assertEqual(_reminder_count(list_id), 0)

    def test_add_reminder_blank_text(self) -> None:
        """REQ-10 / AC6: whitespace-only text is rejected and adds nothing."""
        list_id = self._add_list()
        due_at = _future_iso(1)
        result = execute_graphql(
            "mutation {"
            f'  addReminder(listId: "{list_id}", text: "   ", dueAt: "{due_at}") {{ id }}'
            "}"
        )

        self.assertIn("errors", result)
        self.assertIn("1 and 200", result["errors"][0]["message"])
        self.assertEqual(_reminder_count(list_id), 0)

    def test_add_reminder_text_too_long(self) -> None:
        """REQ-10 / AC6: text longer than 200 characters is rejected and adds nothing."""
        list_id = self._add_list()
        due_at = _future_iso(1)
        too_long = "a" * 201
        result = execute_graphql(
            "mutation {"
            f'  addReminder(listId: "{list_id}", text: "{too_long}", dueAt: "{due_at}") {{'
            "    id"
            "  }"
            "}"
        )

        self.assertIn("errors", result)
        self.assertIn("1 and 200", result["errors"][0]["message"])
        self.assertEqual(_reminder_count(list_id), 0)

    def test_add_reminder_invalid_date(self) -> None:
        """REQ-10 / AC6: an invalid date is rejected and adds nothing."""
        list_id = self._add_list()
        result = execute_graphql(
            "mutation {"
            f'  addReminder(listId: "{list_id}", text: "Task", dueAt: "not-a-date") {{ id }}'
            "}"
        )

        self.assertIn("errors", result)
        self.assertIn("iso-8601", result["errors"][0]["message"].lower())
        self.assertEqual(_reminder_count(list_id), 0)

    def test_add_reminder_past_date(self) -> None:
        """REQ-10 / AC6: a past date is rejected and adds nothing."""
        list_id = self._add_list()
        result = execute_graphql(
            "mutation {"
            f'  addReminder(listId: "{list_id}", text: "Task", dueAt: "2020-01-01T00:00:00Z") {{'
            "    id"
            "  }"
            "}"
        )

        self.assertIn("errors", result)
        self.assertIn("future", result["errors"][0]["message"].lower())
        self.assertEqual(_reminder_count(list_id), 0)

    def test_reminders_excludes_done_by_default(self) -> None:
        """REQ-11 / AC7: reminders returns open reminders sorted by dueAt, oldest first."""
        list_id = self._add_list()
        later = self._add_reminder(list_id, "Later", _future_iso(3))
        soon = self._add_reminder(list_id, "Soon", _future_iso(1))
        middle = self._add_reminder(list_id, "Middle", _future_iso(2))
        completed = execute_graphql(
            "mutation {"
            f'  completeReminder(id: "{soon["id"]}") {{ id }}'
            "}"
        )
        self.assertNotIn("errors", completed)

        result = execute_graphql(
            "query {"
            f'  reminders(listId: "{list_id}") {{ id text done }}'
            "}"
        )

        self.assertNotIn("errors", result)
        self.assertEqual(
            result["data"]["reminders"],
            [
                {"id": middle["id"], "text": "Middle", "done": False},
                {"id": later["id"], "text": "Later", "done": False},
            ],
        )

    def test_reminders_includes_done_when_requested(self) -> None:
        """REQ-11 / AC7: includeDone true returns open and done reminders sorted by dueAt."""
        list_id = self._add_list()
        later = self._add_reminder(list_id, "Later", _future_iso(3))
        soon = self._add_reminder(list_id, "Soon", _future_iso(1))
        middle = self._add_reminder(list_id, "Middle", _future_iso(2))
        execute_graphql(
            "mutation {"
            f'  completeReminder(id: "{soon["id"]}") {{ id }}'
            "}"
        )

        result = execute_graphql(
            "query {"
            f'  reminders(listId: "{list_id}", includeDone: true) {{ id text done }}'
            "}"
        )

        self.assertNotIn("errors", result)
        self.assertEqual(
            result["data"]["reminders"],
            [
                {"id": soon["id"], "text": "Soon", "done": True},
                {"id": middle["id"], "text": "Middle", "done": False},
                {"id": later["id"], "text": "Later", "done": False},
            ],
        )

    def test_complete_reminder_success(self) -> None:
        """REQ-12 / AC8: completeReminder sets done to true and returns the reminder."""
        list_id = self._add_list()
        created = self._add_reminder(list_id, "Pay rent", _future_iso(1))

        result = execute_graphql(
            "mutation {"
            f'  completeReminder(id: "{created["id"]}") {{'
            "    id listId text done"
            "  }"
            "}"
        )

        self.assertNotIn("errors", result)
        self.assertEqual(
            result["data"]["completeReminder"],
            {
                "id": created["id"],
                "listId": list_id,
                "text": "Pay rent",
                "done": True,
            },
        )
        self.assertEqual(_reminder_count(list_id), 0)
        on_list = execute_graphql(
            "query {"
            f'  list(id: "{list_id}") {{ reminders {{ id done }} }}'
            "}"
        )
        self.assertEqual(
            on_list["data"]["list"]["reminders"],
            [{"id": created["id"], "done": True}],
        )

    def test_complete_reminder_unknown_id(self) -> None:
        """REQ-13 / AC8: an unknown reminder id is rejected and modifies nothing."""
        list_id = self._add_list()
        created = self._add_reminder(list_id, "Pay rent", _future_iso(1))

        result = execute_graphql(
            'mutation { completeReminder(id: "unknown") { id done } }'
        )

        self.assertIn("errors", result)
        self.assertIn("not found", result["errors"][0]["message"].lower())
        open_reminders = execute_graphql(
            "query {"
            f'  reminders(listId: "{list_id}") {{ id done }}'
            "}"
        )
        self.assertEqual(
            open_reminders["data"]["reminders"],
            [{"id": created["id"], "done": False}],
        )

    def test_delete_list_cascades_reminders(self) -> None:
        """REQ-7: deleteList removes the list and every reminder that belonged to it."""
        list_id = self._add_list()
        self._add_reminder(list_id, "Task", _future_iso(1))

        deleted = execute_graphql(f'mutation {{ deleteList(id: "{list_id}") }}')

        self.assertNotIn("errors", deleted)
        self.assertIs(deleted["data"]["deleteList"], True)
        fetched = execute_graphql(f'query {{ list(id: "{list_id}") {{ id }} }}')
        self.assertIsNone(fetched["data"]["list"])
        self.assertEqual(_reminder_count(list_id), 0)

    def test_health_unchanged(self) -> None:
        """REQ-14 / AC9: health() still returns exactly {"status": "ok"}."""
        self.assertEqual(health(), {"status": "ok"})
        result = execute_graphql("query { health { status } }")
        self.assertNotIn("errors", result)
        self.assertEqual(result["data"]["health"], {"status": "ok"})

    def test_story1_operations_unchanged(self) -> None:
        """REQ-14 / AC9: list operations keep their Story 1 shape."""
        created = execute_graphql(
            'mutation { addList(name: "Home") { id name reminders { id } } }'
        )
        self.assertNotIn("errors", created)
        list_id = created["data"]["addList"]["id"]
        self.assertEqual(
            created["data"]["addList"],
            {"id": list_id, "name": "Home", "reminders": []},
        )

        listed = execute_graphql("query { lists { id name reminders { id } } }")
        self.assertEqual(
            listed["data"]["lists"],
            [{"id": list_id, "name": "Home", "reminders": []}],
        )

        fetched = execute_graphql(
            "query {"
            f'  list(id: "{list_id}") {{ id name reminders {{ id }} }}'
            "}"
        )
        self.assertEqual(
            fetched["data"]["list"],
            {"id": list_id, "name": "Home", "reminders": []},
        )

        renamed = execute_graphql(
            "mutation {"
            f'  renameList(id: "{list_id}", name: "Work") {{ id name reminders {{ id }} }}'
            "}"
        )
        self.assertEqual(
            renamed["data"]["renameList"],
            {"id": list_id, "name": "Work", "reminders": []},
        )

        deleted = execute_graphql(f'mutation {{ deleteList(id: "{list_id}") }}')
        self.assertIs(deleted["data"]["deleteList"], True)
        self.assertEqual(execute_graphql("query { lists { id } }")["data"]["lists"], [])

    def test_add_reminder_with_description(self) -> None:
        """REQ-9 / AC5: addReminder stores a provided description."""
        list_id = self._add_list()
        due_at = _future_iso(1)
        result = execute_graphql(
            "mutation {"
            "  addReminder("
            f'    listId: "{list_id}",'
            '    text: "Pay rent",'
            '    description: "Monthly rent payment",'
            f'    dueAt: "{due_at}"'
            "  ) { id description }"
            "}"
        )

        self.assertNotIn("errors", result)
        reminder = result["data"]["addReminder"]
        self.assertEqual(reminder["description"], "Monthly rent payment")
        listed = execute_graphql(
            "query {"
            f'  list(id: "{list_id}") {{ reminders {{ id description }} }}'
            "}"
        )
        self.assertEqual(
            listed["data"]["list"]["reminders"],
            [{"id": reminder["id"], "description": "Monthly rent payment"}],
        )

    def test_add_reminder_description_too_long(self) -> None:
        """REQ-10 / AC6: a description longer than 500 characters is rejected."""
        list_id = self._add_list()
        due_at = _future_iso(1)
        too_long = "x" * 501
        result = execute_graphql(
            "mutation {"
            "  addReminder("
            f'    listId: "{list_id}",'
            '    text: "Task",'
            f'    description: "{too_long}",'
            f'    dueAt: "{due_at}"'
            "  ) { id }"
            "}"
        )

        self.assertIn("errors", result)
        message = result["errors"][0]["message"]
        self.assertTrue("500" in message or "description" in message.lower())
        self.assertEqual(_reminder_count(list_id), 0)

    def _add_reminder(self, list_id: str, text: str, due_at: str) -> dict:
        result = execute_graphql(
            "mutation {"
            f'  addReminder(listId: "{list_id}", text: "{text}", dueAt: "{due_at}") {{'
            "    id text"
            "  }"
            "}"
        )
        self.assertNotIn("errors", result)
        return result["data"]["addReminder"]


if __name__ == "__main__":
    unittest.main()
