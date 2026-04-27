from enum import IntEnum

"""ShipmentState enum."""
class ShipmentState(IntEnum):
    PENDING = 0
    IN_TRANSIT = 1
    DELIVERED = 2
    LOST = 3
