"""Price value object for the catalog domain."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    """Price value object."""

    amount: float
    currency: str
