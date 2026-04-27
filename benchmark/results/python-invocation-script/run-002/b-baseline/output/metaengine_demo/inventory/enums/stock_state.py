"""StockState enum."""
from enum import IntEnum


class StockState(IntEnum):
    """State of a StockItem."""

    InStock = 0
    Reserved = 1
    Depleted = 2
