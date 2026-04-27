from typing import Any, Dict, List, Optional
from billing.aggregates.invoice import Invoice

"""InvoiceRepository service."""
class InvoiceRepository:
    def create(self, input: Dict[str, Any]) -> Invoice:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Optional[Invoice]:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> List[Invoice]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

