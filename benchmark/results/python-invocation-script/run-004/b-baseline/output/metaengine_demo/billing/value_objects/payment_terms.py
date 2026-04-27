"""PaymentTerms value object module."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PaymentTerms:
    """Immutable PaymentTerms value object."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
