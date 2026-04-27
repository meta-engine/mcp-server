"""Discount value object for the billing domain."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Discount:
    """Immutable value object representing an invoice discount."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
