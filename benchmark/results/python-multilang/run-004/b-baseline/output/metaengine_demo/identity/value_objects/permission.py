"""Permission value object for the identity domain."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Permission:
    """Immutable Permission value object."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
