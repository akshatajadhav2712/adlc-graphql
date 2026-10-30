"""Unit tests for the health check function."""

import pytest

from src.health import health


def test_health_default():
    """Existing test: health() returns ok."""
    result = health()
    assert result == {"status": "ok"}


def test_health_returns_ok_status() -> None:
    """Verify health() returns {"status": "ok"}."""
    result = health()
    assert result == {"status": "ok"}


def test_health_with_explicit_status():
    """AC4: Health function uses validated status."""
    assert health("down") == {"status": "down"}
    assert health("degraded") == {"status": "degraded"}
    assert health("failed") == {"status": "failed"}
    assert health("  OK ") == {"status": "ok"}


def test_health_with_invalid_status():
    """AC5: Health function propagates validation errors."""
    with pytest.raises(ValueError, match="invalid status: broken"):
        health("broken")
