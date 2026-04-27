"""CarrierGateway service."""
from typing import Optional

from metaengine_demo.shipping.aggregates.shipment import Shipment


class CarrierGateway:
    """CarrierGateway service for the shipping domain."""

    def create(self, input: Optional[Shipment]) -> Shipment:
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[Shipment]:
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Shipment]:
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        raise NotImplementedError("not implemented")
