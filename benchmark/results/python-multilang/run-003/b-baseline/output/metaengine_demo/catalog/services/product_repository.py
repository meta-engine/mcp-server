"""ProductRepository for the catalog domain."""
from typing import Optional

from metaengine_demo.catalog.aggregates.product import Product


class ProductRepository:
    """ProductRepository persistence service."""

    def create(self, input: Optional[Product]) -> Product:
        """Persist a new product."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Product]:
        """Find a product by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Product]:
        """List products up to a limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a product by id."""
        raise NotImplementedError("not implemented")
