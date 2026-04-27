"""Invoice aggregate for the billing domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Invoice:
    """Aggregate root representing a customer invoice."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
