from shipping.aggregates.shipment import Shipment

"""ShipmentRepository service."""
class ShipmentRepository:
    def create(self, input: dict) -> Shipment:
        raise NotImplementedError('not implemented')
    def find_by_id(self, id: str) -> Shipment | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> list[Shipment]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

