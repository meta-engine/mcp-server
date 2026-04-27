"""Discount value object for the billing domain."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Discount:
    """Immutable Discount value object."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
