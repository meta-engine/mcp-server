"""OrderStatus enum."""
from enum import IntEnum


class OrderStatus(IntEnum):
    """Lifecycle status of an Order."""

    Draft = 0
    Placed = 1
    Paid = 2
    Shipped = 3
    Delivered = 4
    Cancelled = 5
