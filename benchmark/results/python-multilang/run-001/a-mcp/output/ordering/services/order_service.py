from ordering.aggregates.order import Order

"""OrderService service."""
class OrderService:
    def create(self, input: dict) -> Order:
        raise NotImplementedError('not implemented')
    def find_by_id(self, id: str) -> Order | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> list[Order]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

