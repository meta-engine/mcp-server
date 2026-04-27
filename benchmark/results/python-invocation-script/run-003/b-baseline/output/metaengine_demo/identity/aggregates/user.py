"""User aggregate for the identity domain."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """Aggregate root representing a user."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
