"""InvoiceStatus enum."""
from enum import IntEnum


class InvoiceStatus(IntEnum):
    """Status of an Invoice."""

    Pending = 0
    Paid = 1
    Overdue = 2
    Void = 3
