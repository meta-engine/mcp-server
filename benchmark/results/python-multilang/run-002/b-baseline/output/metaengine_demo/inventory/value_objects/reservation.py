"""Reservation value object for the inventory domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Reservation:
    """Immutable reservation of stock against an order."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
