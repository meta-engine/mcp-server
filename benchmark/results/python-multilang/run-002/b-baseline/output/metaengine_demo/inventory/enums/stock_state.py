"""StockState enum for the inventory domain."""

from enum import IntEnum


class StockState(IntEnum):
    """State of a stock item in inventory."""

    InStock = 0
    Reserved = 1
    Depleted = 2
