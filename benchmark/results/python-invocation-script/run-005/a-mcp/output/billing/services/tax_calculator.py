from billing.aggregates.invoice import Invoice

"""TaxCalculator service."""
class TaxCalculator:
    def create(self, input: Invoice) -> Invoice:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Invoice | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> list[Invoice]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

