"""TaxCalculator for the billing domain."""
from typing import Optional

from metaengine_demo.billing.aggregates.invoice import Invoice


class TaxCalculator:
    """TaxCalculator domain service."""

    def create(self, input: Optional[Invoice]) -> Invoice:
        """Calculate taxes on a new invoice."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Invoice]:
        """Retrieve tax calculations for an invoice id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Invoice]:
        """List invoices with tax calculations."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Remove tax calculations for an invoice."""
        raise NotImplementedError("not implemented")
