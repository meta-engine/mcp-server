from typing import Optional
from billing.aggregates.invoice import Invoice

"""InvoiceRepository service."""
class InvoiceRepository:
    def create(self, input: Invoice) -> Invoice:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Optional[Invoice]:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> list[Invoice]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

