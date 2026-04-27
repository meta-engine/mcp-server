"""PaymentTerms value object."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PaymentTerms:
    """Immutable PaymentTerms value object."""

    id: str
    created_at: datetime
    updated_at: datetime
    name: str
    description: str
