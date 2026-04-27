"""Quantity value object for the inventory domain."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Quantity:
    """Immutable Quantity value object."""

    amount: float
    unit: str
