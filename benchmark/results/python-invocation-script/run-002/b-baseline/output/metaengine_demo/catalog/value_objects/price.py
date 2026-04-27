"""Price value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    """Immutable Price value object."""

    amount: float
    currency: str
