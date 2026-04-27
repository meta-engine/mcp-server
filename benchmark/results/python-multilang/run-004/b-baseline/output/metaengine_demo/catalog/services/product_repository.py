"""ProductRepository for the catalog domain."""
from typing import Optional

from metaengine_demo.catalog.aggregates.product import Product


class ProductRepository:
    """Repository for persisting and querying Products."""

    def create(self, input: Optional[Product]) -> Product:
        """Persist a new Product."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Product]:
        """Find a Product by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Product]:
        """List Products up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a Product by id."""
        raise NotImplementedError("not implemented")
