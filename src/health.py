"""Health check for the graphql service."""

from typing import TypedDict


class HealthStatus(TypedDict):
    status: str


def health() -> HealthStatus:
    """Return the health status of the service.

    Returns:
        dict: A dictionary with key "status" and value "ok"

    Example:
        >>> health()
        {'status': 'ok'}
    """
    return {"status": "ok"}
