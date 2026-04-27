from typing import List, Optional
from ordering.aggregates.order import Order

"""OrderValidator service."""
class OrderValidator:
    def create(self, input: Order) -> Order:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Optional[Order]:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> List[Order]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

