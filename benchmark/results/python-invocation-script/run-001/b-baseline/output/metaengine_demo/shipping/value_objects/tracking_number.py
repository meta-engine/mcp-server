"""TrackingNumber value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TrackingNumber:
    """TrackingNumber immutable value object."""

    value: str
