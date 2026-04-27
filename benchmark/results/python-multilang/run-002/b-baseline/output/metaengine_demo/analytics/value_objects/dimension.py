"""Dimension value object for the analytics domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Dimension:
    """Immutable analytics dimension definition."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
