"""OrderRepository for the ordering domain."""
from typing import Optional

from metaengine_demo.ordering.aggregates.order import Order


class OrderRepository:
    """Repository for persisting and querying Orders."""

    def create(self, input: Optional[Order]) -> Order:
        """Persist a new Order."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Order]:
        """Find an Order by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Order]:
        """List Orders up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete an Order by id."""
        raise NotImplementedError("not implemented")
