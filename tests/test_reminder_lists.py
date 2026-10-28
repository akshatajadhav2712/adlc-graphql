"""Tests for reminder list queries and mutations."""

import unittest

from src.health import health
from src.schema import execute_graphql
from src.store import clear


def _list_count() -> int:
    result = execute_graphql("query { lists { id } }")
    assert result["data"] is not None
    return len(result["data"]["lists"])


class TestReminderLists(unittest.TestCase):
    """Acceptance tests for lists, list, addList, renameList, and deleteList."""

    def setUp(self) -> None:
        clear()

    def test_lists_empty_initially(self) -> None:
        """REQ-1: lists returns an empty array on startup."""
        result = execute_graphql("query { lists { id name reminders { id } } }")

        self.assertNotIn("errors", result)
        self.assertEqual(result["data"]["lists"], [])

    def test_lists_includes_added_list(self) -> None:
        """REQ-1: lists includes added lists sorted by name, case-insensitive."""
        execute_graphql('mutation { addList(name: "banana") { id } }')
        execute_graphql('mutation { addList(name: "Home") { id } }')
        execute_graphql('mutation { addList(name: "Apple") { id } }')

        result = execute_graphql("query { lists { name reminders { id } } }")

        self.assertNotIn("errors", result)
        names = [item["name"] for item in result["data"]["lists"]]
        self.assertEqual(names, ["Apple", "banana", "Home"])
        self.assertTrue(all(item["reminders"] == [] for item in result["data"]["lists"]))

    def test_list_by_id_valid(self) -> None:
        """REQ-2: list(id) returns the list with that id."""
        created = execute_graphql('mutation { addList(name: "Home") { id } }')
        list_id = created["data"]["addList"]["id"]

        result = execute_graphql(
            "query {"
            f'  list(id: "{list_id}") {{ id name reminders {{ id }} }}'
            "}"
        )

        self.assertNotIn("errors", result)
        self.assertEqual(
            result["data"]["list"],
            {"id": list_id, "name": "Home", "reminders": []},
        )

    def test_list_by_id_unknown(self) -> None:
        """REQ-2: list(id) returns null when the id is unknown."""
        result = execute_graphql('query { list(id: "unknown") { id name } }')

        self.assertNotIn("errors", result)
        self.assertIsNone(result["data"]["list"])

    def test_add_list_success(self) -> None:
        """REQ-3: addList creates a list with a unique id, the given name, and no reminders."""
        result = execute_graphql(
            'mutation { addList(name: "Home") { id name reminders { id } } }'
        )

        self.assertNotIn("errors", result)
        created = result["data"]["addList"]
        self.assertEqual(created["name"], "Home")
        self.assertEqual(created["reminders"], [])
        self.assertTrue(created["id"])
        self.assertEqual(_list_count(), 1)

    def test_add_list_empty_name(self) -> None:
        """REQ-4: an empty name is rejected and adds nothing."""
        result = execute_graphql('mutation { addList(name: "") { id } }')

        self.assertIn("errors", result)
        self.assertIn("1 and 50", result["errors"][0]["message"])
        self.assertEqual(_list_count(), 0)

    def test_add_list_blank_name(self) -> None:
        """REQ-4: a whitespace-only name is rejected and adds nothing."""
        result = execute_graphql('mutation { addList(name: "   ") { id } }')

        self.assertIn("errors", result)
        self.assertIn("1 and 50", result["errors"][0]["message"])
        self.assertEqual(_list_count(), 0)

    def test_add_list_name_too_long(self) -> None:
        """REQ-4: a name longer than 50 characters is rejected and adds nothing."""
        too_long = "a" * 51
        result = execute_graphql(f'mutation {{ addList(name: "{too_long}") {{ id }} }}')

        self.assertIn("errors", result)
        self.assertIn("1 and 50", result["errors"][0]["message"])
        self.assertEqual(_list_count(), 0)

    def test_add_list_duplicate_name_exact(self) -> None:
        """REQ-4: an exact duplicate name is rejected and adds nothing."""
        execute_graphql('mutation { addList(name: "Home") { id } }')

        result = execute_graphql('mutation { addList(name: "Home") { id } }')

        self.assertIn("errors", result)
        self.assertIn("already exists", result["errors"][0]["message"].lower())
        self.assertEqual(_list_count(), 1)

    def test_add_list_duplicate_name_case_insensitive(self) -> None:
        """REQ-4: a case-insensitive duplicate name is rejected and adds nothing."""
        execute_graphql('mutation { addList(name: "Home") { id } }')

        result = execute_graphql('mutation { addList(name: "home") { id } }')

        self.assertIn("errors", result)
        self.assertIn("already exists", result["errors"][0]["message"].lower())
        self.assertEqual(_list_count(), 1)

    def test_rename_list_success(self) -> None:
        """REQ-5: renameList changes the name and returns the updated list."""
        created = execute_graphql('mutation { addList(name: "Home") { id } }')
        list_id = created["data"]["addList"]["id"]

        result = execute_graphql(
            "mutation {"
            f'  renameList(id: "{list_id}", name: "Work") {{ id name reminders {{ id }} }}'
            "}"
        )

        self.assertNotIn("errors", result)
        self.assertEqual(
            result["data"]["renameList"],
            {"id": list_id, "name": "Work", "reminders": []},
        )
        listed = execute_graphql("query { lists { id name } }")
        self.assertEqual(listed["data"]["lists"], [{"id": list_id, "name": "Work"}])

    def test_rename_list_unknown_id(self) -> None:
        """REQ-6: renaming an unknown id is rejected and modifies nothing."""
        created = execute_graphql('mutation { addList(name: "Home") { id } }')
        list_id = created["data"]["addList"]["id"]

        result = execute_graphql(
            'mutation { renameList(id: "unknown", name: "Work") { id name } }'
        )

        self.assertIn("errors", result)
        self.assertIn("not found", result["errors"][0]["message"].lower())
        listed = execute_graphql("query { lists { id name } }")
        self.assertEqual(listed["data"]["lists"], [{"id": list_id, "name": "Home"}])

    def test_rename_list_duplicate_name(self) -> None:
        """REQ-6: renaming to another list's name is rejected and modifies nothing."""
        home = execute_graphql('mutation { addList(name: "Home") { id } }')
        work = execute_graphql('mutation { addList(name: "Work") { id } }')
        home_id = home["data"]["addList"]["id"]
        work_id = work["data"]["addList"]["id"]

        result = execute_graphql(
            "mutation {"
            f'  renameList(id: "{work_id}", name: "Home") {{ id name }}'
            "}"
        )

        self.assertIn("errors", result)
        self.assertIn("already exists", result["errors"][0]["message"].lower())
        listed = execute_graphql("query { lists { id name } }")
        self.assertEqual(
            listed["data"]["lists"],
            [
                {"id": home_id, "name": "Home"},
                {"id": work_id, "name": "Work"},
            ],
        )

    def test_delete_list_success(self) -> None:
        """REQ-7: deleteList removes the list and returns true."""
        created = execute_graphql('mutation { addList(name: "Home") { id } }')
        list_id = created["data"]["addList"]["id"]

        result = execute_graphql(f'mutation {{ deleteList(id: "{list_id}") }}')

        self.assertNotIn("errors", result)
        self.assertIs(result["data"]["deleteList"], True)
        self.assertEqual(_list_count(), 0)
        fetched = execute_graphql(f'query {{ list(id: "{list_id}") {{ id }} }}')
        self.assertIsNone(fetched["data"]["list"])

    def test_delete_list_unknown_id(self) -> None:
        """REQ-8: deleting an unknown id is rejected and modifies nothing."""
        created = execute_graphql('mutation { addList(name: "Home") { id } }')
        list_id = created["data"]["addList"]["id"]

        result = execute_graphql('mutation { deleteList(id: "unknown") }')

        self.assertIn("errors", result)
        self.assertIn("not found", result["errors"][0]["message"].lower())
        listed = execute_graphql("query { lists { id name } }")
        self.assertEqual(listed["data"]["lists"], [{"id": list_id, "name": "Home"}])

    def test_health_unchanged(self) -> None:
        """REQ-14: health() still returns exactly {"status": "ok"}."""
        self.assertEqual(health(), {"status": "ok"})

        result = execute_graphql("query { health { status } }")

        self.assertNotIn("errors", result)
        self.assertEqual(result["data"]["health"], {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
