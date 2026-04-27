from shipping.aggregates.shipment import Shipment

"""ShipmentRepository service."""
class ShipmentRepository:
    def create(self, input: Shipment) -> Shipment:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Shipment | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> list[Shipment]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

