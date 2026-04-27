from enum import IntEnum

"""InvoiceStatus enum."""
class InvoiceStatus(IntEnum):
    PENDING = 0
    PAID = 1
    OVERDUE = 2
    VOID = 3
