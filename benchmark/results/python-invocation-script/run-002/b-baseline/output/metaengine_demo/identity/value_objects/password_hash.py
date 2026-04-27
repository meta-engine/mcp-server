"""PasswordHash value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PasswordHash:
    """Immutable PasswordHash value object."""

    value: str
