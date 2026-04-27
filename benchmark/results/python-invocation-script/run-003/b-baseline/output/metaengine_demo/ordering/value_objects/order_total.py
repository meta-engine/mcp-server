"""OrderTotal value object for the ordering domain."""
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderTotal:
    """Immutable value object representing an order monetary total."""

    amount: float
    currency: str
