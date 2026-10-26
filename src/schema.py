"""Executable GraphQL schema for health and todos."""

from graphql import GraphQLSchema, build_schema, graphql_sync
from graphql.execution import ExecutionResult

from src.resolvers import (
    resolve_add_todo,
    resolve_complete_todo,
    resolve_health,
    resolve_todos,
)

TYPE_DEFS = """
enum DoneStatus {
  done
  not_done
}

type Todo {
  id: String!
  title: String!
  done: DoneStatus!
}

type HealthResponse {
  status: String!
}

type Query {
  health: HealthResponse!
  todos: [Todo!]!
}

type Mutation {
  addTodo(title: String!): Todo!
  completeTodo(id: String!): Todo!
}
"""


def build_graphql_schema() -> GraphQLSchema:
    """Build the schema and attach resolvers."""
    graphql_schema = build_schema(TYPE_DEFS)
    query = graphql_schema.query_type
    mutation = graphql_schema.mutation_type
    if query is None or mutation is None:
        raise RuntimeError("Schema is missing query or mutation type")
    query.fields["health"].resolve = resolve_health
    query.fields["todos"].resolve = resolve_todos
    mutation.fields["addTodo"].resolve = resolve_add_todo
    mutation.fields["completeTodo"].resolve = resolve_complete_todo
    return graphql_schema


schema = build_graphql_schema()


def execute(document: str) -> ExecutionResult:
    """Run a GraphQL document against the service schema."""
    return graphql_sync(schema, document)
