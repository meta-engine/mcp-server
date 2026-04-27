"""TrackingNumber value object for the shipping domain."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TrackingNumber:
    """TrackingNumber value object."""

    value: str
