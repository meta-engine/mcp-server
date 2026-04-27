"""StockRepository for the inventory domain."""
from typing import Optional

from metaengine_demo.inventory.aggregates.stock_item import StockItem


class StockRepository:
    """StockRepository."""

    def create(self, input: Optional[StockItem]) -> StockItem:
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[StockItem]:
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[StockItem]:
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        raise NotImplementedError("not implemented")
