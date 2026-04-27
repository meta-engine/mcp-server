"""InvoiceStatus enum module."""
from enum import IntEnum


class InvoiceStatus(IntEnum):
    """InvoiceStatus enumeration."""

    Pending = 0
    Paid = 1
    Overdue = 2
    Void = 3
