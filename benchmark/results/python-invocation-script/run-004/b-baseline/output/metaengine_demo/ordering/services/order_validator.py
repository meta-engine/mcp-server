"""OrderValidator service module."""
from typing import Optional

from metaengine_demo.ordering.aggregates.order import Order


class OrderValidator:
    """OrderValidator service."""

    def create(self, input: Optional[Order]) -> Order:
        """Create an Order."""
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[Order]:
        """Find an Order by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: int) -> list[Order]:
        """List Orders."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete an Order by id."""
        raise NotImplementedError("not implemented")
