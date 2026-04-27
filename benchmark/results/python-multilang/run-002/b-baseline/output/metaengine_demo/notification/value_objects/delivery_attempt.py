"""DeliveryAttempt value object for the notification domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DeliveryAttempt:
    """Immutable record of a single notification delivery attempt."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
