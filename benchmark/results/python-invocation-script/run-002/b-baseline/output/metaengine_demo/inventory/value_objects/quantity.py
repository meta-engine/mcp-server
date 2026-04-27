"""Quantity value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Quantity:
    """Immutable Quantity value object."""

    amount: float
    unit: str
