"""ReservationService for the inventory domain."""

from typing import Optional

from metaengine_demo.inventory.aggregates.stock_item import StockItem


class ReservationService:
    """Service that manages stock reservations against stock items."""

    def create(self, input: Optional[StockItem]) -> StockItem:
        """Create a reservation for a stock item from partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[StockItem]:
        """Look up a reserved stock item by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[StockItem]:
        """List reserved stock items up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Release a reservation on a stock item by id."""
        raise NotImplementedError("not implemented")
