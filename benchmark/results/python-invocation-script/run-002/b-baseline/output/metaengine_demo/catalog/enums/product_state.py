"""ProductState enum."""
from enum import IntEnum


class ProductState(IntEnum):
    """Lifecycle state of a Product."""

    Draft = 0
    Active = 1
    Archived = 2
