"""Notification aggregate for the notification domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Notification:
    """Aggregate root representing a notification dispatched to a recipient."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
