"""Email value object for the identity domain."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Immutable email address value."""

    value: str
