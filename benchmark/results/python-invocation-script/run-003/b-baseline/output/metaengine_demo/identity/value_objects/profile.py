"""Profile value object for the identity domain."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Profile:
    """Immutable user profile metadata."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
