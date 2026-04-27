"""TrackingNumber value object module."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TrackingNumber:
    """Immutable TrackingNumber value object."""

    value: str
