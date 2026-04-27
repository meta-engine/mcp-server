from typing import Any, Dict, List, Optional
from ordering.aggregates.order import Order

"""OrderValidator service."""
class OrderValidator:
    def create(self, input: Dict[str, Any]) -> Order:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Optional[Order]:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> List[Order]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

