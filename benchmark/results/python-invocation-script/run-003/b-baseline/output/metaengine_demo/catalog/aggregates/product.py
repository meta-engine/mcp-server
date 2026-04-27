"""Product aggregate for the catalog domain."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Product:
    """Aggregate root representing a catalog product."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
