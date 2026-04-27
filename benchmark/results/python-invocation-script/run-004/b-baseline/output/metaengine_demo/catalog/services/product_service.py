"""ProductService service module."""
from typing import Optional

from metaengine_demo.catalog.aggregates.product import Product


class ProductService:
    """ProductService service."""

    def create(self, input: Optional[Product]) -> Product:
        """Create a Product."""
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[Product]:
        """Find a Product by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: int) -> list[Product]:
        """List Products."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a Product by id."""
        raise NotImplementedError("not implemented")
