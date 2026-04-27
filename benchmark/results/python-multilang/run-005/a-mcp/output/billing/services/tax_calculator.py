from typing import List, Optional
from billing.aggregates.invoice import Invoice

"""TaxCalculator service."""
class TaxCalculator:
    def create(self, input: 'Invoice') -> 'Invoice':
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Optional['Invoice']:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> List['Invoice']:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

