"""Quantity value object for the inventory domain."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Quantity:
    """Immutable quantity expressed as an amount and unit."""

    amount: float
    unit: str
