"""PricingEngine for the catalog domain."""
from typing import Optional

from metaengine_demo.catalog.aggregates.product import Product


class PricingEngine:
    """Engine that computes and applies product pricing."""

    def create(self, input: Optional[Product]) -> Product:
        """Create pricing for a Product."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Product]:
        """Find a priced Product by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Product]:
        """List priced Products up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete pricing for a Product by id."""
        raise NotImplementedError("not implemented")
