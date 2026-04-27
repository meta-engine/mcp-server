"""Carrier enum."""
from enum import IntEnum


class Carrier(IntEnum):
    """Shipping carrier identifier."""

    Ups = 0
    Fedex = 1
    Dhl = 2
    Usps = 3
