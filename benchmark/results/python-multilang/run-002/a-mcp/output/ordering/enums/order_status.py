from enum import IntEnum

"""OrderStatus enum."""
class OrderStatus(IntEnum):
    DRAFT = 0
    PLACED = 1
    PAID = 2
    SHIPPED = 3
    DELIVERED = 4
    CANCELLED = 5
