"""InvoiceLine value object for the billing domain."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class InvoiceLine:
    """Immutable value object representing a single invoice line."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
