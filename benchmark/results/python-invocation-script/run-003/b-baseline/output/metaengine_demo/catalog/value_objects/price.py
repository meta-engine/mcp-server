"""Price value object for the catalog domain."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    """Immutable monetary price."""

    amount: float
    currency: str
