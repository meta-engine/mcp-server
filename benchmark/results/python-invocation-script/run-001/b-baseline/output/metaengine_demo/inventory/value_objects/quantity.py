"""Quantity value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Quantity:
    """Quantity immutable value object."""

    amount: float
    unit: str
