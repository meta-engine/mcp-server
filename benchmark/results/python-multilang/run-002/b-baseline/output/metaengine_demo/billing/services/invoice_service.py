"""InvoiceService for the billing domain."""

from typing import Optional

from metaengine_demo.billing.aggregates.invoice import Invoice


class InvoiceService:
    """Application service exposing invoice operations."""

    def create(self, input: Optional[Invoice]) -> Invoice:
        """Create a new invoice from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Invoice]:
        """Look up an invoice by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Invoice]:
        """List invoices up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete an invoice by its identifier."""
        raise NotImplementedError("not implemented")
