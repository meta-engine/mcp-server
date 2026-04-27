"""InvoiceRepository service module."""
from typing import Optional

from metaengine_demo.billing.aggregates.invoice import Invoice


class InvoiceRepository:
    """InvoiceRepository service."""

    def create(self, input: Optional[Invoice]) -> Invoice:
        """Create an Invoice."""
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[Invoice]:
        """Find an Invoice by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: int) -> list[Invoice]:
        """List Invoices."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete an Invoice by id."""
        raise NotImplementedError("not implemented")
