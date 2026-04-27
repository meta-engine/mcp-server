"""Sku value object module."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Sku:
    """Immutable Sku value object."""

    value: str
