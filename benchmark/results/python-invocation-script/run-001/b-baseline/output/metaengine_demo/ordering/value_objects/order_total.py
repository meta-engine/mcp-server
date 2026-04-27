"""OrderTotal value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderTotal:
    """OrderTotal immutable value object."""

    amount: float
    currency: str
