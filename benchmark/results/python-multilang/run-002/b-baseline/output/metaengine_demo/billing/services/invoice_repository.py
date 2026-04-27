"""InvoiceRepository for the billing domain."""

from typing import Optional

from metaengine_demo.billing.aggregates.invoice import Invoice


class InvoiceRepository:
    """Persistence boundary for the Invoice aggregate."""

    def create(self, input: Optional[Invoice]) -> Invoice:
        """Persist a new invoice from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Invoice]:
        """Load an invoice by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Invoice]:
        """List persisted invoices up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a persisted invoice by identifier."""
        raise NotImplementedError("not implemented")
