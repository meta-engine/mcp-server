"""OrderService for the ordering domain."""

from typing import Optional

from metaengine_demo.ordering.aggregates.order import Order


class OrderService:
    """Application service exposing order operations."""

    def create(self, input: Optional[Order]) -> Order:
        """Create a new order from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Order]:
        """Look up an order by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Order]:
        """List orders up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete an order by its identifier."""
        raise NotImplementedError("not implemented")
