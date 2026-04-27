from typing import Optional
from shipping.aggregates.shipment import Shipment

"""CarrierGateway service."""
class CarrierGateway:
    def create(self, input: Shipment) -> Shipment:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Optional[Shipment]:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> list[Shipment]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

