"""ProductDescription value object for the catalog domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ProductDescription:
    """Immutable descriptive metadata for a product."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
