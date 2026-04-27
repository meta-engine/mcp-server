from ordering.aggregates.order import Order

"""OrderService service."""
class OrderService:
    def create(self, input: Order) -> Order:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Order | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> list[Order]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

