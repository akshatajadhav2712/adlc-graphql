"""Status validation for health check values."""

# Allowed status values
ALLOWED_STATUSES = {"ok", "degraded", "down", "failed"}


def validate_status(value: str) -> str:
    """Validate and normalize a status value.

    Args:
        value: Status string to validate

    Returns:
        Normalized status (lowercased and stripped)

    Raises:
        ValueError: If status is not in ALLOWED_STATUSES
    """
    normalized = value.strip().lower()
    if normalized not in ALLOWED_STATUSES:
        raise ValueError(f"invalid status: {value}")
    return normalized
