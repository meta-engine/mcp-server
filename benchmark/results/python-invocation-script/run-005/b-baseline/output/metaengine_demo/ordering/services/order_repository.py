"""OrderRepository for the ordering domain."""
from typing import Optional

from metaengine_demo.ordering.aggregates.order import Order


class OrderRepository:
    """OrderRepository."""

    def create(self, input: Optional[Order]) -> Order:
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[Order]:
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Order]:
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        raise NotImplementedError("not implemented")
