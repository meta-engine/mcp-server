"""CarrierGateway for the shipping domain."""
from typing import Optional

from metaengine_demo.shipping.aggregates.shipment import Shipment


class CarrierGateway:
    """CarrierGateway external integration service."""

    def create(self, input: Optional[Shipment]) -> Shipment:
        """Submit a new shipment to a carrier."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Shipment]:
        """Lookup a shipment via the carrier gateway."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Shipment]:
        """List carrier-tracked shipments."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Cancel a shipment with the carrier."""
        raise NotImplementedError("not implemented")
