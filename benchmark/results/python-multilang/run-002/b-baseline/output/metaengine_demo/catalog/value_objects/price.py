"""Price value object for the catalog domain."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    """Immutable monetary price expressed in a single currency."""

    amount: float
    currency: str
