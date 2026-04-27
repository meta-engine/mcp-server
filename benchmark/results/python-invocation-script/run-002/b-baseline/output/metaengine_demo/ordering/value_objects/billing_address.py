"""BillingAddress value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class BillingAddress:
    """Immutable BillingAddress value object."""

    street: str
    city: str
    country: str
    postal_code: str
