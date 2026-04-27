"""DeliveryWindow value object."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DeliveryWindow:
    """DeliveryWindow immutable value object."""

    id: str
    created_at: datetime
    updated_at: datetime
    name: str
    description: str
