"""Unit tests for the health check function."""

import unittest

from src.health import health


class TestHealth(unittest.TestCase):
    """Test suite for health check function."""

    def test_health_returns_ok_status(self) -> None:
        """Verify health() returns {"status": "ok"}."""
        result = health()
        self.assertEqual(result, {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
