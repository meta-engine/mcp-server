"""StockRepository service module."""
from typing import Optional

from metaengine_demo.inventory.aggregates.stock_item import StockItem


class StockRepository:
    """StockRepository service."""

    def create(self, input: Optional[StockItem]) -> StockItem:
        """Create a StockItem."""
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[StockItem]:
        """Find a StockItem by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: int) -> list[StockItem]:
        """List StockItems."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a StockItem by id."""
        raise NotImplementedError("not implemented")
