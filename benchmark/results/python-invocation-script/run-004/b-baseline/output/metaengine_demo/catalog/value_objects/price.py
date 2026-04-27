"""Price value object module."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    """Immutable Price value object."""

    amount: float
    currency: str
