"""Event aggregate."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    """Event aggregate root for the analytics domain."""

    id: str
    created_at: datetime
    updated_at: datetime
    name: str
    description: str
