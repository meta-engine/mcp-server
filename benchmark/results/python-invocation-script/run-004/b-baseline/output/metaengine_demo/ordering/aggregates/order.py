"""Order aggregate module."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Order:
    """Order aggregate root."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
