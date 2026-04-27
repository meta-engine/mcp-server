from typing import List, Optional
from shipping.aggregates.shipment import Shipment

"""ShipmentService service."""
class ShipmentService:
    def create(self, input: 'Shipment') -> 'Shipment':
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Optional['Shipment']:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> List['Shipment']:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

