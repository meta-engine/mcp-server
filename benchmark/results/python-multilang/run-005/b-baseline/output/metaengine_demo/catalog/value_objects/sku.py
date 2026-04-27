"""Sku value object for the catalog domain."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Sku:
    """Sku value object."""

    value: str
