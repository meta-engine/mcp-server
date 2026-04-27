"""PaymentTerms value object for the billing domain."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PaymentTerms:
    """Immutable value object capturing the payment terms of an invoice."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
