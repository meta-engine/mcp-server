"""ShipmentState enum for the shipping domain."""

from enum import IntEnum


class ShipmentState(IntEnum):
    """ShipmentState enumeration."""

    Pending = 0
    InTransit = 1
    Delivered = 2
    Lost = 3
