"""StockItem aggregate for the inventory domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class StockItem:
    """Aggregate root representing an inventory stock item."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
