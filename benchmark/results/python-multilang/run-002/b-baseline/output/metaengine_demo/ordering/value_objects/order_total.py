"""OrderTotal value object for the ordering domain."""

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderTotal:
    """Immutable value object representing the monetary total of an order."""

    amount: float
    currency: str
