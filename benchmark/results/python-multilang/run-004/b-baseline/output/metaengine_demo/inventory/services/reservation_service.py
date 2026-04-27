"""ReservationService for the inventory domain."""
from typing import Optional

from metaengine_demo.inventory.aggregates.stock_item import StockItem


class ReservationService:
    """Service managing stock reservations."""

    def create(self, input: Optional[StockItem]) -> StockItem:
        """Create a reservation for a StockItem."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[StockItem]:
        """Find a reserved StockItem by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[StockItem]:
        """List reserved StockItems up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Cancel a reservation for a StockItem by id."""
        raise NotImplementedError("not implemented")
