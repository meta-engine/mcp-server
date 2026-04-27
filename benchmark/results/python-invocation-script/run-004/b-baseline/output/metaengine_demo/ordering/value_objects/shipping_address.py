"""ShippingAddress value object module."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ShippingAddress:
    """Immutable ShippingAddress value object."""

    street: str
    city: str
    country: str
    postalCode: str
