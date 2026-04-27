"""Price value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    """Price immutable value object."""

    amount: float
    currency: str
