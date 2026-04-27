from catalog.aggregates.product import Product

"""PricingEngine service."""
class PricingEngine:
    def create(self, input: dict) -> Product:
        raise NotImplementedError('not implemented')
    def find_by_id(self, id: str) -> Product | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> list[Product]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

