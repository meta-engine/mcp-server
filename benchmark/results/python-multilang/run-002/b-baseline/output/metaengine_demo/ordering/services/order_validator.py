"""OrderValidator for the ordering domain."""

from typing import Optional

from metaengine_demo.ordering.aggregates.order import Order


class OrderValidator:
    """Domain service that validates orders."""

    def create(self, input: Optional[Order]) -> Order:
        """Validate creation input for an order."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Order]:
        """Validate access for an order by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Order]:
        """Validate a list query for orders."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Validate deletion of an order by id."""
        raise NotImplementedError("not implemented")
