"""Service package checked by the repo compile step.

Todo and health behavior live in ``src``.
"""

from src.schema import execute, schema

__all__ = ["execute", "schema"]
