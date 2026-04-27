"""InvoiceStatus enum for the billing domain."""

from enum import IntEnum


class InvoiceStatus(IntEnum):
    """Lifecycle status of an invoice."""

    Pending = 0
    Paid = 1
    Overdue = 2
    Void = 3
