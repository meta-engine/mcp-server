"""ProductService for the catalog domain."""
from typing import Optional

from metaengine_demo.catalog.aggregates.product import Product


class ProductService:
    """ProductService."""

    def create(self, input: Optional[Product]) -> Product:
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[Product]:
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Product]:
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        raise NotImplementedError("not implemented")
