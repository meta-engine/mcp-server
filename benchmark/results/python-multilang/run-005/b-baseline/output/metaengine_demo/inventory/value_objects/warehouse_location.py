"""WarehouseLocation value object for the inventory domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class WarehouseLocation:
    """WarehouseLocation value object."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
