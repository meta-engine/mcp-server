"""ShippingAddress value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ShippingAddress:
    """Immutable ShippingAddress value object."""

    street: str
    city: str
    country: str
    postal_code: str
