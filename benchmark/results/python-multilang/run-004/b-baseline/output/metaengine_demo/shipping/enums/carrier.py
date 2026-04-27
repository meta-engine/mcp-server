"""Carrier enum for the shipping domain."""
from enum import IntEnum


class Carrier(IntEnum):
    """Shipping carrier."""

    Ups = 0
    Fedex = 1
    Dhl = 2
    Usps = 3
