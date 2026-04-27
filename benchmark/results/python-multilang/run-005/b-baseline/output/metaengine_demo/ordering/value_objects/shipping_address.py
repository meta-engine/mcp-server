"""ShippingAddress value object for the ordering domain."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ShippingAddress:
    """ShippingAddress value object."""

    street: str
    city: str
    country: str
    postalCode: str
