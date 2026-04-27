"""TaxCalculator for the billing domain."""
from typing import Optional

from metaengine_demo.billing.aggregates.invoice import Invoice


class TaxCalculator:
    """Calculator for invoice taxes."""

    def create(self, input: Optional[Invoice]) -> Invoice:
        """Create tax data for a new Invoice."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Invoice]:
        """Find tax-bearing Invoice by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Invoice]:
        """List tax-bearing Invoices up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete tax data for an Invoice by id."""
        raise NotImplementedError("not implemented")
