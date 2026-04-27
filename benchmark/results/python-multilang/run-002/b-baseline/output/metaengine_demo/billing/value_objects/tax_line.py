"""TaxLine value object for the billing domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TaxLine:
    """Immutable line item describing applied tax."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
