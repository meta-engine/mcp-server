"""OrderService for the ordering domain."""
from typing import Optional

from metaengine_demo.ordering.aggregates.order import Order


class OrderService:
    """OrderService application service."""

    def create(self, input: Optional[Order]) -> Order:
        """Create a new order."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Order]:
        """Find an order by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Order]:
        """List orders up to a limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete an order by id."""
        raise NotImplementedError("not implemented")
