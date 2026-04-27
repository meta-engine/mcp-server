"""OrderValidator for the ordering domain."""

from typing import Optional

from metaengine_demo.ordering.aggregates.order import Order


class OrderValidator:
    """OrderValidator domain service."""

    def create(self, input: Optional[Order]) -> Order:
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Order]:
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Order]:
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        raise NotImplementedError("not implemented")
