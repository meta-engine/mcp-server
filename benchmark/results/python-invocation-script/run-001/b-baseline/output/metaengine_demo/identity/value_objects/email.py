"""Email value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Email immutable value object."""

    value: str
