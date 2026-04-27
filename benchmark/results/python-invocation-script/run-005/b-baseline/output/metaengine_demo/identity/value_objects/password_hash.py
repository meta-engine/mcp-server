"""PasswordHash value object for the identity domain."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PasswordHash:
    """PasswordHash value object."""

    value: str
