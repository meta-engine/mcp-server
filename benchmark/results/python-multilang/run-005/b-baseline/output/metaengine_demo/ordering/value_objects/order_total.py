"""OrderTotal value object for the ordering domain."""

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderTotal:
    """OrderTotal value object."""

    amount: float
    currency: str
