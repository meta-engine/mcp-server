"""OrderLine value object for the ordering domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OrderLine:
    """Immutable value object for a single line within an order."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
