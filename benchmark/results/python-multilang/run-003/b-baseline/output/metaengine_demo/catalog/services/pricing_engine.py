"""PricingEngine for the catalog domain."""
from typing import Optional

from metaengine_demo.catalog.aggregates.product import Product


class PricingEngine:
    """PricingEngine domain service."""

    def create(self, input: Optional[Product]) -> Product:
        """Compute pricing for a new product."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Product]:
        """Lookup pricing for a product by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Product]:
        """List priced products up to a limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Remove pricing for a product."""
        raise NotImplementedError("not implemented")
