"""Unit tests for status validation."""

import pytest

from src.status import validate_status


def test_valid_statuses_unchanged():
    """AC1: Valid statuses are accepted unchanged."""
    assert validate_status("ok") == "ok"
    assert validate_status("degraded") == "degraded"
    assert validate_status("down") == "down"
    assert validate_status("failed") == "failed"


def test_case_insensitive_with_whitespace():
    """AC2: Case-insensitive and whitespace-tolerant."""
    assert validate_status("  OK ") == "ok"
    assert validate_status("DEGRADED") == "degraded"
    assert validate_status("\tDown\n") == "down"
    assert validate_status("  FAILED  ") == "failed"


def test_invalid_status_raises_value_error():
    """AC3: Invalid statuses raise ValueError with specific message."""
    with pytest.raises(ValueError, match="invalid status: broken"):
        validate_status("broken")

    with pytest.raises(ValueError, match="invalid status: unknown"):
        validate_status("unknown")
