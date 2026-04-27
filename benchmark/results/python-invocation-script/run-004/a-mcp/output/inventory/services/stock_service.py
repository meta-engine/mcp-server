from inventory.aggregates.stock_item import StockItem

"""StockService service."""
class StockService:
    def create(self, input: dict) -> StockItem:
        raise NotImplementedError('not implemented')
    def find_by_id(self, id: str) -> StockItem | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> list[StockItem]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

