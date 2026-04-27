"""ShipmentRepository for the shipping domain."""
from typing import Optional

from metaengine_demo.shipping.aggregates.shipment import Shipment


class ShipmentRepository:
    """ShipmentRepository domain service."""

    def create(self, input: Optional[Shipment]) -> Shipment:
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Shipment]:
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Shipment]:
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        raise NotImplementedError("not implemented")
