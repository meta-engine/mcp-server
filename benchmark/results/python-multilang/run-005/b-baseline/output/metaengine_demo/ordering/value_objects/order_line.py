"""OrderLine value object for the ordering domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OrderLine:
    """OrderLine value object."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
