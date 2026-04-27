"""PricingEngine for the catalog domain."""

from typing import Optional

from metaengine_demo.catalog.aggregates.product import Product


class PricingEngine:
    """Domain service that computes and applies product pricing."""

    def create(self, input: Optional[Product]) -> Product:
        """Apply pricing to a newly created product."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Product]:
        """Find pricing for a product by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Product]:
        """List priced products up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Drop pricing for a product by id."""
        raise NotImplementedError("not implemented")
