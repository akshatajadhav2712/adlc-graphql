"""Health check for the graphql service."""

from typing import TypedDict

from src.status import validate_status


class HealthStatus(TypedDict):
    status: str


def health(status: str = "ok") -> HealthStatus:
    """Return health check response with validated status.

    Args:
        status: Health status (default: "ok")

    Returns:
        Dictionary with validated status

    Raises:
        ValueError: If status is invalid

    Example:
        >>> health()
        {'status': 'ok'}
    """
    return {"status": validate_status(status)}
