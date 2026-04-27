from typing import Any, Dict, List, Optional
from inventory.aggregates.stock_item import StockItem

"""StockService service."""
class StockService:
    def create(self, input: Dict[str, Any]) -> StockItem:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Optional[StockItem]:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> List[StockItem]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

