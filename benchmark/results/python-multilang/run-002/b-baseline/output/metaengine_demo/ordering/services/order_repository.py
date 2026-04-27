"""OrderRepository for the ordering domain."""

from typing import Optional

from metaengine_demo.ordering.aggregates.order import Order


class OrderRepository:
    """Persistence boundary for the Order aggregate."""

    def create(self, input: Optional[Order]) -> Order:
        """Persist a new order from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Order]:
        """Load an order by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Order]:
        """List persisted orders up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a persisted order by identifier."""
        raise NotImplementedError("not implemented")
