"""InvoiceService for the billing domain."""
from typing import Optional

from metaengine_demo.billing.aggregates.invoice import Invoice


class InvoiceService:
    """Service exposing invoice operations."""

    def create(self, input: Optional[Invoice]) -> Invoice:
        """Create a new Invoice."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Invoice]:
        """Find an Invoice by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Invoice]:
        """List Invoices up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete an Invoice by id."""
        raise NotImplementedError("not implemented")
