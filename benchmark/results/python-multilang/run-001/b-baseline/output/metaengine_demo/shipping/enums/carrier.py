"""Carrier enum for the shipping domain."""
from enum import IntEnum


class Carrier(IntEnum):
    """Carrier enum."""

    Ups = 0
    Fedex = 1
    Dhl = 2
    Usps = 3
