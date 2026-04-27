from enum import IntEnum

"""StockState enum."""
class StockState(IntEnum):
    IN_STOCK = 0
    RESERVED = 1
    DEPLETED = 2
