"""EventPayload value object for the analytics domain."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EventPayload:
    """Immutable EventPayload value object."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
