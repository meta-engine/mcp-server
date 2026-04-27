"""Email value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Immutable Email value object."""

    value: str
