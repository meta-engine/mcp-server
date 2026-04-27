"""Shipment aggregate for the shipping domain."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Shipment:
    """Aggregate root representing a shipment."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
