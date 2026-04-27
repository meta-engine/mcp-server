"""ProductService for the catalog domain."""

from typing import Optional

from metaengine_demo.catalog.aggregates.product import Product


class ProductService:
    """Application service exposing product operations."""

    def create(self, input: Optional[Product]) -> Product:
        """Create a new product from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Product]:
        """Look up a product by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Product]:
        """List products up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a product by its identifier."""
        raise NotImplementedError("not implemented")
