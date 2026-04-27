"""TaxCalculator for the billing domain."""
from typing import Optional

from metaengine_demo.billing.aggregates.invoice import Invoice


class TaxCalculator:
    """TaxCalculator."""

    def create(self, input: Optional[Invoice]) -> Invoice:
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[Invoice]:
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Invoice]:
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        raise NotImplementedError("not implemented")
