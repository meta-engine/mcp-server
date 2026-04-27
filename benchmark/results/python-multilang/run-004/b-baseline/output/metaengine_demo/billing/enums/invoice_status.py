"""InvoiceStatus enum for the billing domain."""
from enum import IntEnum


class InvoiceStatus(IntEnum):
    """Status of an invoice through its lifecycle."""

    Pending = 0
    Paid = 1
    Overdue = 2
    Void = 3
