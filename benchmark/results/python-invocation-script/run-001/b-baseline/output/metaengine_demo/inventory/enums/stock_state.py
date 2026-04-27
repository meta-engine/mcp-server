"""StockState enum."""
from enum import IntEnum


class StockState(IntEnum):
    """StockState enumeration."""

    InStock = 0
    Reserved = 1
    Depleted = 2
