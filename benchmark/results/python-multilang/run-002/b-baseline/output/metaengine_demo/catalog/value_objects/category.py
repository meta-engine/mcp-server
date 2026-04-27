"""Category value object for the catalog domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Category:
    """Immutable taxonomy category for grouping products."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
