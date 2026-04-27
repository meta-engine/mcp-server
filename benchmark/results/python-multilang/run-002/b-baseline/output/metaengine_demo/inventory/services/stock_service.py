"""StockService for the inventory domain."""

from typing import Optional

from metaengine_demo.inventory.aggregates.stock_item import StockItem


class StockService:
    """Application service exposing stock-item operations."""

    def create(self, input: Optional[StockItem]) -> StockItem:
        """Create a new stock item from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[StockItem]:
        """Look up a stock item by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[StockItem]:
        """List stock items up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a stock item by its identifier."""
        raise NotImplementedError("not implemented")
