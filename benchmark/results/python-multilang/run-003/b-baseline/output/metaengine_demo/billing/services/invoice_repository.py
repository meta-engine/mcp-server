"""InvoiceRepository for the billing domain."""
from typing import Optional

from metaengine_demo.billing.aggregates.invoice import Invoice


class InvoiceRepository:
    """InvoiceRepository persistence service."""

    def create(self, input: Optional[Invoice]) -> Invoice:
        """Persist a new invoice."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Invoice]:
        """Find an invoice by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Invoice]:
        """List invoices up to a limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete an invoice by id."""
        raise NotImplementedError("not implemented")
