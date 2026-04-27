"""Invoice aggregate."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Invoice:
    """Invoice aggregate root for the billing domain."""

    id: str
    created_at: datetime
    updated_at: datetime
    name: str
    description: str
