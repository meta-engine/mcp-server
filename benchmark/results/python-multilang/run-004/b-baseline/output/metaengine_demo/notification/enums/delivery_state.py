"""DeliveryState enum for the notification domain."""
from enum import IntEnum


class DeliveryState(IntEnum):
    """State of a delivery attempt."""

    Queued = 0
    Sent = 1
    Delivered = 2
    Failed = 3
