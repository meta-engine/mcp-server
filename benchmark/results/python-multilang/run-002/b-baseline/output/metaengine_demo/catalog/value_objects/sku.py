"""Sku value object for the catalog domain."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Sku:
    """Immutable stock-keeping unit identifier."""

    value: str
