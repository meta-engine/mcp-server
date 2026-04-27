"""OrderValidator for the ordering domain."""
from typing import Optional

from metaengine_demo.ordering.aggregates.order import Order


class OrderValidator:
    """OrderValidator domain service."""

    def create(self, input: Optional[Order]) -> Order:
        """Validate a candidate order on creation."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Order]:
        """Validate retrieval by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Order]:
        """Validate a listing request."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Validate deletion request."""
        raise NotImplementedError("not implemented")
