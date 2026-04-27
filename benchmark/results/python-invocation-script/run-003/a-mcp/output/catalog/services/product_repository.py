from catalog.aggregates.product import Product

"""ProductRepository service."""
class ProductRepository:
    def create(self, input: Product) -> Product:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Product | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> list[Product]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

