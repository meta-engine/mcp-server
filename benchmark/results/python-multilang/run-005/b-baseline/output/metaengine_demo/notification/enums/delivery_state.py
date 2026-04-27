"""DeliveryState enum for the notification domain."""

from enum import IntEnum


class DeliveryState(IntEnum):
    """DeliveryState enumeration."""

    Queued = 0
    Sent = 1
    Delivered = 2
    Failed = 3
