"""BillingAddress value object for the ordering domain."""
from dataclasses import dataclass


@dataclass(frozen=True)
class BillingAddress:
    """Immutable value object representing a billing address."""

    street: str
    city: str
    country: str
    postalCode: str
