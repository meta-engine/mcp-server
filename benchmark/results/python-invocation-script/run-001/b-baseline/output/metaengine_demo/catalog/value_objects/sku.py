"""Sku value object."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Sku:
    """Sku immutable value object."""

    value: str
