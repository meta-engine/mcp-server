"""BillingAddress value object for the ordering domain."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BillingAddress:
    """Immutable value object describing a billing destination."""

    street: str
    city: str
    country: str
    postalCode: str
