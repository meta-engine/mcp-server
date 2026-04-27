"""Recipient value object for the notification domain."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Recipient:
    """Recipient value object."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
