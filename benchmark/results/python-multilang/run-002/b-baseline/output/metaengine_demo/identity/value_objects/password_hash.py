"""PasswordHash value object for the identity domain."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PasswordHash:
    """Immutable hashed password value."""

    value: str
