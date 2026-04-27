"""Event aggregate for the analytics domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    """Aggregate root representing an analytics event."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
