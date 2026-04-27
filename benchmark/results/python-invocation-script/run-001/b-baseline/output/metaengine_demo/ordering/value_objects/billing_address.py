"""BillingAddress value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class BillingAddress:
    """BillingAddress immutable value object."""

    street: str
    city: str
    country: str
    postal_code: str
