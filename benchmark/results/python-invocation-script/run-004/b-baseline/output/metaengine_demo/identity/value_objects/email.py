"""Email value object module."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Immutable Email value object."""

    value: str
