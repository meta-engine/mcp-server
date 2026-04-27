"""TaxCalculator for the billing domain."""

from typing import Optional

from metaengine_demo.billing.aggregates.invoice import Invoice


class TaxCalculator:
    """Domain service that computes taxes for invoices."""

    def create(self, input: Optional[Invoice]) -> Invoice:
        """Compute taxes for a newly created invoice."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Invoice]:
        """Find tax information for an invoice by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Invoice]:
        """List invoices with tax computations up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Drop tax computations for an invoice by id."""
        raise NotImplementedError("not implemented")
