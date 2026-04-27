"""StockRepository for the inventory domain."""

from typing import Optional

from metaengine_demo.inventory.aggregates.stock_item import StockItem


class StockRepository:
    """Persistence boundary for the StockItem aggregate."""

    def create(self, input: Optional[StockItem]) -> StockItem:
        """Persist a new stock item from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[StockItem]:
        """Load a stock item by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[StockItem]:
        """List persisted stock items up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a persisted stock item by identifier."""
        raise NotImplementedError("not implemented")
