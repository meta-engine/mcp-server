"""Notification aggregate."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Notification:
    """Notification aggregate root for the notification domain."""

    id: str
    created_at: datetime
    updated_at: datetime
    name: str
    description: str
