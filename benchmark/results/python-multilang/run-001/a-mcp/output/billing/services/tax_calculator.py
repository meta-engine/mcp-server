from billing.aggregates.invoice import Invoice

"""TaxCalculator service."""
class TaxCalculator:
    def create(self, input: dict) -> Invoice:
        raise NotImplementedError('not implemented')
    def find_by_id(self, id: str) -> Invoice | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> list[Invoice]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

