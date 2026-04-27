from typing import Optional
from inventory.aggregates.stock_item import StockItem

"""ReservationService service."""
class ReservationService:
    def create(self, input: StockItem) -> StockItem:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Optional[StockItem]:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> list[StockItem]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

