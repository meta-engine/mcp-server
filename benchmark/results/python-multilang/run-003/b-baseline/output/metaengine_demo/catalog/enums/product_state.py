"""ProductState enum for the catalog domain."""
from enum import IntEnum


class ProductState(IntEnum):
    """ProductState enumeration."""

    Draft = 0
    Active = 1
    Archived = 2
