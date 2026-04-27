from typing import Any, Dict, List, Optional
from catalog.aggregates.product import Product

"""ProductService service."""
class ProductService:
    def create(self, input: Dict[str, Any]) -> Product:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Optional[Product]:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> List[Product]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

