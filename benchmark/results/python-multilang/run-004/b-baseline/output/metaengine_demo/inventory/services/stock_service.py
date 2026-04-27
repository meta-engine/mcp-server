"""StockService for the inventory domain."""
from typing import Optional

from metaengine_demo.inventory.aggregates.stock_item import StockItem


class StockService:
    """Service exposing stock operations."""

    def create(self, input: Optional[StockItem]) -> StockItem:
        """Create a new StockItem."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[StockItem]:
        """Find a StockItem by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[StockItem]:
        """List StockItems up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a StockItem by id."""
        raise NotImplementedError("not implemented")
