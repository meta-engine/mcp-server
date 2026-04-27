"""ReservationService for the inventory domain."""
from typing import Optional

from metaengine_demo.inventory.aggregates.stock_item import StockItem


class ReservationService:
    """ReservationService domain service."""

    def create(self, input: Optional[StockItem]) -> StockItem:
        """Reserve stock from a stock item."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[StockItem]:
        """Lookup a stock reservation by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[StockItem]:
        """List reserved stock items."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Release a stock reservation."""
        raise NotImplementedError("not implemented")
