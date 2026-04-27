"""PasswordHash value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PasswordHash:
    """PasswordHash immutable value object."""

    value: str
