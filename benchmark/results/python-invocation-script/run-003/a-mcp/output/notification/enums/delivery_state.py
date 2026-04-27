from enum import IntEnum

"""DeliveryState enum."""
class DeliveryState(IntEnum):
    QUEUED = 0
    SENT = 1
    DELIVERED = 2
    FAILED = 3
