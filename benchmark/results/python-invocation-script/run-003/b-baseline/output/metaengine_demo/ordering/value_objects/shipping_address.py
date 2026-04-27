"""ShippingAddress value object for the ordering domain."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ShippingAddress:
    """Immutable value object representing a shipping address."""

    street: str
    city: str
    country: str
    postalCode: str
