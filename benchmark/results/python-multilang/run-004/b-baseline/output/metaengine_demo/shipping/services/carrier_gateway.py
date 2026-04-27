"""CarrierGateway for the shipping domain."""
from typing import Optional

from metaengine_demo.shipping.aggregates.shipment import Shipment


class CarrierGateway:
    """Gateway integrating with external carriers."""

    def create(self, input: Optional[Shipment]) -> Shipment:
        """Hand off a new Shipment to a carrier."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Shipment]:
        """Look up a Shipment at the carrier by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Shipment]:
        """List Shipments at the carrier up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Cancel a Shipment at the carrier by id."""
        raise NotImplementedError("not implemented")
