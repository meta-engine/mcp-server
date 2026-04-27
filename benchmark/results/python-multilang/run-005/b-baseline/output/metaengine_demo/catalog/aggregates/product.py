"""Product aggregate for the catalog domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Product:
    """Product aggregate root."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
