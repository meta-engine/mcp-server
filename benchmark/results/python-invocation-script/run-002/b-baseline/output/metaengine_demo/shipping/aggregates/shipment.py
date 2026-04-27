"""Shipment aggregate."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Shipment:
    """Shipment aggregate root for the shipping domain."""

    id: str
    created_at: datetime
    updated_at: datetime
    name: str
    description: str
