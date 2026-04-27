"""StockRepository for the inventory domain."""
from typing import Optional

from metaengine_demo.inventory.aggregates.stock_item import StockItem


class StockRepository:
    """StockRepository persistence service."""

    def create(self, input: Optional[StockItem]) -> StockItem:
        """Persist a new stock item."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[StockItem]:
        """Find a stock item by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[StockItem]:
        """List stock items up to a limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a stock item by id."""
        raise NotImplementedError("not implemented")
