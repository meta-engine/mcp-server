"""InvoiceService service."""
from typing import Optional

from metaengine_demo.billing.aggregates.invoice import Invoice


class InvoiceService:
    """InvoiceService service."""

    def create(self, input: Optional[Invoice]) -> Invoice:
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[Invoice]:
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Invoice]:
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        raise NotImplementedError("not implemented")
