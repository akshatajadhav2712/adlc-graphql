"""GraphQL schema for reminder lists, reminders, and the health query."""

from typing import Any

from graphql import GraphQLObjectType, GraphQLSchema, build_schema, graphql_sync

from src.resolvers import (
    resolve_add_list,
    resolve_add_reminder,
    resolve_complete_reminder,
    resolve_delete_list,
    resolve_health,
    resolve_list,
    resolve_list_reminders,
    resolve_lists,
    resolve_reminders,
    resolve_rename_list,
)

TYPE_DEFS = """
type ReminderList {
  id: String!
  name: String!
  reminders: [Reminder!]!
}

type Reminder {
  id: String!
  listId: String!
  text: String!
  description: String
  dueAt: String!
  done: Boolean!
}

type Query {
  lists: [ReminderList!]!
  list(id: String!): ReminderList
  reminders(listId: String!, includeDone: Boolean = false): [Reminder!]!
  health: HealthStatus!
}

type Mutation {
  addList(name: String!): ReminderList!
  renameList(id: String!, name: String!): ReminderList!
  deleteList(id: String!): Boolean!
  addReminder(listId: String!, text: String!, description: String, dueAt: String!): Reminder!
  completeReminder(id: String!): Reminder!
}

type HealthStatus {
  status: String!
}
"""


def build_graphql_schema() -> GraphQLSchema:
    """Build the schema and attach resolvers."""
    graphql_schema = build_schema(TYPE_DEFS)
    query = graphql_schema.query_type
    mutation = graphql_schema.mutation_type
    if query is None or mutation is None:
        raise RuntimeError("Schema is missing query or mutation type")
    query.fields["lists"].resolve = resolve_lists
    query.fields["list"].resolve = resolve_list
    query.fields["reminders"].resolve = resolve_reminders
    query.fields["health"].resolve = resolve_health
    mutation.fields["addList"].resolve = resolve_add_list
    mutation.fields["renameList"].resolve = resolve_rename_list
    mutation.fields["deleteList"].resolve = resolve_delete_list
    mutation.fields["addReminder"].resolve = resolve_add_reminder
    mutation.fields["completeReminder"].resolve = resolve_complete_reminder
    reminder_list = graphql_schema.get_type("ReminderList")
    if not isinstance(reminder_list, GraphQLObjectType):
        raise RuntimeError("Schema is missing ReminderList type")
    reminder_list.fields["reminders"].resolve = resolve_list_reminders
    return graphql_schema


schema = build_graphql_schema()


def execute_graphql(document: str) -> dict[str, Any]:
    """Run a GraphQL document and return a data/errors payload."""
    result = graphql_sync(schema, document)
    payload: dict[str, Any] = {"data": result.data}
    if result.errors:
        payload["errors"] = [{"message": error.message} for error in result.errors]
    return payload
