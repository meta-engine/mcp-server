"""ShipmentRoute value object for the shipping domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ShipmentRoute:
    """ShipmentRoute value object."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
