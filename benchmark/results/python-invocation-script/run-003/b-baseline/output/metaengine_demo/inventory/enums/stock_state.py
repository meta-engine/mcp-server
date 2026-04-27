"""StockState enum for the inventory domain."""
from enum import IntEnum


class StockState(IntEnum):
    """Lifecycle state of a stock item."""

    InStock = 0
    Reserved = 1
    Depleted = 2
