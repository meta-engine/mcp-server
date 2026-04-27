"""ShipmentState enum."""
from enum import IntEnum


class ShipmentState(IntEnum):
    """State of a Shipment."""

    Pending = 0
    InTransit = 1
    Delivered = 2
    Lost = 3
