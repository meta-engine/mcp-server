"""ProductState enum for the catalog domain."""

from enum import IntEnum


class ProductState(IntEnum):
    """Lifecycle state of a product in the catalog."""

    Draft = 0
    Active = 1
    Archived = 2
