"""StockState enum for the inventory domain."""
from enum import IntEnum


class StockState(IntEnum):
    """StockState enum."""

    InStock = 0
    Reserved = 1
    Depleted = 2
