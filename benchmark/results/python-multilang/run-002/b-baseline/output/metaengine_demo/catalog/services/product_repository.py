"""ProductRepository for the catalog domain."""

from typing import Optional

from metaengine_demo.catalog.aggregates.product import Product


class ProductRepository:
    """Persistence boundary for the Product aggregate."""

    def create(self, input: Optional[Product]) -> Product:
        """Persist a new product from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Product]:
        """Load a product by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Product]:
        """List persisted products up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a persisted product by identifier."""
        raise NotImplementedError("not implemented")
