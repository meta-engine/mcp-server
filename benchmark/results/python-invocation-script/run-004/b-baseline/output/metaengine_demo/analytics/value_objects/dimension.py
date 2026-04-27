"""Dimension value object module."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Dimension:
    """Immutable Dimension value object."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
