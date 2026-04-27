"""ShipmentState enum for the shipping domain."""
from enum import IntEnum


class ShipmentState(IntEnum):
    """State of a shipment through its lifecycle."""

    Pending = 0
    InTransit = 1
    Delivered = 2
    Lost = 3
