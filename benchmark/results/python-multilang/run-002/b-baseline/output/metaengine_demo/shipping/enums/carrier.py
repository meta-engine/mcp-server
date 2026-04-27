"""Carrier enum for the shipping domain."""

from enum import IntEnum


class Carrier(IntEnum):
    """Supported shipping carriers."""

    Ups = 0
    Fedex = 1
    Dhl = 2
    Usps = 3
