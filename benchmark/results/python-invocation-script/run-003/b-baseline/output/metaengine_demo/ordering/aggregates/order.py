"""Order aggregate for the ordering domain."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Order:
    """Aggregate root representing an order."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
