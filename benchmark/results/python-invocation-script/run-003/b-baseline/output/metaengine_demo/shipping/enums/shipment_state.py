"""ShipmentState enum for the shipping domain."""
from enum import IntEnum


class ShipmentState(IntEnum):
    """Lifecycle state of a shipment."""

    Pending = 0
    InTransit = 1
    Delivered = 2
    Lost = 3
