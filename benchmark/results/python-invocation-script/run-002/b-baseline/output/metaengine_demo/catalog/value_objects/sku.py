"""Sku value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Sku:
    """Immutable Sku value object."""

    value: str
