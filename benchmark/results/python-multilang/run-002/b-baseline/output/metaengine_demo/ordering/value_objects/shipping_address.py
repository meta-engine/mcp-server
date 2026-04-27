"""ShippingAddress value object for the ordering domain."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ShippingAddress:
    """Immutable value object describing a shipping destination."""

    street: str
    city: str
    country: str
    postalCode: str
